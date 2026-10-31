"""E-153 建卡驅動：沿用 E-142 build_card_t（唯讀匯入），pipe 階段可選連續 d（E-147 同公式）。
用法（repo root）：python -I -B -X utf8 <本檔> <模式> <原點> <工作目錄> <cont:0|1> [候選pkl|none]
  模式 build：原點 2025-26 走 c0 路徑，其餘走 hist 路徑。cont=1 時 pipe 的 d 改連續。
"""
import csv, json, os, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
E142 = ROOT / 'reports/E142-card-target'


def team_badness(M, tg_path):
    tg = M.jload(tg_path)['data']['resultSets'][0]
    h = tg['headers']
    it, iw, ipm = h.index('TEAM_ID'), h.index('WL'), h.index('PLUS_MINUS')
    acc = {}
    for r in tg['rowSet']:
        a = acc.setdefault(r[it], [0, 0, 0.0])
        a[0] += 1; a[1] += r[iw] == 'W'; a[2] += float(r[ipm])
    out = {}
    for t, (gp, w, pm) in acc.items():
        nr, wp = pm / (gp + 10), (w + 5) / (gp + 10)
        s = 0.7 * (0.5 + 0.033 * nr) + 0.3 * wp
        out[t] = {'d': min(1.0, max(0.0, (0.40 - s) / 0.10)), 'gp': gp}
    return out


def main():
    mode = sys.argv[1]
    if mode == 'pipe':
        tag = sys.argv[2]
        spec = json.loads((BC.W / f'{tag}-pipe.json').read_text(encoding='utf-8'))
        out = Path(spec['out'])
        import importlib.util
        s = importlib.util.spec_from_file_location('e094t', BC.S1 / 'e094_t.py')
        M = importlib.util.module_from_spec(s); s.loader.exec_module(M)
        M.HERE, M.W, M.CARDS = out, out / 'work', out / 'cards'
        M.load_data()
        M.set_card_dir(spec['poolCards'] if spec.get('poolCards') else spec['cards'])
        pools = M.build_pools()
        M.set_card_dir(spec['cards'])
        if spec.get('cont'):
            tgp = M._P('teamGames', 'data/season-source/team-games.json')
            tgp = tgp if Path(str(tgp)).is_absolute() else ROOT / tgp
            tb = team_badness(M, tgp)
            ORIG = M.scope_feats
            import numpy as np
            def sf3(*a):
                r = ORIG(*a)
                r['d'] = np.array([tb[t]['d'] if t is not None else 0.0 for t in r['main']])
                return r
            M.scope_feats = sf3
        pdnew = {r['name']: r['presDisplay_new'] for r in csv.DictReader(open(ROOT / BC.RT.E123 / 'work/presDisplay-new.csv', encoding='utf-8'))}
        r_ = M.pipeline(M.BASE_OPTS, pools, 'season')
        rows = [dict(r) for r in r_['_aux']['rows23']]
        for r in rows:
            if r['name'] in pdnew:
                r['presDisplay'] = BC.RT.fmt1(pdnew[r['name']])
        M.write_rank(out / 'ranking.csv', r_['_aux']['cols23'], rows)
        print(json.dumps({'sha256': BC.RT.sha(out / 'ranking.csv'), 'rows': len(rows)}))
        return 0
    origin, cont, pk = sys.argv[2], sys.argv[4] == '1', (sys.argv[5] if len(sys.argv) > 5 else 'none')
    cand = None
    if pk != 'none':
        import pickle
        cand = pickle.load(open(pk, 'rb'))

    def run_pipe(tag, out, cards, cfg, pool_cards=None):
        out = Path(out); out.mkdir(parents=True, exist_ok=True)
        BC.RT.jw(BC.W / f'{tag}-pipe.json', {'out': str(out), 'cards': str(cards), 'poolCards': str(pool_cards) if pool_cards else None, 'cont': cont})
        cfgp = BC.W / f'{tag}-e094cfg.json'
        BC.RT.jw(cfgp, cfg)
        rc, sec, err = BC.RT.sub_run([sys.executable, '-I', '-B', '-X', 'utf8', str(Path(__file__).resolve()), 'pipe', tag], {'E134_CFG': str(cfgp), 'E142_WORK': str(BC.W)}, out / 'pipe.log')
        if rc:
            raise SystemExit(f'{tag} pipe failed: {err}')
        return BC.RT.sha(out / 'ranking.csv'), sec
    BC.run_pipe = run_pipe
    return BC.c0(cand, 'c0') if origin == '2025-26' else BC.hist(origin, cand)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    work = sys.argv[3] if sys.argv[1] != 'pipe' else os.environ['E142_WORK']
    os.environ['E142_WORK'] = work
    sys.path.insert(0, str(E142))
    import build_card_t as BC
    sys.exit(main())
