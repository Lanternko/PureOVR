# 交接（handoff）

只記「目前狀態」，每次收工整份覆寫，不往下追加日期段。每條最多兩行，細節寫進 findings／experiments／rulings 或報告檔，這裡只放 ID 與路徑。UI 小改不進本檔（看 git log）。舊版全文在 `archive/`（最近一份 `handoff-2026-11-05-full.md`，含 11-05 前所有條目原文）。
**多個 session 同時改本檔與工作樹**：覆寫前先重讀一次，只改自己負責的條目。

- **更新**：2026-11-05 球員卡加追蹤量格子並發布（R-166）；11-04 E-239 追蹤全套、inseason 0.2.12e（R-161～R-165）；11-03 球隊評分換 Transformer（R-160）、近期加成 b3h20（R-150）。

## 目前基準（線上）
- **inseason 0.2.12e**（11-04，已 commit）：復出老將補卡（R-161）＋新秀起點加季前賽位移（R-162）＋防守 D 個人場次軸（R-163）＋復出老將補進用人層 hi（R-164）。未修：復出老將 gravity＝70 佔位（L-127）。回退 `DEF_AXIS=calendar`、`RV_USAGE=0`、`RETURNING_VETS=0`、`PS_START=0`。
- **追蹤量格子**（R-166，11-05）：DRV／INS／CRT／PASS／3PT 提示卡加量類追蹤列，不進分數。`scripts/tracking_cells.py`；2026-27 資料是手動快照，重抓 `node scripts/fetch_tracking_cells.mjs <季> data/tracking-cells/<季>` 後重建頁面。
- **賽中近期加成 b=3、h=20**（R-150）；**card／inseason 0.2.12**（R-139，tovSkill 看持球時間）；**0.2.11**（R-137，引力 gravity）。回退旗標 `RECENT_BOOST=0`、`TOV_POSS=0`、`GRAVITY=0`。
- **網站**：trueovr.com；首頁 2026-27、`2025-26.html`；排行／賽程用乾淨路徑 `/rank/`、`/games/`。只改 UI 用 `python -I scripts/daily_inseason_update.py --shell` 立刻發布；每日排程 14:30／16:30＋22:30（registry `basketball-inseason-daily`）。能力值說明在 `season_nav.py` 的 `ATTR_TIPS`；新格子提示用 `sn.cell_tip()`。
- **模擬 sim 0.1.3**（R-120）；防守 `nba-defense-v3`（R-010）；賽中 OVR C4（E-033）。

## 進行中（未稽核，待派 role-audit）
- **E-239 追蹤全套**（3/5）：單一特徵無穩健訊號；量類 42 個可當格子（已做）。待使用者：另開預註冊測定義一致子集（2024-25 起）進 OVR／Transformer；要不要每日抓追蹤（補 registry／audit）。`reports/E239-tracking-full/report.md`、F-160
- **E-238 無球追蹤**：補不進 OVR（H3 不過），只當個案顯示。F-158
- **E-230 新秀起點 SL／PS**：訊號小，PS 位移已套用（R-162）。待使用者決定要不要逐項起點實驗。
- **陣容 Transformer**：R-160 球隊評分已換 T，舊引擎備援。E-234／E-236／E-237 能力值→OVR Transformer 皆不勝 ridge，名單在 `reports/E234-…`、`E235-…`、`E237-…` 待人工檢查。
- **E-222 診斷**：30 隊滿 20 場時跑 `reports/E222-recent-boost-diagnostic/e222_eval.py` 一次。
- **E-151 年輕側年齡連續**：已預註冊，stints 達 450 場自動跑 `e151_eval.py`；不得提前比。
- **聯盟 3PAr 偏差**（R-146）：δ 暫不進引擎；節奏偏慢下一步未開。**0.2.10 待辦**（R-114）：role-audit 沒做、G5。

## 等使用者裁定
- E-196／R-133 得分產量（未上線）、網站品牌名（已用 trueovr.com，舊候選作廢）、0.2.10a 後續（R-121）、R-117 停損、E-162／F-106 產量評價、賽中新秀 d 對不上（R-097）、E-139 換版平滑、正負值沾光（E-148）、小項清單。全文在 `archive/handoff-2026-11-05-full.md`。

## 待辦（非決策）
- Edwards 卡 #38 但 DARKO #9／2K 95；卡對 RAPM ρ 0.78→0.70，2026-27 季後做樣本外複查；sim 得分偏高 119.1 對 115.5。
- 等季末：E-083、E-127、E-141（2026-12-31）。

## 工作樹注意
- 共用 checkout：memory 條目檔與 `season_nav.py`、`build_*_viewer.py` 常混有別的 session 改動，只挑自己的段落。`reports/` 被 gitignore，要 `git add -f`。DeepSeek 餘額不足，auto_review 失效。

## 開放問題
- 長人偏袒量尺（E-102）；卡片 OVR 要不要接進對局（F-010）；體力與換人線擱置（R-068）。
