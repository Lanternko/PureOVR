2026-11-02 開工：工作樹 live/、season_nav 無他人改動；E-207 疊 0.2.12b(W246)→0.2.12c
- 2026-11-02 tov_live.py 觸球版（TOV_TOUCH、window_tch、freeze_touch）完成；tov-pool-card0212c.json 凍結，重現 KC tovSkill max|diff| 2e-8；fetch_possessions NEED 加 TOUCHES
- 2026-11-02 tov_live.CARD→card-0.2.12c-w328；build_0212c.py 建 328 底，ranking 與 KC final 逐位元組相同；window8 加 _tc
- 2026-11-02 run_c4_live.py 語法修好（CRLF 檔，ATTR_NOTE 0.2.12c 段）
- 2026-11-02 run_c4_live_rookie.py ROOKIE_JSON 加 TOV_TOUCH 分支；舊 rookie-prior 備份 _retired/rookie-prior-2026-0212b.json
- 2026-11-02 c0 卡片端：TOV_TOUCH=0 WIN_LEN=246 card_route_0212c→make_card 的 ranking.csv 與 card-0.2.12b 逐位元組相同
- 2026-11-02 reports/card-0.2.12c/ 以 w328 檔播種；make_card_0212c.py 改 SRC=card-0.2.12b、錨點取 w328；開跑 WIN_LEN=246 TOV_TOUCH=1 card_route → work/on246
- 2026-11-02 card-0.2.12c/ 建成（W246，sha 7083ced9…）；live 端 c0：TOV_TOUCH=0 ranking.csv 與 HEAD 碼同資料逐位元組相同（參考夾 live_ref 為暫時副本，之後刪）
- 2026-11-02 站台：season_nav／build_card_viewer／fetch_possessions 改完、npm test 過、daily --dry-run 兩頁建成（TO 提示含每百次觸球失誤）；準備 commit＋發布
