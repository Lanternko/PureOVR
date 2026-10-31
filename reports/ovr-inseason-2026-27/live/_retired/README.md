# live/_retired

已淘汰。重現請 checkout 當時 commit。

本夾是 inseason 0.2.9 以前各版的建構腳本與凍結檔（build_prior_*、build_usage_*、prior-*.json、usage-*.json、pool-*.json）。
.py 檔頂端有 `raise SystemExit` 守門，不能直接執行；run_c4_live.py 也已不再讀這些檔。
現行版本與檔案清單見上一層 `CURRENT.json`；換版時把舊版檔案搬進本夾、更新 CURRENT.json（test/live_current_gate.py 會擋）。
