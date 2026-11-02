"""球隊評分（E-208 第二階段）：分鐘規則、傷兵移除、姓名對應、預測勝場、頁面表頭。npm test 會跑；不跑模擬（輕量）。
若本機有 data/season-source-2026-27/team-ratings.json，另外檢查成品：每隊兩版輪替 240 分鐘、單人 ≤48、Out／Doubtful 不在今日輪替。"""
import datetime as dt
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
PDF_TXT = (ROOT / 'test/fixtures/injury-report-2026-11-02_04_15AM.txt').read_text(encoding='utf-8')   # 真實報告的 pdftotext -raw 輸出（6 頁）


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


class OfficialPdf(unittest.TestCase):
    def test_name_conversion(self):
        f = T.pdf_name_to_first_last
        self.assertEqual(f('Holmgren, Chet'), 'Chet Holmgren')
        self.assertEqual(f('Udeh, Jr., Ernest'), 'Ernest Udeh Jr.')
        self.assertEqual(f('Murphy III, Trey'), 'Trey Murphy III')
        self.assertEqual(f('de Larrea, Sergio'), 'Sergio de Larrea')

    def test_parse_fixture(self):
        d = T.parse_injury_text(PDF_TXT)
        by = {i['name']: i for i in d['items']}
        self.assertEqual(len(d['items']), 83)
        self.assertEqual(d['reportTime'], '11/02/26 04:15 AM')
        self.assertEqual(set(d['notSubmitted']), {'IND', 'BKN', 'ORL', 'BOS', 'LAL', 'GSW', 'TOR', 'LAC'})   # NOT YET SUBMITTED 的隊不產生球員
        self.assertFalse({i['team'] for i in d['items']} & set(d['notSubmitted']))
        self.assertEqual((by['Alex Caruso']['team'], by['Alex Caruso']['status']), ('OKC', 'Out'))
        self.assertEqual((by['Ernest Udeh Jr.']['team'], by['Ernest Udeh Jr.']['status']), ('CLE', 'Out'))      # 後綴＋同隊沿用
        self.assertEqual((by['Nic Claxton']['team'], by['Nic Claxton']['status']), ('CHI', 'Doubtful'))
        self.assertEqual((by['Tim Hardaway Jr.']['team'], by['Tim Hardaway Jr.']['status']), ('MIA', 'Questionable'))
        self.assertEqual((by['Trey Murphy III']['team'], by['Trey Murphy III']['status']), ('NOP', 'Probable'))
        self.assertEqual(by['Caleb Martin']['status'], 'Available')
        # 跨頁沿用隊名：第 2 頁開頭的 Veesaar、Wilson 屬於第 1 頁最後的 ATL；第 3 頁開頭的 Grant Williams 屬於第 2 頁最後的 CHA
        self.assertEqual((by['Henri Veesaar']['team'], by['Jalen Wilson']['team']), ('ATL', 'ATL'))
        self.assertEqual(by['Grant Williams']['team'], 'CHA')
        self.assertEqual(by['Quinten Post']['team'], 'MEM')
        self.assertEqual(by['Chet Holmgren']['comment'], 'Injury/Illness - Right Knee/ Injury Recovery')       # 折行的原因接回去
        self.assertEqual(by['Jalen Williams']['team'], 'OKC')                                                 # 三個 Williams 各歸各隊
        self.assertEqual(by['Mark Williams']['team'], 'PHX')
        self.assertTrue(T.is_out('Doubtful') and not T.is_out(by['Caleb Martin']['status']) and not T.is_out('Probable'))

    def test_eastern_time_and_urls(self):
        utc = dt.timezone.utc
        et = T.et_from_utc(dt.datetime(2026, 11, 2, 9, 19, tzinfo=utc))
        self.assertEqual((et.hour, et.minute, et.utcoffset()), (4, 19, dt.timedelta(hours=-5)))
        for args, hrs in (((2026, 7, 1, 12, 0), -4), ((2026, 11, 1, 5, 59), -4), ((2026, 11, 1, 6, 0), -5),
                          ((2026, 3, 8, 6, 59), -5), ((2026, 3, 8, 7, 0), -4)):                              # 夏令時間兩個交界
            self.assertEqual(T.et_from_utc(dt.datetime(*args, tzinfo=utc)).utcoffset(), dt.timedelta(hours=hrs), args)
        urls = T.pdf_urls(et)
        self.assertTrue(urls[0][0].endswith('/Injury-Report_2026-11-02_04_15AM.pdf'))
        self.assertTrue(urls[1][0].endswith('_04_00AM.pdf'))
        self.assertTrue(urls[5][0].endswith('Injury-Report_2026-11-02_03_00AM.pdf'))
        self.assertTrue(urls[-1][0].endswith('Injury-Report_2026-10-31_04_15PM.pdf'))                       # 36 小時前、PM 格式
        self.assertEqual(len(urls), 36 * 4 + 1)

    def test_fetch_latest_walks_back_and_gives_up(self):
        et = dt.datetime(2026, 11, 2, 4, 19, tzinfo=dt.timezone(dt.timedelta(hours=-5)))
        calls = []
        def fetch(url):
            calls.append(url)
            return b'%PDF-1.4 x' if len(calls) == 3 else None                                              # 前兩個時段 404
        url, slot, data = T.fetch_latest_pdf(et, fetch)
        self.assertTrue(url.endswith('_03_45AM.pdf') and data.startswith(b'%PDF'))
        def boom(url):
            calls.append(url)
            raise OSError('network down')
        calls.clear()
        with self.assertRaises(RuntimeError):
            T.fetch_latest_pdf(et, boom)
        self.assertEqual(len(calls), 3)                                                                     # 連線掛掉不會把 144 個時段都試完
        with self.assertRaises(RuntimeError):
            T.fetch_latest_pdf(et, lambda u: None)

    def run_load(self, espn, pdf_ok=True, source='auto', prev=None):
        idx = {T.nn('Alex Caruso'): [(1, 'OKC')]}
        with tempfile.TemporaryDirectory() as td:
            inj = Path(td) / 'injuries.json'
            if prev:
                inj.write_text(json.dumps(prev), encoding='utf-8')
            pdf_calls = []
            def fake_pdf(now_et):
                pdf_calls.append(1)
                if not pdf_ok:
                    raise RuntimeError('no pdf')
                return 'https://x/Injury-Report_2026-11-02_04_15AM.pdf', now_et, b'%PDF'
            with mock.patch.object(T, 'INJURIES', inj), mock.patch.object(T, 'fetch_json', espn), \
                    mock.patch.object(T, 'fetch_latest_pdf', fake_pdf), mock.patch.object(T, 'pdf_to_text', lambda b: PDF_TXT):
                doc = T.load_injuries(idx, True, source)
            return doc, len(pdf_calls), json.loads(inj.read_text(encoding='utf-8')) if inj.exists() else None

    def test_espn_ok_skips_pdf(self):
        raw = {'timestamp': 't', 'injuries': [{'displayName': 'Oklahoma City Thunder', 'injuries': [
            {'status': 'Out', 'athlete': {'displayName': 'Alex Caruso', 'team': {'abbreviation': 'OKC'}}}]}]}
        doc, n_pdf, _ = self.run_load(lambda url: raw)
        self.assertEqual((doc['source'], n_pdf), ('espn', 0))

    def test_espn_failure_falls_back_to_pdf(self):
        def bad(url):
            raise OSError('espn down')
        doc, n_pdf, saved = self.run_load(bad)
        self.assertEqual((doc['source'], doc['stale'], n_pdf), ('nba-official-pdf', False, 1))
        self.assertEqual(len(doc['items']), 83)
        self.assertTrue(doc['pdfUrl'].endswith('04_15AM.pdf') and doc['reportTime'])
        self.assertEqual(saved['source'], 'nba-official-pdf')
        self.assertEqual([i['playerId'] for i in doc['items'] if i['name'] == 'Alex Caruso'], [1])          # 走同一個 attach_ids
        self.assertEqual(len(doc['unmatched']), 82)
        doc2, n2, _ = self.run_load(lambda url: {'injuries': []})                                           # 空的 ESPN 回應也算失敗
        self.assertEqual((doc2['source'], n2), ('nba-official-pdf', 1))

    def test_forced_pdf_skips_espn(self):
        def must_not_call(url):
            raise AssertionError('不該碰 ESPN')
        doc, n_pdf, _ = self.run_load(must_not_call, source='pdf')
        self.assertEqual((doc['source'], n_pdf), ('nba-official-pdf', 1))

    def test_both_fail_reuses_previous(self):
        def bad(url):
            raise OSError('down')
        prev = {'fetchedAt': 'old', 'source': 'espn', 'stale': False, 'items': [{'name': 'A'}], 'unmatched': []}
        doc, n_pdf, _ = self.run_load(bad, pdf_ok=False, prev=prev)
        self.assertEqual((doc['source'], doc['stale'], doc['fetchedAt'], n_pdf), ('espn', True, 'old', 1))


class Predict(unittest.TestCase):
    def test_predict_wins(self):
        margin = {str(i): 0.0 for i in range(30)}
        w, ng, nr = T.predict_wins(3, 6, [(0, 1), (2, 0)], margin, '0')
        self.assertEqual((ng, nr), (2, 82 - 6 - 2))
        self.assertAlmostEqual(w, 3 + 0.5 * (82 - 6), places=6)          # 兩場主客各一，Φ(+H)+1−Φ(+H) ＝ 1，平均勝率補的場數各 0.5
        margin['0'] = 10.0
        self.assertGreater(T.predict_wins(0, 0, [], margin, '0')[0], 41)


class MinutesReturn(unittest.TestCase):
    """spec-minutes-return：分鐘只平均有出場的比賽、15 分鐘門檻補回傷癒者、回歸日逐場切換陣容。"""

    def test_only_games_played_count(self):
        self.assertEqual(T.own_avg([0, 30, 0, 20, 0]), 25.0)             # 0 分鐘的場次不算進分母
        self.assertIsNone(T.own_avg([0, 0]))
        self.assertAlmostEqual(T.own_avg([48] * 5 + [10] * 10), 10.0)    # 只看最近 10 場有出場的
        prior = [[[1, 30], [2, 20]], [[1, 0], [2, 20]], [[2, 20], [3, 10]]]
        got, restored = T.candidate_minutes(prior)
        self.assertEqual(got, {1: 30.0, 2: 20.0, 3: 10.0})              # 1 號缺一場、3 號只打一場，都不被 0 拉低
        self.assertEqual(restored, set())

    def test_own_log_across_teams(self):
        prior = [[[1, 20], [2, 20]]]
        got, _ = T.candidate_minutes(prior, logs={1: [30, 30, 20], 2: [20]})   # 1 號之前在別隊打過 → 用自己的紀錄
        self.assertAlmostEqual(got[1], 80 / 3)
        self.assertEqual(got[2], 20.0)

    def test_return_threshold_restores_injured(self):
        prior = [[[1, 30], [2, 20]]] * 3
        logs = {1: [30] * 3, 2: [20] * 3, 7: [0, 28, 30], 8: [14.9, 12], 9: []}
        roster = {1, 2, 7, 8, 9}
        got, restored = T.candidate_minutes(prior, logs, roster)
        self.assertEqual(restored, {7})                                  # 7 號最近沒出場但自己平均 29 ≥ 15 → 補回；8 號 13.45 不夠；9 號本季沒出場
        self.assertAlmostEqual(got[7], 29.0)
        self.assertNotIn(8, got); self.assertNotIn(9, got)
        self.assertEqual(T.candidate_minutes(prior, logs, None)[1], set())   # 沒給名單就不補人
        rot = dict(T.rotation(prior, FALLBACK, logs=logs, roster=roster))
        self.assertIn(7, rot)
        self.assertNotIn(7, dict(T.rotation(prior, FALLBACK, excluded={7}, logs=logs, roster=roster)))   # 今日陣容版仍可扣掉（傷兵還沒回）

    def test_lineup_switches_at_return_date(self):
        outs = [(1, '2026-11-04'), (2, '2026-11-10'), (3, None)]
        f = lambda d: T.lineup_out(outs, d, '2026-11-02')
        self.assertEqual(f('2026-11-03'), {1, 2, 3})                    # 回歸日前：全缺
        self.assertEqual(f('2026-11-04'), {2, 3})                       # 回歸日當天就回來
        self.assertEqual(f('2026-11-09'), {2, 3})
        self.assertEqual(f('2026-11-10'), {3})
        self.assertEqual(f('2027-04-01'), {3})                          # 沒有回歸日＝整季缺陣
        self.assertEqual(T.lineup_out([(4, '2026-10-30')], '2026-11-02', '2026-11-02'), {4})   # ESPN 日期過期但今天仍列 Out：今天還是缺
        self.assertEqual(T.lineup_out([(4, '2026-10-30')], '2026-11-03', '2026-11-02'), set())

    def test_predict_wins_follows_lineup_by_date(self):
        tids = ['0', '1']
        def mg(t, d):
            return 10.0 if (t == '0' and d is not None and d >= '2026-11-10') else 0.0     # 0 隊 11/10 起回來變強
        rem = [(0, 1, '2026-11-03'), (0, 1, '2026-11-12')]
        w, ng, nr = T.predict_wins(0, 0, rem, mg, '0', tids)
        self.assertEqual((ng, nr), (2, 80))
        early = T.margin_win_prob(0.0, True); late = T.margin_win_prob(10.0, True)
        pool = 0.5 * (T.margin_win_prob(0.0, True) + T.margin_win_prob(0.0, False))        # 補的場次用最後狀態（d=None → 沒回來 → 0）
        self.assertAlmostEqual(w, early + late + 80 * pool, places=9)
        self.assertGreater(w, T.predict_wins(0, 0, rem, {'0': 0.0, '1': 0.0}, '0')[0])      # 比整季缺陣高
        self.assertAlmostEqual(T.predict_wins(0, 0, [(0, 1)], {'0': 0.0, '1': 0.0}, '0')[0], T.predict_wins(0, 0, [(0, 1, 'x')], {'0': 0.0, '1': 0.0}, '0')[0])   # 舊的 2-tuple 仍可用

    def test_page_shows_switch_and_return(self):
        html = build_teams_page.build({'season': '2026-27', 'teams': {}, 'injuries': {}, 'schedule': {}, 'version': 'inseason x', 'dataCutoff': 'd',
                                       'generatedAt': 'g', 'engine': 'e', 'seeds': 1, 'H': 2.5, 'sigma': 12, 'lastN': 10})
        self.assertIn('id="viewSeg"', html)
        self.assertNotIn('class="ctrl"', html)                  # site_header 的 CSS 有 .wrap>.ctrl{display:none}，切換列放那個 class 會整列被藏起來（桌面手機都看不到）
        self.assertIn('預計回', html)
        self.assertIn('無回歸日，當整季缺陣', html)


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
            if 'lineupStates' in t['today']:
                self.assertGreaterEqual(t['today']['lineupStates'], 1)
                for x in t['injured']:
                    if 'missGames' in x:
                        self.assertGreaterEqual(x['missGames'], 0)


if __name__ == '__main__':
    unittest.main()
