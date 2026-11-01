# 交接（handoff）

只記「目前狀態」，每次收工整份覆寫，不往下追加日期段。每條最多兩行，細節寫進 findings／experiments／rulings 或報告檔，這裡只放 ID 與路徑。UI 小改不進本檔（看 git log）。舊版全文在 `archive/`（最近一份 `handoff-2026-11-01-full.md`）。
**多個 session 同時改本檔與工作樹**：覆寫前先重讀一次，只改自己負責的條目。

- **更新**：2026-11-01，Claude Code App（lead；分支 claude/project-thread-63h2fz；handoff 瘦身 29KB→約 7KB）

## 目前基準（線上）
- **正式卡 card 0.2.10c**（R-122）：`reports/card-0.2.10c/`＝card 0.2.10a（R-121：8 項四季滑動窗口＋L-102 修好的 T6）重擬合＋傳球全位置共用斜率（E-187 KAU，修 JW 偏高）；OFFICIAL_CARD 指它。
- **新賽季頁 inseason 0.2.10** 已發布（2026-11-01）：8 項每日由窗口算（`live/window8.py`），其他屬性同前；單場評分 **Z1**（R-108，E-169，`scripts/rating_m10.py`）。
  - 2026-11-01：2026-27 pbp 沒有 area 欄位，mid／short 整季停在 day0；改用距離＋座標推導區域（佔位座標不計），2024-25 核對 mid 97.4%／short 100% 後上線（F-124、L-098，d8eaf90）；同時修歷史折線 8 項偷看全季資料。
- **網站**：首頁 2026-27、`2025-26.html`（`build_card_viewer.py`、`enrich_roster_viewer.py`、共用 `season_nav.py`）。能力值說明文字在 `season_nav.py` 的 `ATTR_TIPS`，改屬性公式要一起改；新格子提示用 `sn.cell_tip()`。只改 UI 用 `python -I scripts/daily_inseason_update.py --shell` 立刻發布；每日排程 14:30／16:30＋22:30 補對位（registry `basketball-inseason-daily`）。
- **模擬 sim 0.1.3**（R-120，2026-11-01：0.1.2 的防守者投籃犯規 β×2、c −0.05625、pace ×0.998125，`benchmark.mjs` options()；0.1.2 以前的 WinImp 數字不能直接比，G3）；防守 `nba-defense-v3`（R-010）；賽中 OVR C4（E-033）、顯示值 B0。
- 新賽季頁版本由 `reports/ovr-inseason-2026-27/live/CURRENT.json` 決定，`test/live_current_gate.py` 掛在 npm test（L-090）；舊建構腳本放 `live/_retired/`。

## 進行中
- **0.2.10 待辦**（R-114）：獨立 role-audit 沒做（F-116：組合值評 foulDraw／pass 不過，使用者知情上線）；換季跳動對 0.2.9a 沒量；Porter Jr. 20→40；G5。
- **E-166 β×2 → sim 0.1.3 已上線**（R-120）：非中鋒罰球防守散布 0.54→1.04、中鋒 0.23→0.56；防守型非中鋒少低估 12 名，S 偏袒長人 +79→+107、30 隊 MAE +0.154。未解：名次和 S 方向相反、F-112 剩 +54 名低估。`reports/sim-0.1.2+E166-ft-defense/`
- **E-151 年輕側年齡連續**：已預註冊（6820474），每日排程在 2026-27 stints 達 450 場時自動跑 `e151_eval.py` 一次（daily.log 會出現 WARNING「E-151 評估完成」）。不得提前拿卡片去比。

## 等使用者裁定
- **E-189 非投籃犯規屬性**（R-125 重開 F-129 額度）：預註冊草稿 `reports/sim-0.1.3+E189-nsfoul-attr/preregistration.md` 待使用者凍結。F-130（球隊造罰球偏大＝5 名真實球員占 73% 出手）待使用者決定改不改。
- **E-188 OVR 頂端錨 S3 → card 0.2.10b**（2026-11-01，F-131）：PR90→88、PR95→92，≥500 分鐘池 OVR 90–99 從 4 人變 20 人，名次與其他欄逐位元不變，npm test 過。未切 `OFFICIAL_CARD`、未部署、未 commit；新賽季頁 patch 在 `reports/card-0.2.10a+E188-ovr-top-scale/live-patch.md`，要交 27 賽季 session（0.2.12）。副作用：70–88 段 ΔOVR ×1.66、92–99 段 ×0.49。E-187 KAU 已採用為 0.2.10c（R-122），E-188 上線前要把 `build_card_0210b.py` 的 BASE 改成 0.2.10c 重跑（錨不變）。
- **0.2.10a 後續**（R-121）：新賽季頁仍是舊 T6，等 0.2.12（以 0.2.10a 為底）一起修；H1 封頂壓前段（SGA 118.8→103.8）另議；E-142／E-153／E-186 用舊 T6 要重核。
- **F-126 難球命中問題卡**（2026-11-01 開卡，額度 3）：NBA.com Shot Difficulty 逐球 xFG% 有 2025-26、2026-27（`shotqualityvideologs`），Gravity 只有整季。下一步第 0 步診斷：SM＝FG%−xFG% 對卡片殘差的斜率（RAPM 分半交叉）。改卡片 OVR 牴觸 R-020，要使用者改裁定。`reports/F126-shot-difficulty/data-check.md`
- **R-117 停損**：JW、長人犯規兩條線只做診斷，不提新假設，除非使用者重開額度；全文見 rulings。
- **E-181 無球能力值**（2026-11-01 完成：不採用，F-119、L-096）：無球型（offBall 高、creation 低）在 2024-25 卡對下季 RAPM 確實低估約 9 個百分點，但加「被助攻得分／36」屬性係數幾乎 0、補不回。下一步待使用者：從 T6 目標或 creation 定義下手（同 F-118），或放著。`reports/E181-offball-attr/report.md`
- **JW 偏高 F-125 已修（R-122，2026-11-01）**：正式卡改 **card 0.2.10c**＝0.2.10a 修正後 T6 重擬合＋傳球全位置共用斜率（E-187 KAU）；JW 第 9→12（MIN≥500）、分段殘差 −1.50→−1.22。新賽季頁仍 0.2.10 係數；**0.2.12 若要帶上本修正要改以 0.2.10c 為底**。2026-27 季末用本季 RAPM 做樣本外複查。`reports/card-0.2.10c/report.md`
- **ΔOVR 基準（R-112，2026-11-01）**：老將 lastOVR＝今天的模型但本季 0 場（窗口 cur=False、防守 D 逐人 leave-one-out、posMeanD 用賽中版），0 場的人 ΔOVR 全部 0；JW +2.34→+0.35。已發布。
- **E-162／F-106 產量評價**：卡相對 T6 不低估高用球者，只是相對薪水低估；選項：接受 T6、提高市場權重（另寫預註冊）、先放著。`reports/card-0.2.9+E162-per-volume/report.md`
- **E-154** 3/5 不採用（F-100），等使用者確認結案。
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
