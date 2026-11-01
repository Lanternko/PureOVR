"""2025-26 正式卡名單頁（card 0.2.10）：以正式卡名單頁為版型，換成 card 0.2.10 的 OVR／能力值（OVR 為每場、含上場時間、相對替補水準，R-028；能力值同 0.1.2），3PT 顯示 threeValue（R-024）。
OVR 能力估計納入教練用人證據（分鐘、出賽率、年齡、練兵隊），DNP 與輪休分開（E-075）；用人回歸的訓練目標是 2025-26 單季 RAPM（E-084）；分鐘權重為飽和曲線 W(m)（E-089）；補籃改歸近距離、能力值錨點對四季合併池、頂端只壓縮（E-101）；OVR 迴歸不用 physique（E-131），網站不顯示 PHYS。
PRES 顯示 presDisplay（逼失誤 − 0.25·犯規，E-071），提示卡列逼失誤（卡片 pressure）與五個分量（抄截、干擾球、對位逼失誤、造進攻犯規、犯規，E-071 收縮後值＋PR＋前十名次）；
TO 提示卡列失誤、球權、失誤率（player-games.json 整季加總）；PER D 提示卡列 E-060 三分量（三分干擾、對位負擔、威懾力）。

輸入：reports/card-0.2.10/ranking.csv（card 0.2.10）、
      reports/card-0.2.10/three-value.csv（以姓名對 tv_main；E-123 頂端開尾）、data/season-source/player-games.json。
版型：reports/ovr-v58-card-2025-26/roster-viewer.html（只讀；team／ht／gp 依姓名取自它）。
輸出：reports/card-0.1.2-2025-26/roster-viewer.html（或 argv[1] 指定路徑）

用法：python -I scripts/build_card_viewer.py [輸出路徑]
"""
import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import enrich_roster_viewer as er  # noqa: E402
from season_nav import add_season_nav, apply_common, regroup_attrs  # noqa: E402
import season_nav as sn  # noqa: E402

ROOT = er.ROOT
BASE = ROOT / 'reports/ovr-v58-card-2025-26/roster-viewer.html'
CARD = ROOT / 'reports/card-0.2.10/ranking.csv'
THREE_VALUE = ROOT / 'reports/card-0.2.10/three-value.csv'
FORCE = ROOT / 'reports/card-0.2.0+E071-pressure/force-2025-26.csv'
DEFAULT_OUT = ROOT / 'reports/card-0.1.2-2025-26/roster-viewer.html'
# PRES 提示卡的分量（E-071 force 的收縮後值）；PR／名次對上場 ≥ 1000 分鐘的人群
PRES_SUB = [('stl_shr', '抄截', '/36', '{:.2f}'), ('defl_shr', '干擾球', '/36', '{:.2f}'),
            ('mtov_shr', '對位逼失誤', '/100 回合', '{:+.2f}'), ('chg_shr', '造進攻犯規', '/36', '{:.2f}'),
            ('pf_shr', '犯規', '/36', '{:.2f}')]
PRES_LOW_GOOD = {'pf_shr'}   # PR 反轉：越少犯規 PR 越高
POOL_MIN = 1000


def pres_tips():
    """({name: 細項列}, pool 人數)：逼失誤四分量＋犯規，各附 PR 與前十名次；犯規數值旁標（多）／（普通）／（少）。"""
    rows = list(csv.DictReader(FORCE.open(encoding='utf-8')))
    pool = [r for r in rows if float(r['MIN']) >= POOL_MIN]
    tips = {}
    for r in rows:
        lines, inpool = [], float(r['MIN']) >= POOL_MIN
        for k, label, unit, fmt in PRES_SUB:
            x = float(r[k])
            pr, rk = sn.pr_rank(x, [float(q[k]) for q in pool], low_good=k in PRES_LOW_GOOD)
            v = fmt.format(x)
            if k in PRES_LOW_GOOD:
                v += '（多）' if pr <= 33 else '（少）' if pr >= 67 else '（普通）'
            lines.append((label, v + unit, pr, rk if inpool else None))
        tips[r['name']] = lines
    return tips, len(pool)


def pres_tip(pres, force, sub, n_pool, note=''):
    return sn.cell_tip('壓迫', 'PRES', round(pres), sub, d=f'逼失誤 {round(force)} − 0.25×犯規{note}',
                       foot=['各項為收縮後估計；對位逼失誤是超出預期的部分'])


def tov_tip(v, sub, n_pool, season='2025-26', pool_min=POOL_MIN):
    return sn.cell_tip('少失誤', 'TO', round(v), sub, d=f'{season} 失誤 ÷ 球權次數，失誤率越低越高',
                       foot=['球權＝投籃＋0.44×罰球＋助攻＋失誤'])


ONBALL = ROOT / 'reports/card-0.1.1+E060-onball-targeting/components-2025-26.csv'


def onball_rows(comps, pool):
    """E-060 三個收縮後分量 → PER D 細項列 {key: rows}。comps：{key: (C3, B, T)}；pool：算 PR／名次的人（key 集合）。
    威懾力列 T（對手在他面前比平常多出手幾次／100 回合），越少 PR 越高。"""
    P = [comps[k] for k in pool if k in comps]
    out = {}
    for k, (c3, b, t) in comps.items():
        inpool = k in pool
        q = [sn.pr_rank(x, [p[i] for p in P], low_good=i == 2) for i, x in enumerate((c3, b, t))]
        out[k] = [('三分干擾', f'{c3:.2f}/36', q[0][0], q[0][1] if inpool else None),
                  ('對位負擔', f'對手USG {b:.1f}%', q[1][0], q[1][1] if inpool else None),
                  ('威懾力', f'減少出手 {-t:.1f}', q[2][0], q[2][1] if inpool else None)]
    return out


def onball_tip(v, sub, note=''):
    return sn.cell_tip('單防', 'PER D', round(v), sub, d=f'三分干擾＋對位負擔＋威懾力，各一份{note}',
                       foot=['USG＝球權使用率：在場時全隊回合由他出手、罰球或失誤結束的比例'])


def main(out=None):
    out = Path(out) if out else DEFAULT_OUT
    rows = list(csv.DictReader(CARD.open(encoding='utf-8')))
    tv = {r['name']: float(r['tv_main']) for r in csv.DictReader(THREE_VALUE.open(encoding='utf-8'))}
    base = BASE.read_text(encoding='utf-8')
    old = json.loads(re.search(r'const DATA=(\{.*?\});\nconst COLS', base, re.S).group(1))
    oc = old['cols']
    by_old = {r[oc.index('name')]: r for r in old['rows']}
    # 不在樣板的人：球隊與場數取自 2025-26 player-games.json（球隊＝最後一場）
    rs = json.loads(er.SRC.read_text(encoding='utf-8'))['data']['resultSets'][0]
    h = {k: i for i, k in enumerate(rs['headers'])}
    last_team, gp_src = {}, {}
    for row in sorted(rs['rowSet'], key=lambda r: r[h['GAME_DATE']]):
        last_team[row[h['PLAYER_NAME']]] = row[h['TEAM_ABBREVIATION']]
        gp_src[row[h['PLAYER_NAME']]] = gp_src.get(row[h['PLAYER_NAME']], 0) + 1
    cols = ['rank', 'ovr', 'name', 'pos', 'team', 'ht', 'min', 'gp', 'imp', 'dbon', 'threeValue', 'mid', 'short', 'ft',
            'drive', 'foulDraw', 'pass', 'tovSkill', 'creation', 'rebound', 'physique', 'stamina', 'onBall', 'help', 'pressure', 'force', 'foulDisc',
            'tips', 'off', 'def']
    od, od_bad = sn.off_def(rows, 'name')
    assert od_bad == 0, f'進攻／防守分：{od_bad} 人 pred0 算不回來'
    ptips, n_pres = pres_tips()
    trows, n_tov = sn.tov_rows(er.SRC, 'PLAYER_NAME', POOL_MIN)
    oc_ = list(csv.DictReader(ONBALL.open(encoding='utf-8')))
    orows = onball_rows({r['name']: (float(r['C3']), float(r['B']), float(r['T'])) for r in oc_ if '' not in (r['C3'], r['B'], r['T'])},
                        {r['name'] for r in oc_ if float(r['min']) >= POOL_MIN})
    # DIQ 顯示負分：card 0.2.10 的 defenseBonus（同 0.2.7b） 用 def-L-primary，posMeanD 從同一批人算（max(0, ·) 逐人核對）
    dcen = sn.defense_centered(rows, 'name', [(ROOT / 'reports/card-0.2.5+E104-defense-pergame-decay/def-L-primary.csv', None)])
    assert dcen, 'DIQ 負分：def-L-primary 算回來的 defenseBonus 對不上 card 0.2.10'
    data_rows, missing, no_tv = [], [], []
    for r in rows:
        num = lambda k: float(r[k])
        o = by_old.get(r['name'])
        if o:
            team, ht, gp = o[oc.index('team')], o[oc.index('ht')], o[oc.index('gp')]
        else:
            missing.append(r['name'])
            team, ht, gp = last_team.get(r['name'], ''), 0, gp_src.get(r['name'], 0)
        if r['name'] in tv:
            three = round(tv[r['name']], 1)
        else:
            no_tv.append(r['name'])
            three = num('long')
        data_rows.append([int(r['rank']), num('ovr'), r['name'], r['pos'], team, ht, round(num('MIN') / gp, 1) if gp else 0.0, gp,
                          num('predictedPer36'), dcen[r['name']], three, *[num(a) for a in cols[11:24]],
                          num('presDisplay'), num('pressure'), num('foulDisc'),
                          {**({'pressure': pres_tip(num('presDisplay'), num('pressure'), ptips[r['name']], n_pres)} if r['name'] in ptips else {}),
                           **({'tovSkill': tov_tip(num('tovSkill'), trows[r['name']], n_tov)} if r['name'] in trows else {}),
                           **({'onBall': onball_tip(num('onBall'), orows[r['name']])} if r['name'] in orows else {})},
                          *od[r['name']]])
    s = base
    s = s.replace('<title>OVR 名單檢視</title>', '<title>2025-26 OVR 名單</title>', 1)
    s = re.sub(r'<div class="src">.*?</div>',
               f'<div class="src">OVR：正式卡 card 0.2.10（2025-26 整季；OVR 為每場，含上場時間，相對替補水準；FD 以量為主；PRES＝逼失誤扣犯規；OVR 能力估計納入教練用人證據，DNP 與輪休分開，用人回歸對齊當季 RAPM；分鐘權重遞減；能力值對 2022-23～2025-26 四季比較；防守加成不打折、近期加權；OVR 評分標準為 DARKO 加 BPM；年輕人沒有爛隊折扣；傳球看量也看率；3PT、RIM、PRES 頂端不封在 99；OVR 不看身高體重）；3PT 顯示 threeValue；{len(rows)} 人</div>',
               s, count=1, flags=re.S)
    new_data = json.dumps({'cols': cols, 'rows': data_rows}, ensure_ascii=False, separators=(',', ':'))
    s = re.sub(r'const DATA=\{.*?\};\nconst COLS', lambda m: f'const DATA={new_data};\nconst COLS', s, count=1, flags=re.S)
    for a, b in [
        ("['long', '3PT', '三分']", "['threeValue', '3PT', '三分']"),
        ("['drive', 'DRV', '切入']", "['drive', 'DRV', '切入'], ['foulDraw', 'FD', '製造犯規']"),
        ('colspan="22"', 'colspan="23"'),
        # PRES 改為壓迫（E-071）：顯示 presDisplay，tooltip 列逼失誤與犯規紀律
        ("['pressure', 'PRES', '壓命中率']", "['pressure', 'PRES', '壓迫']"),
        # 分鐘改顯示場均（使用者 2026-10-29），篩選門檻改成場均分鐘
        ("th('min', 'MIN', '分鐘', 'gl')", "th('min', 'MPG', '分鐘', 'gl')"),
        ("[[0, '全部'], [500, '≥500'], [1000, '≥1000'], [1500, '≥1500']]",
         "[[0, '全部'], [10, '≥10'], [20, '≥20'], [30, '≥30']]"),
        ('<td class="sub gl${sc(\'min\')}">${p.min.toLocaleString()}</td>',
         '<td class="sub gl${sc(\'min\')}">${p.min.toFixed(1)}</td>'),
        ('<span>上場 <b>${p.min.toLocaleString()}</b> 分鐘</span>', '<span>場均 <b>${p.min.toFixed(1)}</b> 分鐘</span>'),
    ]:
        assert s.count(a) >= 1, a
        s = s.replace(a, b)
    s = regroup_attrs(sn.apply_cell_tips(apply_common(s)))   # PRES／TO 格子帶浮動提示卡（兩種顯示模式都有）
    s = add_season_nav(s, 'card')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(s, encoding='utf-8')
    er.inject(out, er.aggregate(), view='season')
    print('wrote', out, len(rows), 'players; missing from template:', len(missing), missing[:10],
          '; no threeValue:', len(no_tv), no_tv[:10])
    return out


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else None)
