# E-190 報告：停在 c0（預註冊前提錯）

- 日期：2026-11-01。執行：role-card 子 agent（App session 內，routing=self）；lead 核對 sha 與 results.json。
- 結論：**沒判定**。c0 第 1 部分過，第 2 部分不過，依 spec 停下；phase0、KJ 沒跑，a1／a2 沒有數字。

## c0
1. KAU 重建：2025-26 ranking.csv sha e46315bd…158b ＝ `reports/card-0.2.10c/ranking.csv`（lead 重算一致）；三歷史原點 298／349／417 人。
2. 舊 creation 逐球重現：**不過**（門檻 <1e-6）。MIN≥500 378 人：最大差 17.6、平均 3.8、108 人 >5、r 0.958；全 582 人最大 41.4、r 0.889。

## 原因（三處預註冊寫錯，lead 的錯，L-105）
1. 舊 creation 原值＝(1 − creationDependence_sourceRole) × FGA／36；sourceRole 來自 player-impact-v30 的接球機會占比，經 `src/source_creation_dependence.js` 用 selfCreation 調整，是模擬模型量，不是逐球助攻加權。用此式重算與 a0-raw.json 差 0.0。逐球版把中鋒非助攻補籃／低位算成自主：Mitchell Robinson 42.2→59.8、Gobert 40.9→55.3、Ayton 39.9→53.8、Capela 52.2→65.6；Lonzo Ball 55.9→42.9。
2. 換算：舊欄用 E-101 多季合併池＋頭尾延伸（範圍 38.8–108.7），不是 attach_creation 單季池；只換池最大差 9.7。
3. 窗口：0.2.10c 的 creation 是 2025-26 單季、四原點共用（L-091），不是四季滑動（R-118 在 0.2.10d 才落實）。

## 其他
- `work/creation-recompute.csv` 附帶算了 creationJ，子 agent 與 lead 都沒拿它算 a1／a2 或與 drive 的相關。
- npm test：52 passed、0 failed，engine OK，Python 4 OK。
- 檔案：`build.py`、`run_all.py`（E187-rebase 複本，只改 work 路徑）、`build_creation_jumper.py`、`results.json`（含全部 sha256）、`work/`、`logs/`。
