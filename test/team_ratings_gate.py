"""球隊評分（E-208 第二階段）：分鐘規則、傷兵移除、姓名對應、預測勝場、頁面表頭。npm test 會跑；不跑模擬（輕量）。
若本機有 data/season-source-2026-27/team-ratings.json，另外檢查成品：每隊兩版輪替 240 分鐘、單人 ≤48、Out／Doubtful 不在今日輪替。"""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import team_ratings_daily as T  # noqa: E402
import site_header  # noqa: E402
import build_teams_page  # noqa: E402

# 一隊最近 3 場：1 號 40 分的球星、其餘輪替
PRIOR = [[[1, 40], [2, 34], [3, 30], [4, 28], [5, 24], [6, 22], [7, 20], [8, 16], [9, 14], [10, 12]],
         [[1, 38], [2, 33], [3, 31], [4, 27], [5, 25], [6, 21], [7, 19], [8, 17], [9, 15], [11, 14]],
         [[2, 35], [3, 32], [4, 29], [5, 26], [6, 23], [7, 21], [8, 18], [9, 16], [10, 13], [11, 12]]]
FALLBACK = [[i, 20.0] for i in range(1, 15)]


class Rotation(unittest.TestCase):
    def check(self, rot, out=()):
        self.assertLessEqual(len(rot), 10)
        self.assertAlmostEqual(sum(m for _, m in rot), 240.0, places=4)
        self.assertLessEqual(max(m for _, m in rot), 48.0 + 1e-9)
        self.assertFalse({p for p, _ in rot} & set(out))

    def test_recent_sums_240_cap_48(self):
        self.check(T.rotation(PRIOR, FALLBACK))

    def test_out_removed_and_redistributed(self):
        rot = T.rotation(PRIOR, FALLBACK, excluded={1, 2})
        self.check(rot, out={1, 2})
        self.assertEqual(len(rot), 9)                        # 近況名單只剩 9 人，不為了湊 10 人亂補
        base = dict(T.rotation(PRIOR, FALLBACK))
        self.assertGreater(dict(rot)[3], base[3])             # 剩下的人分到更多分鐘

    def test_cap_binds_with_few_players(self):
        rot = T.rotation(PRIOR, FALLBACK + [[i, 10.0] for i in range(15, 21)], excluded=set(range(1, 9)))   # 近況只剩 3 人 → 由季前名單補到 8 人以上
        self.check(rot, out=set(range(1, 9)))
        self.assertGreaterEqual(len(rot), 8)
        thin = T.norm([[1, 30], [2, 30], [3, 30], [4, 30], [5, 30]])
        self.check(thin)                                      # 5 人×48＝240，上限剛好

    def test_no_prior_uses_fallback(self):
        self.check(T.rotation([], FALLBACK, excluded={1}), out={1})

    def test_out_statuses(self):
        for s in ('Out', 'out', 'Doubtful', 'Suspension'):
            self.assertTrue(T.is_out(s), s)
        for s in ('Day-To-Day', 'Questionable', 'Probable', ''):
            self.assertFalse(T.is_out(s), s)


class Injuries(unittest.TestCase):
    def test_parse_espn(self):
        raw = {'injuries': [{'displayName': 'Golden State Warriors', 'injuries': [
            {'status': 'Day-To-Day', 'date': '2026-11-01T23:00Z', 'shortComment': 'X (back) is listed as doubtful for Monday.',
             'athlete': {'displayName': 'Player X', 'team': {'abbreviation': 'GS'}}, 'details': {'returnDate': '2026-11-02'}},
            {'status': 'Day-To-Day', 'shortComment': 'Y is questionable for Monday.', 'athlete': {'displayName': 'Player Y', 'team': {'abbreviation': 'GS'}}},
            {'status': 'Out', 'shortComment': 'Z out.', 'athlete': {'displayName': 'Player Z', 'team': {'abbreviation': 'GS'}}}]}]}
        it = T.parse_espn(raw)
        self.assertEqual([i['status'] for i in it], ['Doubtful', 'Day-To-Day', 'Out'])
        self.assertEqual(it[0]['team'], 'GSW')
        self.assertTrue(T.is_out(it[0]['status']) and not T.is_out(it[1]['status']))

    def test_name_matching(self):
        idx = {T.nn('Nikola Jokić'): [(203999, 'DEN')], T.nn('Tim Hardaway Jr.'): [(1, 'DAL')],
               T.nn('Jaylin Williams'): [(10, 'OKC'), (11, 'IND')]}
        items = [{'name': 'Nikola Jokic', 'team': 'DEN'}, {'name': 'Tim Hardaway', 'team': 'DAL'}, {'name': 'Jaylin Williams', 'team': 'IND'},
                 {'name': 'Jaylin Williams', 'team': 'BOS'}, {'name': 'Nobody Here', 'team': 'MEM'}]
        m, un = T.attach_ids(items, idx)
        self.assertEqual([x['playerId'] for x in m], [203999, 1, 11, None, None])     # 同名多人對不到隊就不猜
        self.assertEqual(un, ['Jaylin Williams', 'Nobody Here'])


class Predict(unittest.TestCase):
    def test_predict_wins(self):
        margin = {str(i): 0.0 for i in range(30)}
        w, ng, nr = T.predict_wins(3, 6, [(0, 1), (2, 0)], margin, '0')
        self.assertEqual((ng, nr), (2, 82 - 6 - 2))
        self.assertAlmostEqual(w, 3 + 0.5 * (82 - 6), places=6)          # 兩場主客各一，Φ(+H)+1−Φ(+H) ＝ 1，平均勝率補的場數各 0.5
        margin['0'] = 10.0
        self.assertGreater(T.predict_wins(0, 0, [], margin, '0')[0], 41)


class Header(unittest.TestCase):
    def test_header_has_team_link(self):
        for cur in ('inseason', 'card'):
            self.assertIn('href="teams.html"', site_header.header_html(cur))
        css, hdr, js = site_header.teams_masthead()
        self.assertIn('href="teams.html"', hdr)
        self.assertIn('球隊評分', hdr)

    def test_page_builds(self):
        doc = {'season': '2026-27', 'teams': {}, 'injuries': {}, 'schedule': {}, 'version': 'inseason x', 'dataCutoff': 'd', 'generatedAt': 'g',
               'engine': 'e', 'seeds': 1, 'H': 2.5, 'sigma': 12, 'lastN': 10}
        html = build_teams_page.build(doc)
        self.assertIn('id="data"', html)
        self.assertIn('回測僅與上季淨效率打平', html)


class Product(unittest.TestCase):
    def test_product_invariants(self):
        p = T.RATINGS
        if not p.exists():
            self.skipTest('沒有 team-ratings.json')
        d = json.loads(p.read_text(encoding='utf-8'))
        self.assertEqual(len(d['teams']), 30)
        for t in d['teams'].values():
            outs = {x['playerId'] for x in t['injured'] if x['playerId'] and T.is_out(x['status'])}
            for v in ('c', 'today'):
                rot = t[v]['rotation']
                self.assertAlmostEqual(sum(r['min'] for r in rot), 240.0, places=3, msg=t['name'])
                self.assertLessEqual(max(r['min'] for r in rot), 48.0 + 1e-6)
            self.assertFalse({r['pid'] for r in t['today']['rotation']} & outs, t['name'])


if __name__ == '__main__':
    unittest.main()
