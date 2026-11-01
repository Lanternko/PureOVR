# sim 0.1.4：非投籃犯規屬性（E-189）升為預設（R-131）

## 改了哪些檔
| 檔 | 內容 |
|---|---|
| `reports/sim-0.1.4/build_ns_gamma.py`（新） | 用 2025-26 全季（1220 場、兩半合併）建 γ；定義同 `sim-0.1.3+E189-nsfoul-attr/build_attr.py`；k 凍結為 696.6998437251774（build_attr.log），不重算；不起子程序 |
| `reports/sim-0.1.4/ns-foul-gamma-2025-26.json`（新） | rbar 1.53239、center_shift −0.04717、582 人、γ sd 0.2567（範圍 −0.803～+0.811）。sha256 `dc726c61bd24a307551f5d11bf1895cae7748c214690876843a37cf43c65bef7` |
| `reports/player-impact-v53/engine.mjs` | 機制：luck 修補清單最前面加兩處字串替換（與 E-189 `engine-e189-v53.mjs` 同文）。未設 `opt.nsFoulExp` 時所有因子恰為 1、不多抽 rng() |
| `reports/player-impact-v29/benchmark.mjs` | `options()` 加 `nsFoulExp`（讀上面 json，exp(γ)，懶載入），註解寫 sim 0.1.4 |
| `reports/sim-0.1.3+E189-nsfoul-attr/engine-e189.mjs` | 只改 wrapper：永遠覆寫 `nsFoulExp`（nsAttr 為空＝null＝關），保留 E-189 harness「flag off = 0.1.3」語意 |

不是改 src：預設路徑（benchmark `options()` + `player-impact-v53/engine.mjs` → v47 → v45 → v41 → defense-tenth adapter → `src/defense_fourth_season.js`）的非投籃犯規那行是 v26～v41 engine 的字串補丁產生的，`src/` 裡沒有該行。放在 v53 engine 是不破壞 `engine-e189-v53.mjs`（讀 v47，自己補一份）錨點的位置，也沒動 v41 以下任何檔。

## 機制
1. 非投籃犯規閘門機率 × `nsFoulBase`（預設 1）× 場上 5 名防守者 exp(γ) 的平均（沒有 γ 的人當 1）。
2. 犯規者從 5 名防守者依 exp(γ) 加權抽（多一次 rng()，只在設定時；故意犯規不動）。
校準沿用 E-189：m=1、c=−0.05625、pace 0.998125，不變。

## 驗證（本機輕量，seed 20261201，round-robin 前 30 組、1 場/組）
- 4a 關閉：預設路徑（v53 engine + `options()`，fatigue:false）改動前 vs 改動後刪掉 `nsFoulExp`：30 場比分與全部球員得分／犯規逐場完全相同（非投籃犯規 390 = 390）。
- 4b 開著：預設路徑 vs E-189 harness（`engine-e189.mjs`，nsAttr＝同一份全季 γ、nsBase=1）：30 場逐場相同（非投籃犯規 393 = 393）；兩者機制補丁各自獨立（v53 engine vs engine-e189-v53 自己那份），所以這是兩份程式碼的真比對。開 vs 關確實不同（393 vs 390）。
- E-189 harness 的 flag-off（nsAttr 空）仍等於改動前預設路徑：30 場相同。
- 4c `npm test`：exit 0，JS 52 過 0 失敗、timed game 60 場過、Python 4 + 1 測試 OK；log `reports/sim-0.1.4/npm-test.log`。另單獨跑 `node test/player_workload_benchmark.js`（用 v28 engine，忽略 nsFoulExp）passed。
- 驗證腳本在 session scratchpad，未入 repo。

## 影響範圍與已知限制
- 所有用 `benchmark.mjs options()` 搭 v53 engine 鏈（`engine-e140`、E120／E122／ovr-v53+ 等 worker）的呼叫，重跑後現在會預設開 γ；歷史報告若要重現舊數字，需在 options 刪掉 `nsFoulExp`。v28 等較舊 engine 不認這個 option（npm test 不受影響）。
- 屬性用 2025-26 全季建，對 2025-26 是樣本內；E-189 的樣本外結果只對半季分割成立。
- WinImp 對 RAPM 0.432→0.417（E-189）待確認；0.1.3 以前的 WinImp 不能和 0.1.4 直接比。
- 沒做：多 seed 校準重驗（c／pace 直接沿用 E-189 final，沒在全季 γ 上重跑 round-robin 平均）。
- `.gitignore` 第 7 行忽略整個 `/reports/`：`ns-foul-gamma-2025-26.json` 現在是 `options()` 的執行期依賴，commit 需 `git add -f`，否則乾淨 clone 的 npm test 會讀不到檔（`build_ns_gamma.py`、`report.md`、`npm-test.log` 建議一起 -f）。
