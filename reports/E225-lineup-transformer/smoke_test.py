"""E-225 管線 smoke test：極小 Transformer、CPU、幾個 epoch，只確認管線通、驗證損失會下降。
只用 2023-24 的 split=train（folds 1-4 訓練、fold 0 驗證）；不讀 test／前向季（e225_common 會擋）。不寫任何準度結論。
用法：python -I -X utf8 reports/E225-lineup-transformer/smoke_test.py
"""
import json, os, sys, time

import numpy as np
import torch
import torch.nn as nn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e225_common import FEATS, HERE, load_players, load_rows

SEASON = '2023-24'
torch.manual_seed(0); np.random.seed(0)


class LineupNet(nn.Module):
    """token＝球員 embedding＋Linear(能力值 z ⊕ 遮罩)＋位置＋隊別；前面加 2 個 CLS（A 進攻、B 進攻）。"""

    def __init__(self, n_players, d=32, layers=1, heads=2):
        super().__init__()
        F = len(FEATS)
        self.emb = nn.Embedding(n_players, d); nn.init.normal_(self.emb.weight, std=0.02)
        self.attr = nn.Linear(2 * F, d); self.pos = nn.Embedding(6, d); self.side = nn.Embedding(2, d); self.cls = nn.Parameter(torch.zeros(2, d))
        enc = nn.TransformerEncoderLayer(d, heads, 2 * d, dropout=0.1, batch_first=True, norm_first=True)
        self.enc = nn.TransformerEncoder(enc, layers)
        self.head = nn.Linear(d, 3)   # 每回合得分（偏離聯盟平均）、失誤 logit、進攻籃板 logit

    def forward(self, pid, attr, pos, side):
        x = self.emb(pid) + self.attr(attr) + self.pos(pos) + self.side(side)
        c = self.cls.unsqueeze(0).expand(x.shape[0], -1, -1) + self.side.weight.unsqueeze(0)
        h = self.enc(torch.cat([c, x], 1))
        return self.head(h[:, :2])   # [B, 2(A 進攻, B 進攻), 3]


def tensors(rows, P, vocab, mean):
    F = len(FEATS); N = len(rows)
    pid = np.zeros((N, 10), np.int64); attr = np.zeros((N, 10, 2 * F), np.float32); pos = np.full((N, 10), 5, np.int64)
    side = np.tile(np.r_[np.zeros(5), np.ones(5)].astype(np.int64), (N, 1))
    y = np.zeros((N, 2, 6), np.float32)   # pts, poss, tov, orb, rebOpp, valid
    for i, r in enumerate(rows):
        for t, (x, j) in enumerate((x, j) for x in 'ab' for j in range(5)):
            p = r[x + str(j)]; pid[i, t] = vocab.get(p, 0)
            if p in P:
                attr[i, t, :F], attr[i, t, F:], pos[i, t] = P[p][0], P[p][1], P[p][2]
        for k, x in enumerate('ab'):
            y[i, k] = [r['pts' + x], r['poss' + x], r['tov' + x], r['orb' + x], r['rebOpp' + x], float(r['poss' + x] > 0)]
    return [torch.from_numpy(a) for a in (pid, attr, pos, side, y)]


def loss_fn(out, y, mean):
    pts, poss, tov, orb, opp, ok = y.unbind(-1)
    rate = torch.where(poss > 0, pts / poss.clamp(min=1e-6), torch.zeros_like(pts)) - mean
    l_pts = (poss * (out[..., 0] - rate) ** 2).sum() / poss.sum()
    p_t = torch.sigmoid(out[..., 1]).clamp(1e-5, 1 - 1e-5); tv = tov.clamp(max=poss)
    l_tov = -(tv * p_t.log() + (poss - tv).clamp(min=0) * (1 - p_t).log()).sum() / poss.sum()
    p_o = torch.sigmoid(out[..., 2]).clamp(1e-5, 1 - 1e-5); ob = orb.clamp(max=opp)
    l_orb = -(ob * p_o.log() + (opp - ob).clamp(min=0) * (1 - p_o).log()).sum() / opp.sum().clamp(min=1)
    return l_pts + l_tov + l_orb, (l_pts.item(), l_tov.item(), l_orb.item())


def main():
    t0 = time.time()
    rows = load_rows([SEASON]); P = load_players(SEASON)
    tr = [r for r in rows if r['fold'] != 0]; va = [r for r in rows if r['fold'] == 0]
    from collections import Counter
    cnt = Counter(r[x + str(j)] for r in tr for x in 'ab' for j in range(5))
    vocab = {p: k + 1 for k, p in enumerate(sorted(p for p, c in cnt.items() if c >= 20))}   # 0＝少見球員共用
    mean = sum(r['ptsa'] + r['ptsb'] for r in tr) / sum(r['possa'] + r['possb'] for r in tr)
    Tt, Tv = tensors(tr, P, vocab, mean), tensors(va, P, vocab, mean)
    net = LineupNet(len(vocab) + 1); opt = torch.optim.AdamW(net.parameters(), lr=1e-3, weight_decay=1e-2)
    nparam = sum(p.numel() for p in net.parameters())

    def evaluate():
        net.eval()
        with torch.no_grad():
            return loss_fn(net(*Tv[:4]), Tv[4], mean)[1]

    hist = [{'epoch': 0, 'val': evaluate()}]
    for ep in range(1, 6):
        net.train(); perm = torch.randperm(len(tr))
        for b in range(0, len(tr), 512):
            ix = perm[b:b + 512]
            loss, _ = loss_fn(net(*(t[ix] for t in Tt[:4])), Tt[4][ix], mean)
            opt.zero_grad(); loss.backward(); opt.step()
        hist.append({'epoch': ep, 'val': evaluate()})
        print(ep, [round(v, 4) for v in hist[-1]['val']], flush=True)
    v0, v1 = sum(hist[0]['val']), sum(hist[-1]['val'])
    out = {'season': SEASON, 'trainStints': len(tr), 'valStints': len(va), 'vocab': len(vocab), 'params': nparam,
           'valLoss(pts,tov,orb)': hist, 'valTotalStart': round(v0, 4), 'valTotalEnd': round(v1, 4), 'decreased': v1 < v0,
           'seconds': round(time.time() - t0, 1), 'note': '只確認管線；不是準度結論。test／前向季未讀。'}
    json.dump(out, open(os.path.join(HERE, 'smoke-test.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('pipeline ok; val loss', round(v0, 4), '->', round(v1, 4), 'params', nparam)


if __name__ == '__main__':
    main()
