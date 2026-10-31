# 交接（handoff）

只記「目前狀態」，每次收工整份覆寫，不往下追加日期段。每條最多兩行，細節寫進 findings／experiments／rulings 或報告檔，這裡只放 ID 與路徑。UI 小改不進本檔（看 git log）。舊版全文在 `archive/`（最近一份 `handoff-2026-11-01-full.md`）。
**多個 session 同時改本檔與工作樹**：覆寫前先重讀一次，只改自己負責的條目。

- **更新**：2026-11-01，Claude Code App（lead；分支 claude/project-thread-63h2fz；handoff 瘦身 29KB→約 7KB）

## 目前基準（線上）
- **正式卡 card 0.2.9**（R-104，E-158 Y0）：`reports/card-0.2.9/`；status_snapshot `OFFICIAL_CARD` 已指 0.2.9。版本鏈與每版理由查 experiments／rulings。
- **新賽季頁 inseason 0.2.9** 已發布；單場評分 **Z1**（R-108，E-169，`scripts/rating_m10.py`）。
- **網站**：首頁 2026-27、`2025-26.html`（`build_card_viewer.py`、`enrich_roster_viewer.py`、共用 `season_nav.py`）。能力值說明文字在 `season_nav.py` 的 `ATTR_TIPS`，改屬性公式要一起改；新格子提示用 `sn.cell_tip()`。只改 UI 用 `python -I scripts/daily_inseason_update.py --shell` 立刻發布；每日排程 14:30／16:30＋22:30 補對位（registry `basketball-inseason-daily`）。
- **模擬 sim 0.1.2**（R-094，防守者投籃犯規預設開；之前的 WinImp 數字不能直接比，G3）；防守 `nba-defense-v3`（R-010）；賽中 OVR C4（E-033）、顯示值 B0。
- 新賽季頁版本由 `reports/ovr-inseason-2026-27/live/CURRENT.json` 決定，`test/live_current_gate.py` 掛在 npm test（L-090）；舊建構腳本放 `live/_retired/`。

## 進行中
- **card／inseason 0.2.9a 拿掉 stamina 已發布**（2026-11-01，R-107／R-109，commit 162c139、gh-pages fb59ab0；連同壓迫／切入解凍）。舊路徑守門：`live/CURRENT.json`＋`test/live_current_gate.py`（L-090）。待辦：另開 session 做 role-audit 重算 → 使用者 G5。
- **E-166 罰球防守 β×k**（側翼低估線，F-103～F-105）：已凍結，5090 `~/e166` 執行中。報告 `reports/sim-0.1.1-wing-diag/poss-report.md`（實為 sim 0.1.2，L-089）。
- **E-151 年輕側年齡連續**：已預註冊（6820474），每日排程在 2026-27 stints 達 450 場時自動跑 `e151_eval.py` 一次（daily.log 會出現 WARNING「E-151 評估完成」）。不得提前拿卡片去比。

## 等使用者裁定
- **E-162／F-106 產量評價**：卡相對 T6 不低估高用球者，只是相對薪水低估。選項：接受 T6、在口徑或目標提高市場權重（要另寫預註冊）、先放著。`reports/card-0.2.9+E162-per-volume/report.md`。
- **E-154 壓迫情境校正** 3/5 不採用（F-100）：等使用者確認結案。
- **賽中新秀 d 對不上**（R-097、F-090）：季末連續 d 和卡的二元 d 在 MEM／DAL／NOP／CHI／MIL 對不上。選項：卡也改連續 d，或拉長 R-092 回歸窗口。上季爛隊的年輕人開季普遍 +17～23，使用者說「晚點再改」。
- **E-139 開季先驗權重** 判「沒有改善」（F-087），線上維持 B0，下一步未定；卡片換版讓年輕球員單日跳 ±10–17，換版平滑還沒開實驗。
- **正負值沾光**（大勝時投不好的人評分偏高）：E-148 不過（F-092），下一步未定。
- E-132 errata（階段 B 2027-02 回來算）；E-134 階段 1 已完成；E-130 結案與否（worktree `D:/Projects/CODING/ba-e130`）；E-100 第二階段；E-114 草稿待核可；E-122 D1 未表態。
- 小項：TO 刪或改持球分母（R-032）、INS 拆分、foulDraw／drive／onBall 改原始值（F-046）、補籃另開能力值（R-056）、防守四項權重（R-053）、Hauser「護球」改名。

## 待辦（非決策）
- Edwards 卡 #38，但 DARKO #9／2K 95，開季 4 場 +16 而賽中 OVR 不升，待查。Podziemski 賽中 #20（卡 #41，約 +3 分來自 ≤23 歲加分）。
- 卡對 RAPM ρ 0.78→0.70（0.2.8 起）；2026-27 季後做真正的樣本外複查。
- sim 得分偏高 119.1 對 115.5（TODO）。E-090 狀態欄要改成被 E-101 取代。
- 等季末：E-083 跨季 RAPM d=0.75、E-127 換隊隔年變好、E-141 新秀曲線的前瞻檢查（2026-12-31）。

## 工作樹注意
- 共用 checkout：memory 條目檔、`scripts/season_nav.py`、`build_card_viewer.py`、`build_inseason_viewer.py` 常混有別的 session 的改動，只挑自己的段落 commit。`reports/` 被 gitignore，要 `git add -f`。
- 2026-11-01 時 memory 條目檔有大約 1,400 行沒 commit（多個 session 寫入），下次 commit memory 前先 `git diff` 確認。
- DeepSeek 餘額不足（402），auto_review 失效。

## 開放問題
- 長人偏袒量尺（E-102）：E-076 G5 升不升版、量尺與 b1 停止條件、H1 基準陣容。OVR 量「比平均球員」（R-103），籃板不算偏差。
- 卡片 OVR 要不要接進對局（F-010）；體力與換人線擱置（R-068）；Stewart help 99（E-080）。
