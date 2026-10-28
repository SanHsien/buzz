# 路線圖

> 本 repo 後續工作的單一真相源。做完一項，就在同一個 commit 刪掉那一列；新工作只加在這裡。
> 現況段的數字是 2026-10-29 依 `main` `8c8b1f596216` 查的快照，開工前先重查 GitHub。

## 現況
Buzz 是可自行架設、讓人與代理共用簽章事件記錄的通訊工作區，fork 維持上游產品行為（[README](README.md)、[FORK](FORK.md)）。2026-10-29 `gh` 查詢顯示 CI、CodeQL、Fork tools 與 Upstream check 最近成功，但 Dependabot 仍開放 103 筆、Code scanning 161 筆，不能以工作流程成功推論安全告警已清除（2026-10-29 `gh` 查詢）。上游比較為 ahead 45／behind 4；實際採用仍須依水位與裁決，不能只看差距（2026-10-29 `gh` 查詢（上游比較）；[既有裁決](docs/fork/DECISIONS.md)）。

## 近期：可以直接動手
| 項目 | 為什麼 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 依水位審查新增上游差異 | 快照已有未同步 commit；舊版 Upstream check 成功不代表最新上游已審完 | 對照 `tools/upstream_baseline.json` 審 commit／PR／issue，核對 fork patch 清單與發布 guard；採用後維護工具 gate 及受影響 CI 通過，才推進水位 | Codex | tools/upstream_baseline.json；FORK.md；2026-10-29 `gh` 查詢 |
| 同步前重跑 Tauri 鎖檔 advisory 盤點 | 根 workspace 的 cargo-deny 不涵蓋桌面鎖檔 | 執行 `cargo deny --manifest-path desktop/src-tauri/Cargo.toml check advisories`，區分 vulnerability 與 unmaintained；對照既有 ignore，新增漏洞必須有修補或裁決，不擴大既有 ignore | Codex | docs/fork/DECISIONS.md:105-109 |

## 中期：等條件成立再做
| 項目 | 觸發條件 | 驗收方式 | 建議執行者 | 證據 |
| --- | --- | --- | --- | --- |
| 隨上游採用編輯器與 selector 安全更新 | 上游 PR #8624 合併 | 按合併 commit 帶入；連結貼上回歸與 desktop 型別檢查通過，對應 Dependabot 告警 state=fixed | Codex | docs/fork/DECISIONS.md:254 |
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