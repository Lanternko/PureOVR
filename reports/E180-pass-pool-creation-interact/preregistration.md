# E-180 預註冊：傳球改全位置共用斜率／creation、foulDraw 加位置交互項（修 E-179 的前鋒高估）

- 日期：2026-11-01。來源：使用者看完 E-179（creation 前鋒高估、pass 全位置偏高）後說「寫修正預註冊」。
- 基準：card 0.2.9a（`reports/card-0.2.9a/ranking.csv`；建卡管線＝E-164 S 臂，位置只在 `reports/card-0.2.9+E164-no-stamina/calibrate_wing_t.py` 讀，見 E-177 `phase0.md`）。
- 狀態：草稿，待使用者核可凍結。

## 0. 已揭露（lead 寫本檔前看過的東西）
- E-179（三個歷史原點對下季 RAPM）：creation 的前鋒−後衛殘差差 −0.14 [−0.25, −0.03]；pass 前鋒 −0.32、後衛 −0.29，差不顯著；foulDraw 差 −0.17（只報告）。**這三季的下季 RAPM 對本問題已經看過，不能再當判定資料**（L-026）。
- E-176／F-113：2025-26 同季外部進攻殘差（樣本內）。
- 卡片設計：`INTERACT = ['long', 'short', 'pass', 'rebound', 'help']`，位置虛擬變數 PG／SG／SF／PF（C 為基準），ridge 1.0。**creation、foulDraw 沒有位置交互項**，所以 E-179 看到的前鋒 creation 偏差不是交互項造成的；可能來源是 T6 目標本身、或和 pass 交互項共線（L-095）。
- 歷史原點的能力值是 2025-26 現值（L-091）。
- **沒看過**任何改動後的卡片、OVR、名次。兩個臂都是結構改動，沒有可調數值；判定不得以 JW 或任何單一球員為條件，JW 只列在例子表。

## 1. 臂（只動 `INTERACT`，其餘照 0.2.9a）
| 臂 | INTERACT | 想法 |
|---|---|---|
| K0 | long, short, pass, rebound, help | 0.2.9a 原樣。c0：重建後 2025-26 ranking 與 `reports/card-0.2.9a/ranking.csv` 逐位元相同，不同就停 |
| A | long, short, rebound, help | 傳球不分位置，一條斜率（E-179：pass 偏高不分位置） |
| B | long, short, pass, rebound, help, creation, foulDraw | 讓 creation、foulDraw 依位置各自擬合（E-179：這兩項前鋒偏差較大） |

不動：能力值、目標 T6、ridge、RAPM 混合、用人層、映射錨、r_repl、賽中管線、名單頁、`season_nav.off_def`。

## 2. 兩階段
### 第 1 階段（現在跑，只做不劣於檢查，不決定採用）
- c0（K0 逐位元）、`npm test` 過。
- 2025-26 卡（MIN ≥ 500）：
  - s1：Spearman(OVR, 薪水 errata-1 權重) 與 Spearman(OVR, 2K `data/external-impact/2k/2k-merged-e142.csv`)，X−K0 的球員層 bootstrap（2000 次，seed 20261101）90% 下界 > −0.01。
  - s2：隊內 MIN–OVR Spearman 30 隊中位數，X 不低於 K0 超過 0.02。
- 第 1 階段不過的臂，直接不採用，不進第 2 階段。

### 第 2 階段（判定；2026-27 RAPM 到位才跑）
- 時點：2026-27 例行賽 RAPM（照 E-126 `rapm_season.py` 的作法），**在 2025-26 卡人群中 poss ≥ 1000 的人數 ≥ 250 時**才跑，最早 2027-02-15；資料截止日寫進 results.json，之後不換日期重跑。
- 卡片：第 1 階段建好的 2025-26 K0／A／B（能力值是當季值，沒有 L-091 的問題）。
- 答案：2026-27 RAPM `net`、`O`，乘 `wfun(2026-27 mpg)`；人群照 E-179 §2。
- 統計量照 E-179 §3：e_net＝pct(net×W)−pct(OVR)，前鋒 F＝SF/PF、後衛 G＝PG/SG（K0 的硬標籤，三臂同一份分組）；D_a＝S_F(a, e_net)−S_G(a, e_net)。bootstrap 2000 次，seed 20261101，90% 區間；臂間差在同一組重抽上算。
- 判定：
  - **前提 p0**：K0 的 D_creation 上界 < 0（偏差在新資料重現）。不成立 → 判「偏差沒重現，不改卡」，A／B 都不採用。
  - **臂 X 採用候選**（X ∈ {A, B}）同時滿足：
    - ① D_creation(X)−D_creation(K0) 的下界 > 0（前鋒 creation 偏差變小）；
    - ② Spearman(OVR, net×W)，X−K0 下界 > −0.01（整體不變差）；
    - ③ 第 1 階段已過。
  - A、B 都是候選時選 A（改動較少）。都不是 → 不採用。
- 只報告：D_pass、D_foulDraw、S_C；e_O 版本；JW、Jalen Johnson、Paolo Banchero、Scottie Barnes、Franz Wagner、LeBron James 的三臂 OVR／名次與 OFF 拆解。

## 3. 只報告（第 1 階段）
- 三臂的係數表（pass、creation、foulDraw 各位置的有效斜率＝主效應＋交互項）。
- 前鋒內 pass 與 creation 的 Spearman（看共線）。
- 2025-26 前 20 名進出、OVR 變動最大的 20 人、上面例子球員。
- E-179 三季統計量在 A／B 下重算——**已看過答案的資料，只當方向參考，不進判定**。

## 4. 限制
- 只寫 `reports/E180-pass-pool-creation-interact/`；0.2.9a、E-164、E-153、E-142 目錄唯讀；不改 `src/`、不改賽中管線。
- T6 目標不動；若偏差來自 T6 本身，兩臂都可能無效（那會是 p0 成立、① 不過）。
- 第 2 階段要等數個月；這段時間正式卡維持 0.2.9a。
- 回報用六段格式（CLAUDE.md）。

## 5. 產出
- 第 1 階段：`e180_build.py`、`ranking-{K0,A,B}-2025-26.csv`、`stage1.json`、`stage1.md`。
- 第 2 階段：`e180_stage2.py`、`results.json`、`report.md`。
