"""R-153：焦灼比賽分槽乘數（資料直接量，不擬合不挑參數）。用法：python -I -X utf8 reports/E208-team-rating/r153_close_multipliers.py
資料：2024-25（data/defense-seventh/2024-25）與 2025-26（data/season-source）的 leaguegamelog 例行賽 player-games／team-games。
每隊每季球員依該季（該隊）場均分鐘（總分鐘 ÷ 出場數，沒上場的不算出場）排名 → 槽 1…10，>10 併成槽 11（11+）。
焦灼場＝最終分差（team-games PLUS_MINUS）|d| ≤ 5 或延長賽（team MIN > 240）。延長賽分鐘等比換算成 48 分鐘：m × 240 / team MIN。
m_k ＝ 槽 k 在焦灼場的平均分鐘 ÷ 槽 k 在全部場的平均分鐘（都是「有出場」的球員場次；兩季合併）。"""
import collections
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEASONS = {'2024-25': ROOT / 'data/defense-seventh/2024-25', '2025-26': ROOT / 'data/season-source'}
CLOSE = 5
OUT = Path(__file__).resolve().parent / 'r153-close-game-multipliers.json'


def rows(path):
    d = json.loads(path.read_text(encoding='utf-8'))['data']['resultSets'][0]
    h = {k: i for i, k in enumerate(d['headers'])}
    return [{k: r[i] for k, i in h.items()} for r in d['rowSet']], hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    allm, closem, src = collections.defaultdict(list), collections.defaultdict(list), {}
    ngames = {}
    for season, d in SEASONS.items():
        tg, sha_t = rows(d / 'team-games.json'); pg, sha_p = rows(d / 'player-games.json')
        src[season] = {'dir': str(d.relative_to(ROOT)), 'team-games.sha256': sha_t, 'player-games.sha256': sha_p}
        info = {(r['GAME_ID'], r['TEAM_ID']): (r['MIN'], r['PLUS_MINUS']) for r in tg}
        by = collections.defaultdict(list)       # (team, player) → [(game, min scaled, close)]
        for r in pg:
            if not r['MIN'] or r['MIN'] <= 0:
                continue
            tmin, pm = info[(r['GAME_ID'], r['TEAM_ID'])]
            by[(r['TEAM_ID'], r['PLAYER_ID'])].append((r['MIN'] * 240.0 / tmin, abs(pm) <= CLOSE or tmin > 240))
        teams = collections.defaultdict(list)
        for (t, p), g in by.items():
            teams[t].append((sum(m for m, _ in g) / len(g), g))
        ncl = 0
        for t, lst in teams.items():
            lst.sort(key=lambda x: -x[0])
            for i, (_, g) in enumerate(lst):
                k = min(i + 1, 11)
                for m, c in g:
                    allm[k].append(m)
                    if c:
                        closem[k].append(m)
        ngames[season] = {'games': len({g for g, _ in info}), 'closeTeamGames': sum(1 for (g, t), (mn, pm) in info.items() if abs(pm) <= CLOSE or mn > 240) // 2}
    mult = {}
    for k in range(1, 12):
        a, c = sum(allm[k]) / len(allm[k]), sum(closem[k]) / len(closem[k])
        mult[str(k)] = {'label': str(k) if k < 11 else '11+', 'allMin': round(a, 4), 'closeMin': round(c, 4), 'm': round(c / a, 4), 'nAll': len(allm[k]), 'nClose': len(closem[k])}
    OUT.write_text(json.dumps({'rule': 'R-153', 'close': f'|margin| <= {CLOSE} or OT', 'sources': src, 'games': ngames, 'multipliers': mult}, ensure_ascii=False, indent=1), encoding='utf-8')
    print([mult[str(k)]['m'] for k in range(1, 12)], ngames)


if __name__ == '__main__':
    sys.exit(main())
