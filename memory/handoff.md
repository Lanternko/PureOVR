# 交接（handoff）

只記「目前狀態」，每次收工整份覆寫，不往下追加日期段。每條最多兩行，細節寫進 findings／experiments／rulings 或報告檔，這裡只放 ID 與路徑。UI 小改不進本檔（看 git log）。舊版全文在 `archive/`（最近一份 `handoff-2026-11-01-full.md`）。
**多個 session 同時改本檔與工作樹**：覆寫前先重讀一次，只改自己負責的條目。

- **更新**：2026-11-03，賽中 OVR 近期加成 b3h20 上線（R-150，E-221／E-222，d4a43fc，gh-pages 46e288f）；同日回報格式拿掉五級文字標籤（R-148 併入 R-011）

## 目前基準（線上）
- **賽中近期加成 b=3、h=20**（R-150，11-03 上線）：本季逐場權重加重近期場次，最後 20% 季淡出、季末不變；`RECENT_BOOST=0` 回舊版。單場評分－上季平均 vs 當場 ΔOVR 相關 0.28→0.43、大場當場上漲 67%→79%（量法 scratch，未進報告）。`live/recent_boost.py`
- **card／inseason 0.2.12**（R-139，E-203，11-02 上線，gh-pages 7fc64c4）：tovSkill 改看持球時間（0.5·z(−每持球分鐘失誤)＋0.5·z(持球分鐘/36)），其餘不動；每日抓 `possessions.json`；`TOV_POSS=0` 重現 0.2.11。正式卡 `reports/card-0.2.12-tov/`。
- **card／inseason 0.2.11**（原 0.2.10j，R-137；R-134／R-135，E-200）：加能力值引力 gravity（主畫面 GRV 取代切入位置，每日抓本季引力），`GRAVITY=0` 重現 0.2.10i。`reports/card-0.2.10j/`、`live/gravity_live.py`
- **網站**：首頁 2026-27、`2025-26.html`（`build_card_viewer.py`、`enrich_roster_viewer.py`、共用 `season_nav.py`）。能力值說明文字在 `season_nav.py` 的 `ATTR_TIPS`，改屬性公式要一起改；新格子提示用 `sn.cell_tip()`。只改 UI 用 `python -I scripts/daily_inseason_update.py --shell` 立刻發布；每日排程 14:30／16:30＋22:30 補對位（registry `basketball-inseason-daily`）。
- **模擬 sim 0.1.3**（R-120，2026-11-01：0.1.2 的防守者投籃犯規 β×2、c −0.05625、pace ×0.998125，`benchmark.mjs` options()；0.1.2 以前的 WinImp 數字不能直接比，G3）；防守 `nba-defense-v3`（R-010）；賽中 OVR C4（E-033）、顯示值 B0。
- **新秀開季起點**（R-096，2026-11-01 重解）：0.2.10e～h 換版後 δ 沒重解、起點跑掉（L-109）；已用 `reports/E121-rookie-scale/build_2k_start.py` 重解，42 人 ≤0.05；`test/rookie_start_gate.py`（npm test）擋換版後再跑掉。換版後要重跑該腳本。

## 進行中
- **E-222 診斷**（R-149 已被 R-150 推翻，保留作事後檢查）：MDE_p 0.030，每日更新在 30 隊滿 20 場時跑 `reports/E222-recent-boost-diagnostic/e222_eval.py` 一次；errata-1（c→g 改 15·c）未核可。剩餘落差：OVR 結構不看重部分高評分表現（Murray 16.9 分場 +0.2）
- **聯盟 3PAr 偏差**（11-03）：預註冊 1 來源不明；預註冊 2（E-219）位置池對手 K=0.62 部分原因；預註冊 3（E-220，F-148，R-146）3 分 logit 位移 δ*=0.27／0.10 補齊 3PAr 無副作用，但節奏只補 5–8%，同源不成立。使用者 11-03 裁定 δ 暫不進引擎；節奏偏慢下一步（查回合組成：失誤率、罰球率）未開。`reports/3par-logit-shift/report.md`；E-219 報告尚未稽核
- **球星重疊遞減 E-217**（11-02）：H1 不通過，OL 單隊多為噪音，要驗證需約 10 倍場數。`reports/star-overlap/report.md`
- **E-208／E-213 球隊評分**（11-02）：`teams.html` 上線；傷病 ESPN→官方PDF（E-214）；缺陣球員補底卡 E-216。`reports/E208-team-rating/report-missing-profiles.md`
- **0.2.10 待辦**（R-114）：獨立 role-audit 沒做（F-116：組合值評 foulDraw／pass 不過，使用者知情上線）；換季跳動對 0.2.9a 沒量；Porter Jr. 20→40；G5。
- **E-166 β×2 → sim 0.1.3 已上線**（R-120）：罰球防守散布拉開，防守型非中鋒少低估 12 名；未解：S 偏袒長人 +79→+107、F-112 剩 +54 名低估。`reports/sim-0.1.2+E166-ft-defense/`
- **E-151 年輕側年齡連續**：已預註冊（6820474），每日排程在 2026-27 stints 達 450 場時自動跑 `e151_eval.py` 一次（daily.log 會出現 WARNING「E-151 評估完成」）。不得提前拿卡片去比。

## 等使用者裁定
- **E-196／R-133 得分產量**（11-01 完成，未上線）：產量取代 creation 樣本外無球組低估 5.2→4.5，但係數全靠下限撐；待選。`reports/card-0.2.10g+E196-production/report.md`
- **網站品牌名**（11-01）：傾向 Pure.OVR（pureovr.com 可註冊），備選 hoopgrade、ovihoops；未買、社群帳號未查。`reports/site-naming/domains.md`
- **0.2.10a 後續**（R-121）：新賽季頁仍是舊 T6，等 0.2.12（以 0.2.10a 為底）一起修；H1 封頂壓前段（SGA 118.8→103.8）另議；E-142／E-153／E-186 用舊 T6 要重核。
- **R-117 停損**：JW、長人犯規兩條線只做診斷，不提新假設，除非使用者重開額度；全文見 rulings。
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
