"""E-225 雜訊／MDE 草稿：只用訓練季（2021-22..2024-25）的 split=train，folds 1-4 擬合、fold 0 評估（不碰 test／前向季，L-026）。

基準：B0 聯盟平均（每季）；B1-id＝E-224 型單人 stints ridge（球員×季 進攻／防守欄，λ3000）；
B1＝B1-id＋場上五人能力值／OVR z 分數加總（進攻邊、防守邊各 16 欄，λ1）。B1×3＝λ 改 9000 的近鄰模型（只當配對雜訊的代理）。
主指標：stint 淨值誤差＝回合加權 MSE，淨值＝100·(ptsA−ptsB)/P，P＝(possA+possB)/2，預測＝100·(μA·possA−μB·possB)/P。
雜訊：依場次 bootstrap（2000 次）成對差的 90% 半寬。輸出 mde-noise.json。用法：python -I -X utf8 reports/E225-lineup-transformer/mde_noise.py
"""
import json, os, sys
from collections import defaultdict

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e225_common import FEATS, HERE, load_players, load_rows

SEASONS = ['2021-22', '2022-23', '2023-24', '2024-25']
B = 2000


def main():
    rows = load_rows(SEASONS)
    P = {s: load_players(s) for s in SEASONS}
    fit = [r for r in rows if r['fold'] != 0]; ev = [r for r in rows if r['fold'] == 0]
    mean = {s: sum(r['ptsa'] + r['ptsb'] for r in fit if r['season'] == s) / sum(r['possa'] + r['possb'] for r in fit if r['season'] == s) for s in SEASONS}
    ids = sorted({f"{r['season']}:{r[x + str(j)]}" for r in fit for x in 'ab' for j in range(5)}); ix = {v: k for k, v in enumerate(ids)}; n = len(ids); F = len(FEATS)

    def design(rs):   # 每段 stint 兩列（A 進攻、B 進攻）
        rr, cc, vv, y, w, meta = [], [], [], [], [], []
        k = 0
        for r in rs:
            for o, d in (('a', 'b'), ('b', 'a')):
                for j in range(5):
                    po, pd = f"{r['season']}:{r[o + str(j)]}", f"{r['season']}:{r[d + str(j)]}"
                    if po in ix: rr.append(k); cc.append(ix[po]); vv.append(1.0)
                    if pd in ix: rr.append(k); cc.append(n + ix[pd]); vv.append(1.0)
                for side, off in ((o, 0), (d, F)):
                    z = sum(P[r['season']].get(r[side + str(j)], [np.zeros(F)])[0] for j in range(5))
                    for q in range(F):
                        if z[q]: rr.append(k); cc.append(2 * n + off + q); vv.append(float(z[q]))
                poss = r['poss' + o]
                y.append(r['pts' + o] / poss - mean[r['season']] if poss > 0 else 0.0); w.append(poss); meta.append(r['season'])
                k += 1
        return sp.csr_matrix((vv, (rr, cc)), shape=(k, 2 * n + 2 * F)), np.array(y), np.array(w)

    Xf, yf, wf = design(fit); Xe, _, _ = design(ev)

    def ridge(lam, with_attr):
        pen = np.r_[np.full(2 * n, lam), np.full(2 * F, 1.0 if with_attr else 1e12)]
        A = (Xf.T @ sp.diags(wf) @ Xf + sp.diags(pen)).tocsc()
        return sl.spsolve(A, Xf.T @ (wf * yf))

    models = {'B0': np.zeros(Xe.shape[1]), 'B1-id': ridge(3000, False), 'B1': ridge(3000, True), 'B1x3': ridge(9000, True)}
    gid = [r['gid'] for r in ev]; games = sorted(set(gid))
    gmap = {g: k for k, g in enumerate(games)}; gi = np.array([gmap[g] for g in gid])
    possA = np.array([r['possa'] for r in ev]); possB = np.array([r['possb'] for r in ev]); Pw = (possA + possB) / 2
    actual = np.where(Pw > 0, 100 * (np.array([r['ptsa'] for r in ev]) - np.array([r['ptsb'] for r in ev])) / np.maximum(Pw, 1e-9), 0)
    m = np.array([mean[r['season']] for r in ev])
    res = {}
    for name, b in models.items():
        mu = Xe @ b; muA, muB = mu[0::2] + m, mu[1::2] + m
        pred = 100 * (muA * possA - muB * possB) / np.maximum(Pw, 1e-9)
        se = Pw * (actual - pred) ** 2
        res[name] = (np.bincount(gi, se, len(games)), np.bincount(gi, Pw, len(games)))
    rng = np.random.default_rng(20261103)
    draws = [np.bincount(rng.integers(0, len(games), len(games)), minlength=len(games)) for _ in range(B)]
    mse = lambda k, c=None: (res[k][0].sum() / res[k][1].sum()) if c is None else (c @ res[k][0]) / (c @ res[k][1])

    def paired(a, b):
        d = np.array([mse(a, c) - mse(b, c) for c in draws]); pt = mse(a) - mse(b)
        lo, hi = np.percentile(d, [5, 95])
        return {'point': round(pt, 3), 'ci90': [round(lo, 3), round(hi, 3)], 'halfWidth90': round((hi - lo) / 2, 3), 'sd': round(float(d.std()), 3)}

    out = {'seasons': SEASONS, 'fitRows': len(fit), 'evalStints': len(ev), 'evalGames': len(games), 'evalPoss': round(float(Pw.sum() * 2)),
           'mse': {k: round(mse(k), 2) for k in res},
           'paired': {'B1-id−B0': paired('B1-id', 'B0'), 'B1−B0': paired('B1', 'B0'), 'B1−B1-id': paired('B1', 'B1-id'), 'B1x3−B1': paired('B1x3', 'B1')},
           'note': 'MSE 單位：(每 100 回合淨值)²，回合加權；只用訓練季 split=train 的 fold 0 評估，test／前向季未讀。'}
    hw = out['paired']['B1−B1-id']['halfWidth90']   # 代理：在 ID 之外加非 ID 資訊、預測變動量級相近的成對比較
    out['mdeDraft'] = {'rule': 'MDE 草稿＝2×成對 90% 半寬（B1−B1-id，代理）；凍結時改用 A 對 B1 在同一驗證 fold、5 seed 平均預測的成對半寬×2，兩者取大', 'value': round(2 * hw, 3),
                       'relativeToB1Gain': round(2 * hw / -out['paired']['B1−B0']['point'], 3)}
    json.dump(out, open(os.path.join(HERE, 'mde-noise.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
