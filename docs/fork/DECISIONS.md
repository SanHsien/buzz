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
| CI／Security Domain（`cargo deny`） | 失敗 | 新公告 RUSTSEC-2026-0387：`crypto-bigint 0.5.5` 時間變異（建議升 0.7.6，跨大版）。公告（2026-10-23 通報、10-24 收錄）晚於 fork 點與上游同 SHA 的綠燈，上游同一份 `Cargo.lock` 預期也會紅（上游公告後尚無新 CI run，未實證）。 | 依賴鏈 `buzz-push-gateway` → `p256 0.13.2` → `elliptic-curve`／`ecdsa`／`primeorder` → `crypto-bigint 0.5.5`；升到 0.7.x 要在 Manifest 升 p256 大版並可能改 push-gateway API，`cargo update -p` 做不到，本機也沒有 cargo 工具鏈可驗證。替代做法是在 `deny.toml` 加帶理由的 ignore（上游處理 RUSTSEC-2026-0381 的方式），需維護者決定。觸發：上游升 p256 時帶入並重跑。 |
| CI／Windows Rust | 取消（45 分鐘逾時） | fork 沒有暖快取，冷編譯 workspace＋Tauri 超過上游設定的 45 分鐘；快取只在成功後才存，所以不會自己好。 | 不改上游 workflow。觸發：上游調整逾時或快取策略；或在本機驗證後手動重跑。 |
| Docker image | 失敗 | 推送目標寫死上游組織的 `ghcr.io/block/buzz`（relay 映像）與 `ghcr.io/block/buzz-push-gateway`，fork 沒有權限（permission_denied）；另一關要求同 SHA 的 CI 成功。 | 預期紅，無法在 fork 修。不停用 workflow。 |
| Sprig | 失敗 | 「Update rolling release」對不存在的 `sprig-latest` release 執行 `gh release edit`（上游事先手動建立）。 | 建立 release 屬於公開發佈，需維護者決定；未建立。 |
| Dependabot 更新（vitest、markdown-it） | 失敗 | Dependabot 更新器內部錯誤（無法讀細節）；vite、zod 已成功開出 PR #1、#2。 | 觀察；PR 在 CI 綠且審查後才合併。 |

Dependabot alerts 與自動安全更新已於推送時開啟。branch protection 不設必要檢查（沒有任何一個會穩定回報成功）。

## 2026-10-26 讓上游遺留的紅燈變綠（本 fork 對上游檔案的修補）

這是第一次改上游持有檔，因為維護者要求不留紅燈且不得停用 workflow。每一處都是最小修補，加上註解標明 `fork patch`，同步上游時若衝突以上游為準再重做。

1. **`deny.toml`＋`Cargo.lock`（cargo-deny）**：
   - `tokio` 1.52.3 → 1.54.1（RUSTSEC-2026-0386）與 `lru` 0.18.0 → 0.18.2（iroh-relay 帶入的那一份，RUSTSEC-2026-0253 的修補版），皆 semver 相容，由 `cargo update` 產生。重新解析也順帶把 Windows 專用的 `windows-sys`／`windows-link` 依賴改指到 lock 內已有的版本（anstream、rustix、tempfile 等），只影響 Windows target，`--locked` 與 `cargo check` 通過。
   - RUSTSEC-2026-0387（`crypto-bigint 0.5.5`，修補版只有 >=0.7.6，鏈在 `p256 0.13`）與 RUSTSEC-2026-0253（剩下的 `lru 0.16.4`：workspace 的 `lru = "0.16"` 與 `launchdarkly-server-sdk =3.2.0` 的 `lru ^0.16`，修補版 >=0.18.2）無法由相容升級解決，加 `ignore` 並附影響評估：push-gateway 只用 p256 解析公鑰、不處理祕密整數；`lru` 只有在鍵的 `Drop` 會 panic 且 `catch_unwind` 時才不安全，buzz 自己的鍵是 `String`（`nip_fi_resolver.rs`）；launchdarkly 3.2.0 內部（`events/dispatcher.rs`）鍵型別也是 `String`。觸發條件寫在 `deny.toml` 註解：p256 升到 crypto-bigint 0.7 線；workspace lru 與 launchdarkly 都升到 lru >= 0.18.2。
   - 另一個選項「把 workspace `lru` 升到 0.18」被放棄：launchdarkly 仍會留下 0.16.4，升級沒有消除告警，只增加產品碼風險。
2. **`docker.yml`**：非 `block` owner 時只 build、不 push、不寫 buildcache、不跑 qualify／merge，因為映像名固定在 `ghcr.io/block/*`（沒有權限）。保留 build 的驗證價值。若日後想推到自己的 ghcr，需要設 `vars.GHCR_IMAGE` 並處理 push-gateway 的寫死名稱，目前不做。
3. **`sprig.yml`**：發佈 job 只在 `block` owner 執行。維護主管（代轉維護者）曾表示可建立 fork 自己的 `sprig-latest` release，但那會公開發佈 CI 建置的二進位檔，屬於需維護者明確同意的動作；改採「fork 只 build」讓 workflow 轉綠，未建立 release。

4. **`sprig-image.yml`**：與 `docker.yml` 相同的 owner 閘門（映像 `ghcr.io/block/buzz-sprig`，fork 沒有權限）。8398c4e 的 run 證實 `permission_denied`。
5. **`codeql.yml`（本 fork 自己的檔案）**：`timeout-minutes` 30 → 90。8398c4e 的 rust 掃描在 30 分鐘被取消（冷快取、約 40 個 crate 的 workspace）；先前 `2ab160a` 的同一掃描曾在時限內完成，所以是邊界而非壞掉。
6. **Desktop Tauri (mesh) 的「Install Tauri dependencies (Linux)」失敗**：該步驟是 `apt-get install`（有重試腳本），日誌取不到錯誤細節，推測為套件鏡像暫時性問題（未證實），已重跑失敗的 job 一次確認；結果見下方。
