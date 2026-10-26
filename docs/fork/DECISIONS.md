# Fork 決策紀錄

## 2026-10-26 建立維護骨架

- **水位起點**：fork 建立時上游 `main` 即 `9e8c9fc`（`ahead_by 0`）。commit 水位＝`9e8c9fc`；PR／issue 水位＝8592（建立當天上游最大編號）。
- **刻意不做：水位以前的 issue 分流。** 上游約 3,682 個 open issue，逐筆分流沒有可驗證的產出。觸發條件：本 fork 開始改產品碼，或遇到具體缺陷時，針對該區域搜尋 `--state all`。
- **追蹤模式用 commit，不用 release。** 上游 tag 有 `v*`、`desktop-v*`、`mobile-v*`、`chart-v*` 等多條線，semver 單線追不全；上游 main 約每週數十個 commit，仍可逐週審。
- **README／AGENTS／CLAUDE 不改。** 這些是上游持有檔；翻轉成繁中會讓每次同步都衝突。fork 說明放 `FORK.md`。
- **Dependabot 取代 Renovate。** 上游 `renovate.json` 依賴 Renovate 應用程式，fork 沒有安裝，不會運作；本 fork 用 Dependabot（cargo、npm、github-actions、docker、pub）。`renovate.json` 保留不動。
- **依賴新鮮度只讀 npm、Cargo 與 workflow pins。** Pub（`mobile/pubspec.yaml`）、Gradle、SwiftPM、`benchmarks/` 的 pyproject 沒有對應讀取器；Dependabot 仍涵蓋 pub。觸發條件：這些宣告造成實際漏更時再加讀取器。
- **CodeQL 語言：javascript-typescript、rust、actions、python（皆 build-mode none）。** Python 只有 `benchmarks/`、`scripts/`、`docs/formal` 與本 fork 的維護工具。 Kotlin 需完整 Android 建置、Swift 需 macOS runner，成本與訊號不成比例；觸發條件：行動端出現本 fork 自己的程式。
- **不在 Windows 跑上游 CI。** 上游 Windows 只有 `windows-canary`（手動觸發）。

## 2026-10-26 上游 PR 分流

- **#8593**（`feat(media): accept audio-only AAC MP4 uploads as audio/mp4`）：draft、未合併，head `a8ec9398884d12c62c5b0a5e27f4547ca5f66597`，6 檔 +644/-54。本 fork 沒有分歧的媒體碼（`crates/buzz-media`、`buzz-relay` 與上游相同），不獨立引進。觸發條件：上游合併後經 commit 軸審查；PR 水位推進到 8593。

## 2026-10-26 依賴新鮮度：為什麼延後而不是提高下限

首次執行有 76 筆（72 個套件名）宣告落後（npm、Cargo、workflow pins）。這些宣告都在上游持有的產品檔與 workflow 裡，本 fork 沒有任何產品變更、也無法在本機建置驗證 Rust／桌面／行動端。提高下限＝改上游檔案、製造日後同步衝突，且不能消除「新鮮度紅燈」以外的任何風險。

做法：全部寫進 `.github/dependency-deferrals.json`（附 `deferredLatest` 與理由），一旦 registry 超過該版本就重新追問；不調高任何宣告下限。`Swatinem/rust-cache@<sha>` 這類無版本下限的 pin 列為 NO FLOOR（不比較）。

觸發條件：本 fork 開始自己維護產品依賴時，改為逐項升級而不是延後；或上游 Renovate 長期不動某個安全相關套件時，單獨處理。

## 2026-10-26 上游 workflow 在 fork 上的行為

`ci.yml` 對 `push main`／`pull_request` 沒有 `github.repository` 守衛，所以推送到本 fork 會跑完整的上游 CI（Rust、桌面、行動端、security），耗時長且部分步驟可能因缺 secrets 或 runner 而失敗；約 17 支其他 workflow 有守衛（docker、release、canary 等）會跳過。

處理方式：首次推送後讀實際 check runs，把「缺 secrets 造成的紅燈」與「真壞」分開記在這裡（見下方「首次 CI 結果」，推送後補）；**不停用任何 workflow**、不改上游 workflow 檔（避免同步衝突）。必要檢查（branch protection）一律不設，除非確認它真的會回報。

## 2026-10-26 安全告警

Dependabot alerts 與自動安全更新在 fork 預設關閉（API 404／disabled）。有可掃的依賴宣告，所以已於首次推送時開啟；新鮮度延後清單不替代它們。

## 2026-10-26 首次 CI 結果（推送 `2ab160a`）

我們新增的 workflow（Fork tools、Upstream check、Dependency freshness、CodeQL）全綠；上游 `helm chart`、`Graph Update` 綠，`Codex Security Review` 依守衛略過。紅燈全部來自上游 workflow 在 fork 上的環境差異或新出現的弱點，**不是本次變更造成**（產品碼與上游相同，還原本次提交不會改變它們）：

| workflow／job | 結果 | 判讀 | 處理 |
| --- | --- | --- | --- |
| CI／Security Domain（`cargo deny`） | 失敗 | 新公告 RUSTSEC-2026-0387：`crypto-bigint 0.5.5` 時間變異（建議升 0.7.6，跨大版）。公告晚於 fork 點，上游同一份 `Cargo.lock` 也會紅。 | 等上游修；沒有 cargo 工具鏈可驗證跨大版升級，不在 lock 手改。觸發：上游 commit 出現 `crypto-bigint` 升版時帶入並重跑；或 Dependabot 安全更新 PR 在 CI 綠時合併。 |
| CI／Windows Rust | 取消（45 分鐘逾時） | fork 沒有暖快取，冷編譯 workspace＋Tauri 超過上游設定的 45 分鐘；快取只在成功後才存，所以不會自己好。 | 不改上游 workflow。觸發：上游調整逾時或快取策略；或在本機驗證後手動重跑。 |
| Docker image | 失敗 | 推送目標寫死 `ghcr.io/block/buzz-*`（上游組織，fork 沒有權限）；另一關要求同 SHA 的 CI 成功。 | 預期紅，無法在 fork 修。不停用 workflow。 |
| Sprig | 失敗 | 「Update rolling release」對不存在的 `sprig-latest` release 執行 `gh release edit`（上游事先手動建立）。 | 建立 release 屬於公開發佈，需維護者決定；未建立。 |
| Dependabot 更新（vitest、markdown-it） | 失敗 | Dependabot 更新器內部錯誤（無法讀細節）；vite、zod 已成功開出 PR #1、#2。 | 觀察；PR 在 CI 綠且審查後才合併。 |

Dependabot alerts 與自動安全更新已於推送時開啟。branch protection 不設必要檢查（沒有任何一個會穩定回報成功）。
