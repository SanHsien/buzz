# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段是 2026-10-30 依 `main` `3bfb2b541844` 與固定上游快照重查的結果；遠端 fork 與舊告警數本次未重查。

## 現況
Buzz 是可自行架設、讓人與代理共用簽章事件記錄的通訊工作區，fork 維持上游產品行為（[README](README.md)、[FORK](FORK.md)）。2026-10-30 已逐筆裁決至上游 main `6d719c680a85c98153324809988be37425fba73e`：累計 32 個 commit（6 skip、26 defer）、54 筆 PR（12 skip、42 defer）與 2 筆 issue（均 defer），沒有採用產品變更。水位為該完整 commit／PR #8699／issue #8684；最新清單沒有新增 issue，故 issue 編號不變。維護工具 gate 為 29 passed；產品同步與原生驗收尚未完成。2026-10-29 的 Dependabot 103 筆、Code scanning 161 筆未重查，不視為目前告警數；#8624 已關閉未合併，等待替代修補（[本輪裁決](docs/fork/UPSTREAM_REVIEW_2026-10-30.md)、[增量證據](docs/fork/UPSTREAM_REVIEW_2026-10-30_INCREMENT.json)、[既有裁決](docs/fork/DECISIONS.md)）。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 同步前重跑 Tauri 鎖檔 advisory 盤點 | 根 workspace 的 cargo-deny 不涵蓋桌面鎖檔 | 執行 `cargo deny --manifest-path desktop/src-tauri/Cargo.toml check advisories`，區分 vulnerability 與 unmaintained；對照既有 ignore，新增漏洞必須有修補或裁決，不擴大既有 ignore | Codex | docs/fork/DECISIONS.md:105-109 |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 同步延後變更 | 可用受影響平台／Postgres 的完整驗收環境；本批長編碼／長行拒收需符合政策的修訂或維護者明確決定 | 依固定裁決逐筆帶入，保留 FORK.md 修補與發布 guard；重跑 Tauri advisory 盤點、維護工具及受影響產品閘門；提交後檢查 CI，不能把已審查水位當成產品同步完成 | Codex | docs/fork/UPSTREAM_REVIEW_2026-10-30.md；docs/fork/UPSTREAM_REVIEW_2026-10-30.json |
| 隨上游採用編輯器與 selector 安全更新 | 取代已關閉未合併 #8624 的上游修補合併，或 typography 放寬 selector 版本且可由相容鎖檔更新解決 | 對照實際修補 commit 與依賴鏈帶入；連結貼上回歸與 desktop 型別檢查通過，對應 Dependabot 告警 state=fixed | Codex | docs/fork/UPSTREAM_REVIEW_2026-10-30.md「#8624 與路線圖」；docs/fork/DECISIONS.md |
| 隨上游遷移 rmcp、glib 與 lru 依賴鏈 | 上游完成相容遷移或依賴鏈容許修補版 | 檢查 buzz-agent 實際依賴與兩份 Cargo.lock，跑受影響 Rust／Tauri gate；移除已不需要的 advisory ignore | Codex | docs/fork/DECISIONS.md:56、78、82-86；deny.toml |
| 重評 benchmark 鎖檔與上游 CodeQL 風險 | 上游更新鎖檔／修正告警，或 fork 要執行 benchmark、變更部署暴露面 | 按既有裁決重做可達性評估；若要改來源先取得維護者決定，受影響測試通過並重查告警狀態 | Claude Opus | docs/fork/DECISIONS.md:74、86、212 |
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