# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段是 2026-10-30 依 `main` `3bfb2b541844` 與固定上游快照重查的結果；遠端 fork 與舊告警數本次未重查。

## 現況
Buzz 是可自行架設、讓人與代理共用簽章事件記錄的通訊工作區，fork 維持上游產品行為（[README](README.md)、[FORK](FORK.md)）。2026-11-02 已再逐筆裁決至上游 main `d342cf141cb3211c8e5a6c74f881cf1d39ad3b12`（84 commit：1 adopt、8 skip、75 defer；195 PR：1 adopt、55 skip、139 defer；15 issue：5 skip、10 defer，見 [本輪裁決](docs/fork/UPSTREAM_REVIEW_2026-11-02.md)）。2026-11-07 因 CI 紅燈採用兩項上游修補：#8711（Android lane 釘 JDK 17）與審查範圍之後的 #8922（RUSTSEC-2026-0433／0429），推送後須看遠端 CI 才能說已綠。以下為 2026-10-30 的前一輪：已逐筆裁決至 `6d719c680a85c98153324809988be37425fba73e`：累計 32 個 commit（6 skip、26 defer）、54 筆 PR（12 skip、42 defer）與 2 筆 issue（均 defer），沒有採用產品變更。水位為該完整 commit／PR #8699／issue #8684；最新清單沒有新增 issue，故 issue 編號不變。Tauri 鎖檔 advisory 盤點已重跑（0 漏洞，unmaintained 均為既有項目，不擴大 ignore，見 [既有裁決](docs/fork/DECISIONS.md)）。維護工具 gate 為 29 passed；產品同步與原生驗收尚未完成。2026-10-29 的 Dependabot 103 筆、Code scanning 161 筆未重查，不視為目前告警數；#8624 已關閉未合併，等待替代修補（[本輪裁決](docs/fork/UPSTREAM_REVIEW_2026-10-30.md)、[增量證據](docs/fork/UPSTREAM_REVIEW_2026-10-30_INCREMENT.json)、[既有裁決](docs/fork/DECISIONS.md)）。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| （目前無） | - | - | - | - |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 同步延後變更 | 可用受影響平台／Postgres 的完整驗收環境；本批長編碼／長行拒收需符合政策的修訂或維護者明確決定 | 依固定裁決逐筆帶入（#8711、#8922 已帶入，不在此列），保留 FORK.md 修補與發布 guard；重跑 Tauri advisory 盤點、維護工具及受影響產品閘門；提交後檢查 CI，不能把已審查水位當成產品同步完成 | Codex | docs/fork/UPSTREAM_REVIEW_2026-10-30.md；docs/fork/UPSTREAM_REVIEW_2026-10-30.json；docs/fork/UPSTREAM_REVIEW_2026-11-02.md（84 commit、195 PR、15 issue；2026-11-07 起 #8711 改 adopt）；docs/fork/UPSTREAM_REVIEW_2026-11-02.json |
| 隨上游採用編輯器與 selector 安全更新 | 取代已關閉未合併 #8624 的上游修補合併，或 typography 放寬 selector 版本且可由相容鎖檔更新解決 | 對照實際修補 commit 與依賴鏈帶入；連結貼上回歸與 desktop 型別檢查通過，對應 Dependabot 告警 state=fixed | Codex | docs/fork/UPSTREAM_REVIEW_2026-10-30.md「#8624 與路線圖」；docs/fork/DECISIONS.md |
| 隨上游遷移 rmcp、glib 與 lru 依賴鏈 | 上游完成相容遷移或依賴鏈容許修補版 | 檢查 buzz-agent 實際依賴與兩份 Cargo.lock，跑受影響 Rust／Tauri gate；移除已不需要的 advisory ignore | Codex | docs/fork/DECISIONS.md:56、78、82-86；deny.toml |
| 重驗 `deny.toml:52` 的 RUSTSEC-2026-0381 ignore 是否還需要 | 下次動 `deny.toml`，或 tokio-tungstenite 不再依賴 webpki-roots 0.26 | 先移除該行跑 `cargo deny check advisories`：通過就刪掉，失敗就更新 reason 寫明還卡在哪個 crate。2026-11-07 維運長紀錄說它「已對不到任何 crate」，但該行的 reason 寫的是仍需要 webpki-roots 0.26.11 shim，這兩種說法沒有實跑核對過 | Codex | deny.toml:52；repo-fleet-ops `docs/WORKLOG.md` 11-07 buzz 段 |
| 重評 benchmark 鎖檔與上游 CodeQL 風險 | 上游更新鎖檔／修正告警，或 fork 要執行 benchmark、變更部署暴露面 | 按既有裁決重做可達性評估；若要改來源先取得維護者決定，受影響測試通過並重查告警狀態 | Claude Opus | docs/fork/DECISIONS.md:74、86、212 |
| 重看上游 issue #8856（Windows Desktop 0.5.28 連自架 relay 持續「Can't reach the relay」） | 上游釘出根因或修正 commit，或維護者實際在 Windows 桌面重現 | 在 Windows 實機對自架 relay 驗證連線穩定（含 BUZZ_CORS_ORIGINS 含 tauri.localhost 來源）；記錄版本與對應修正 | 維護者／Codex | docs/fork/UPSTREAM_REVIEW_2026-11-02.md issue 軸；https://github.com/block/buzz/issues/8856 |
| 驗收 Hermes 發訊與 Windows 圖片流程 | 上游合併 #8643，或 Windows 使用者遇到圖片／時鐘偏差問題 | 維護者在實際桌面版驗證 Hermes 訊息抵達、圖片顯示；記錄版本與對應修正，不以瀏覽器測試取代原生結果 | 維護者 | docs/fork/DECISIONS.md「PR 軸」#8643、「Issue 軸」#8618、#8619 |

## 刻意不做
| 不做什麼 | 理由 | 什麼情況下重新考慮 |
| --- | --- | --- |
| 自行改產品 API、編輯器行為或整批改寫 benchmark 鎖檔來源 | 已有等待上游與不改來源的裁決，見 docs/fork/DECISIONS.md:74-86 | 上游合併修正，或維護者改變使用範圍與授權 |
| 自動 dismiss 繼承告警或把掃描成功當安全通過 | 掃描執行與漏洞解除是不同證據 | 有逐筆可達性評估或修補證據後再作裁決 |
| 在 fork 建立 sprig-latest 或向 block 映像庫發布 | FORK.md 的發布 guard 與既有裁決禁止 | 維護者另行授權自己的發布目標 |

## 維護方式
每週依 [上游流程](docs/fork/UPSTREAM.md) 重查水位後的 commit／PR／issue，採用前保留 FORK.md 所列修補；已有共同歷史，依目前同步紀錄處理，不改寫歷史。
依賴更新先審鎖檔與 [裁決](docs/fork/DECISIONS.md)，跑 `pwsh -NoProfile -File tools/dev_check.ps1`，產品改動再跑 TESTING.md 對應檢查；新鮮度延後不替代安全告警處理。