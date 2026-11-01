# 交接（handoff）

只記「目前狀態」，每次收工整份覆寫，不往下追加日期段。每條最多兩行，細節寫進 findings／experiments／rulings 或報告檔，這裡只放 ID 與路徑。UI 小改不進本檔（看 git log）。舊版全文在 `archive/`（最近一份 `handoff-2026-11-01-full.md`）。
**多個 session 同時改本檔與工作樹**：覆寫前先重讀一次，只改自己負責的條目。

- **更新**：2026-11-01，Claude Code App（lead；分支 claude/project-thread-63h2fz；handoff 瘦身 29KB→約 7KB）

## 目前基準（線上）
- **正式卡 card 0.2.10**（R-114，E-175）：`reports/card-0.2.10/`；8 項能力值（mid、short、ft、foulDraw、pass、rebound、tovSkill、drive）改 R-076 四季滑動窗口，OVR 係數／錨點／用人層凍結 0.2.9a（`frozen.json`）。status_snapshot `OFFICIAL_CARD` 指 0.2.10。
- **新賽季頁 inseason 0.2.10** 已發布（2026-11-01）：8 項每日由窗口算（`live/window8.py`），其他屬性同前；單場評分 **Z1**（R-108，E-169，`scripts/rating_m10.py`）。
- **網站**：首頁 2026-27、`2025-26.html`（`build_card_viewer.py`、`enrich_roster_viewer.py`、共用 `season_nav.py`）。能力值說明文字在 `season_nav.py` 的 `ATTR_TIPS`，改屬性公式要一起改；新格子提示用 `sn.cell_tip()`。只改 UI 用 `python -I scripts/daily_inseason_update.py --shell` 立刻發布；每日排程 14:30／16:30＋22:30 補對位（registry `basketball-inseason-daily`）。
- **模擬 sim 0.1.2**（R-094，防守者投籃犯規預設開；之前的 WinImp 數字不能直接比，G3）；防守 `nba-defense-v3`（R-010）；賽中 OVR C4（E-033）、顯示值 B0。
- 新賽季頁版本由 `reports/ovr-inseason-2026-27/live/CURRENT.json` 決定，`test/live_current_gate.py` 掛在 npm test（L-090）；舊建構腳本放 `live/_retired/`。

## 進行中
- **card／inseason 0.2.10 已發布**（2026-11-01，R-114）：稽核用顯示組合值評 foulDraw／pass 時不過 adopt（F-116），使用者知情仍上線。待辦：card-0.2.10 獨立 role-audit（`audit/` 只有說明）、換季跳動同口徑對 0.2.9a 沒量到、Porter Jr. 20→40 要看、使用者 G5。
- **E-166 罰球防守 β×k**（側翼低估線，F-103～F-105）：2026-11-01 完成「不採用」（F-111）。k=2 把罰球防守補到實測散布，36 名防守型非中鋒平均少低估 12 名、Spearman +0.04；但 30 隊 MAE +0.154 超過門檻 0.1、E-067 S 偏袒長人變大。報告 `reports/sim-0.1.2+E166-ft-defense/report.md`。同日 F-112 查 WinImp 情境：換成同位置隊友，36 人低估 90.6→54.1、中鋒 −60→+9，但整體 ρ 0.388→0.324；主版中鋒每場有 +2.4 位置紅利、得分後衛防守權重 0.01；分鐘不是原因。報告 `reports/sim-0.1.2-winimp-context/report.md`。同日 F-114 雙中鋒：實測雙中鋒≈加總（+0.8／100，雜訊內），模擬多 +2.6／100（籃下防守疊加），整隊換一個平均 C 強 4 分／場；報告 `reports/sim-0.1.2-twin-c/report.md`。分區補充：實測雙中鋒沒讓對手多投三分，唯一穩定成本是對手多罰 +2.6／100（模擬 +0.3）。使用者選雙長人犯規成本：E-178 預註冊已凍結（≥2 中鋒時犯規 logit +γ），j0 過，但引擎的位置是槽位標籤、γ 永遠不觸發（L-094）；修正 A1（改用球員本身位置）已凍結、執行中，派工 task 20261101-081630-b7c13f。
- **E-151 年輕側年齡連續**：已預註冊（6820474），每日排程在 2026-27 stints 達 450 場時自動跑 `e151_eval.py` 一次（daily.log 會出現 WARNING「E-151 評估完成」）。不得提前拿卡片去比。

## 等使用者裁定
- **card 0.2.11（L-102／F-128）**：BPM 解析把聯盟第一讀成空值，Jokić 四季都不在 T6；修好重建 Jokić 7→3，但 H1 封頂壓縮前段（SGA 118.8→103.8、Kawhi 3→6）。待使用者：直接上線，或先處理封頂。E-186 用的是舊 T6，要重跑。`reports/card-0.2.11/report.md`
- **R-117 問題卡與停損**（2026-11-01，commit 1697309）：之後的 JW 偏高、長人犯規兩條線都要先補問題卡（F 條目）、算 MDE；兩條已連續多次不過，下一步只能做診斷（例如 JW 名次是否超出 RAPM 分半雜訊），不再提新假設，除非使用者重開額度。預註冊只准「主目標修到／沒弄壞」兩類必過，球隊 MAE 等只權衡（R-042、L-099）。
- **E-181 無球能力值**（2026-11-01 完成：不採用，F-119、L-096）：無球型（offBall 高、creation 低）在 2024-25 卡對下季 RAPM 確實低估約 9 個百分點，但加「被助攻得分／36」屬性係數幾乎 0、補不回。下一步待使用者：從 T6 目標或 creation 定義下手（同 F-118），或放著。`reports/E181-offball-attr/report.md`
- **JW 偏高問題卡 F-125**（2026-11-01 停損後診斷）：對卡片目標 T6 殘差 ≈0；對本季 RAPM −0.87、SE 0.79（z −1.1，和 Edwards／Durant 同區），和雜訊分不開；專修 JW 的 MDE 1.6 大於落差，不跑。使用者 /goal 要解決 → 換方向：E-186（目標 T6 混四季 RAPM，w=0.5）已凍結、派 role-card。`reports/F125-jw-noise-check/report.md`
- **ΔOVR 基準（R-112，2026-11-01）**：老將 lastOVR＝今天的模型但本季 0 場（窗口 cur=False、防守 D 逐人 leave-one-out、posMeanD 用賽中版），0 場的人 ΔOVR 全部 0；JW +2.34→+0.35。已發布。
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
