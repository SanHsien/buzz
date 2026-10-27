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
| CI／Windows Rust | 取消（45 分鐘逾時） | fork 沒有暖快取，冷編譯 workspace＋Tauri 超過上游設定的 45 分鐘；快取只在成功後才存，所以不會自己好。 | 已由下方第 7 點修補（非 block owner 逾時 90 分鐘）。 |
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
7. **`_ci-rust.yml` 的 Windows Rust 逾時**：非 `block` owner 時 45 → 90 分鐘。fork 沒有暖快取，冷編譯 workspace＋Tauri 在 `2ab160a`、`6b9d953` 兩次於 45 分鐘被取消；`block` owner 維持 45。
8. **Desktop Smoke E2E 的兩個測試（`video-attachment.spec.ts:1469`、`voice-note.spec.ts:906`）在 `6b9d953` 失敗**：`8398c4e` 的 CI 這兩個測試通過（該次失敗的只有 Tauri 依賴安裝與其彙總 job），且 `8398c4e` 到 `6b9d953` 之間沒有產品碼差異（只動 workflow 與文件）；`abc369f` 亦曾通過，但 `abc369f` 之後的 `8398c4e` 有 `Cargo.lock` 更新（tokio、lru 等），所以不能以此證明與 lock 更新無關。判斷為共用 runner 負載下的逾時型不穩定（當時同時有兩個 Dependabot PR 的 CI 在跑），已重跑失敗 job 一次，結果見下方；若反覆失敗再視為真問題處理。

## 2026-10-26 Dependabot 安全告警（第一批：相容的鎖檔更新）

開啟 Dependabot alerts 後 fork 顯示約 50 組告警（上游遺留，產品碼與上游相同）。原則：只用工具產生的鎖檔更新（`cargo update -p`、`pnpm update --lockfile-only`、`uv lock --upgrade-package`），**不調高任何 `package.json`／`Cargo.toml`／`pyproject.toml` 的宣告下限**；pnpm 不覆寫內建的 `minimumReleaseAge` 預設（repo 沒有另行設定；Renovate 的 3 天政策不適用於手動 `pnpm update`，其中 seroval 1.7.2、baseline-browser-mapping 2.11.32 發佈未滿 3 天）。

已處理：
- **Rust**（兩份 lock 都有 `hickory-resolver`／`hickory-proto`／`hickory-net` 0.26.1→0.26.3；`xxhash-rust` 0.8.15→0.8.19、`cmov` 0.5.3→0.5.4 只在根目錄 `Cargo.lock`）。重新解析也把 Windows 專用的 `windows-sys` 等依賴改指到 lock 內已有的版本。`cargo deny check` 四項 ok；`cargo check -p buzz-relay -p buzz-relay-mesh -p buzz-push-gateway -p buzz-agent -p buzz-acp -p buzz-core --locked` 通過。Tauri 端沒有本機編譯，交給 CI 的 Desktop Tauri。
- **npm**（`pnpm-lock.yaml`）：`markdown-it` 14.3.3、`seroval` 1.7.2、`vite` 8.3.5、`zod` 4.6.7、`nanoid` 3.3.20、`postcss` 8.5.31、`browserslist` 4.29.4、`baseline-browser-mapping`、`@babel/core` 7.29.7；vite 8.0→8.3 是 minor 升級，連帶 rolldown 1.0→1.2、新增 lightningcss 與其平台套件，實際打包行為會變，以 CI 的 build／E2E 為準。`pnpm install --frozen-lockfile` 與 `pnpm typecheck`、`pnpm check` 通過；desktop 單元測試 6833/6834，唯一失敗的 `useDocumentVisible.test.mjs`「focused polling pauses on blur…」在更新前的 lock 上同樣失敗（本機 Windows 環境），與本次無關。推送後待辦：確認 Dependabot PR #1（vite）、#2（zod）被取代後關閉。
- **pip**（`benchmarks/harbor-buzz-orchestra/uv.lock`、`benchmarks/harbor-buzz-orchestra/testbed/uv.lock`，約 20 組告警含 3 個 critical：PyJWT、anyio、certifi）：**本批不處理**。上游鎖檔的來源全指向 Block 內部 Artifactory（`global.block-artifacts.com`），fork 無法使用；`uv lock` 會把所有套件來源整批改成 `pypi.org` 並重寫約 3.5k 行（實測），之後每次同步上游這兩個檔案都會全檔衝突，而且 litellm 會一次跳到發佈才一天的 1.106.4（連帶新增 boto3 等相依）。這兩個目錄是 benchmark 工具、不隨產品發行；CI 的 `benchmark-harbor.yml` 只在 `benchmarks/harbor-buzz-orchestra/**` 變更時觸發，且以 `pip install -e ".[dev]"` 依 `pyproject.toml` 解析、不讀 `uv.lock`。告警的實際暴露面只剩有人在本機用這兩份 lock 跑 `uv sync`，而鎖檔指向的內部 Artifactory 對 fork 本來就連不上。觸發條件：維護者要實際執行 benchmark 時，或決定接受來源改用 pypi.org 並以 `--upgrade-package '<pkg>==<最低修補版>'` 逐一鎖到修補版（litellm 等滿 3 天）。

刻意不處理（附理由與觸發條件）：
- **`@tiptap/*`＋`prosemirror-*` 家族**（`@tiptap/core`、`prosemirror-view` 告警）：整個家族升到 3.32.0 會讓 5 個連結貼上測試失敗（`composerLinkPastePipeline.test.mjs`：「expected Link's onCreate to register the buzz protocol with linkify」），需要改產品碼；只升單一套件則 `prosemirror-model` 出現兩份型別而 `tsc` 失敗。觸發：上游自己升 tiptap 時帶入。
- **`rmcp`**（high／medium）：有漏洞的 1.8.0 來自 `crates/buzz-agent/Cargo.toml` 自己宣告的 `rmcp = { version = "1", ... }`（兩份 lock 都有）；根目錄 `[workspace.dependencies]` 裡的 `rmcp` 沒有任何 crate 繼承。修補版是 2.x／3.x，要把 buzz-agent 的 client／transport-child-process 用法遷移到 3.x（產品碼 API 變動）。Dependabot PR #3（只改那行沒人用的 workspace 宣告與 Tauri lock 的 Windows 依賴指向）因此關閉，並未修掉告警。觸發：上游遷移 buzz-agent 到 rmcp 3.x。
- **`glib` 0.18.5**（Tauri lock，medium）：修補版 0.20.0，被 gtk3-rs 一整組擋住；觸發：Tauri／gtk 升版。
- **`@vitest/mocker`**、**`postcss-selector-parser`**：目前可解析的版本低於告警的修補版（受 pnpm 發佈時間政策或相依範圍限制），隔日重跑 `pnpm update` 再試；已在報告列出。

## 2026-10-26 維護者決定：剩餘告警的處理（經維護主管代決）

下列項目**保持現狀、告警保持開啟、不 dismiss**；每項附觸發條件，條件成立才回頭處理。

1. **pip benchmarks 告警**（`benchmarks/harbor-buzz-orchestra/uv.lock`、`.../testbed/uv.lock`，含 PyJWT、anyio、certifi 三個 critical）：不重寫 `uv.lock`。來源改成 pypi.org 會整批重寫、每次同步上游都全檔衝突；benchmarks 不在 fork 以 `uv.lock` 執行、不隨產品發佈，CI 的 benchmark-harbor 亦以 pip 依 `pyproject.toml` 解析、不讀 `uv.lock`。記為**已評估的風險**。觸發條件：上游更新那兩份鎖檔（隨同步帶入），或 fork 開始執行 benchmarks。
2. **rmcp、`@tiptap/*`＋`prosemirror-*`**：fork 不改產品碼（會與上游分岔）。等上游升級後隨同步帶入。觸發條件：上游升級（rmcp 為上游把 buzz-agent 遷移到 3.x），或公告確認影響 fork 實際使用的路徑。
3. **`sprig-latest` release**：不建立（不在 fork 公開發佈 CI 建置的二進位檔）；Sprig 發佈 job 維持只在上游 owner 執行。觸發條件：維護者決定要在 fork 發佈二進位檔。
4. **`glib` 0.18.5（Tauri）、`@vitest/mocker`、`postcss-selector-parser`**：目前沒有可相容的修補版，或受 pnpm 內建發佈時間預設限制。觸發條件：隔日以 `pnpm update <pkg> -r --depth Infinity --lockfile-only` 重試後兩者（尚未重試）；`glib` 待 Tauri／gtk 升版。重試仍無法解析就維持現狀，下次同步上游時再試。

## 2026-10-27 深度掃描（只掃 fork 自己加的東西）

範圍：`docs/fork/`、`tools/`＋`tests/fork`、fork 新增與修補的 workflow、`deny.toml` 的 ignore、fork 對鎖檔與產品測試碼的改動。上游原封不動的產品碼不在範圍。每個缺陷先寫修前會失敗的測試再修，一個缺陷一個 commit。

已修（測試都在 `tests/fork/test_fork_tools.py`）：

1. **`sprig.yml` 的 `publish-tag` 沒有 owner 守衛。** 在 fork 推 `sprig-v*` tag 會用 CI 建置的二進位檔建立公開 release，與上方「Sprig 發佈 job 維持只在上游 owner 執行」的決定相反（只有滾動 release 的 `publish` 有守衛）。加上守衛；測試檢查所有發佈 workflow 裡有寫入權限的 job 都帶守衛、所有能 push 的 build-push 步驟的 `push=` 都帶守衛。
2. **新鮮度檢查把未加註解的 SHA pin 讀成版本下限。** `actions/checkout@34e11487…` 的下限變成 `34`（永遠不過期）、`azure/setup-helm@1a275c3b…` 變成 `1`（永遠過期）。三個 pin 受影響（`push-gateway-helm-chart.yml`）。改為 NO FLOOR。
3. **上游檢查的 `git`／`gh` 呼叫沒有逾時**，網路卡住會拖到 runner 的 10 分鐘上限且不產生報告；`git` 不存在時以裸 traceback 結束。逾時與 `OSError` 現在是 `UpstreamCheckError`（報告「Check failed」、exit 2），`gh` 逾時回 `None`（「未檢查」，不是「無新項目」）。
4. **兩支工具在無法編碼報告的主控台上崩潰**（Windows 無 `PYTHONUTF8` 的 cp1252／cp950：繁中狀態行或 issue 標題裡的 emoji → `UnicodeEncodeError`），發生在檔案寫完之後，exit 1 與 `--strict` 的「上游有更新」同碼。stdout 改為 `errors="replace"`。
5. **延後（deferral）的過期判斷以「已審視版本」的精度截斷**：唯一的兩段版本 `openai/codex-action "1.13"` 在 1.13.4 仍延後，與「registry 超過該版本就自動過期」不符。改為全精度比較；`deferredLatest` 無法解析（如 `"latest"`）的項目永遠不會過期，載入時改為忽略。
6. **Cargo workspace `members` 的 glob 被當字面路徑**，`crates/*` 之類的成員會無聲地從報告消失。改為展開並尊重 `exclude`；目前的明列清單解析結果不變（38 份）。
7. **registry 回應被截斷（`IncompleteRead`，不是 `OSError`）會讓整份新鮮度報告中止**，改為一筆 CHECK FAILED。
8. **`FORK.md`／`NOTICE.md` 說產品碼與上游逐位元組相同／未修改**，但 fork 已修補四個 workflow、加兩條 `deny.toml` ignore、升級三份鎖檔、動過 `buzz-dev-mcp` 的測試碼。補上「上游持有檔的修補」表，`deny.toml` 加 `fork patch (SanHsien/buzz)` 標記，測試要求帶標記的檔案必須列在 `FORK.md`。
9. **Tauri 鎖檔沒跟上 `cargo-deny` 的修補。** CI 的 `cargo-deny check` 只讀根 workspace，所以 tokio 1.54.1（RUSTSEC-2026-0386）、lru 0.18.2（0253）只進了根 `Cargo.lock`；`desktop/src-tauri/Cargo.lock`（桌面 app 實際用的依賴集）仍是 tokio 1.52.3、lru 0.18.1、h2 0.4.15（0258）、rtrb 0.3.4（0274）。以 `cargo update -p <crate> --precise` 升到 tokio 1.54.1、lru 0.18.2、h2 0.4.16、rtrb 0.3.5（相容升級、不動 manifest）；`cargo deny --manifest-path desktop/src-tauri/Cargo.toml check advisories` 修後沒有 vulnerability／unsound 條目。本機只能 `cargo check --locked -p tokio -p h2 -p rtrb` 通過（完整的 Tauri crate 在本機卡在 `opusic-sys` 需要 cmake），完整編譯交給 CI 的 Desktop Tauri。`cargo update -p tokio` 重新解析時，順帶把 arboard 3.6.1 的 `windows-sys` 由 0.60.2 換成 0.59.0（arboard 允許 `>=0.52.0, <0.61.0`，兩版原本都在鎖檔裡，只影響 Windows），這是附帶變動，不是刻意升降版。

觀察（上游的東西，不改；附觸發條件）：

- **Tauri 鎖檔沒有任何 CI 的安全掃描**（Dependabot 只對有 GHSA 的告警開單）。同一個 `cargo deny` 掃 Tauri 鎖檔還會報 `unic-*`、`mach`、`proc-macro-error` 的 unmaintained。要讓 CI 掃它需要另一份帶 ignore 的設定，屬於上游 CI 結構。觸發：維護者要 Tauri 鎖檔進 CI，或下次同步上游時順手重跑上面那條指令。
- **`str_replace.rs`、`view_image.rs` 的測試 `make_state` 沒拿 `lock_shell_env()`**（`e3561ee` 只補了 `shell.rs`、`read_file.rs`）。它們不依賴 shell 解析結果，沒有已知失敗。觸發：這兩處的測試在 Windows 出現不穩定。
- **`helm-chart.yml`（`chart-v*` tag）、`push-gateway-helm-chart.yml`（`push-chart-v*` tag）、`staging-dev-relay-image.yml`（手動）沒有 owner 守衛**，在 fork 推 tag 或手動觸發會嘗試推 `ghcr.io/block/*`，結果是權限失敗（紅燈）而不是發佈。fork 不推這些 tag。觸發：fork 開始推 tag，或需要這些 workflow 轉綠。

## 2026-10-27 `10aedc7` 兩條紅燈的原因與處理

### Dependency freshness

本機重現（`GH_TOKEN=… python tools/check_dependency_freshness.py`）與 CI 日誌一致：報告裡**只有一列**需要處理（`REVIEW UPDATE`），另有四列 `NO FLOOR`（未註解的 SHA pin，設計上不比較，不算紅燈）。深度掃描修的兩件事（全精度過期比較、SHA 不當下限）沒有讓被遮住的項目浮出來：

- **`openai/codex-action` 沒有過期。** 宣告 `v1.12`，延後 `1.13`；該 repo 的 tag 最新就是 `v1.13`（沒有 `v1.13.x` tag，`releases/latest` 也是 404），registry 沒有超過延後的版本，狀態維持 `DEFERRED at 1.13`。
- **唯一的 `REVIEW UPDATE`：`taiki-e/install-action`**（`v2.79.15`，`_ci-relay.yml`／`_ci-rust.yml`／`sprig.yml` 共六處）。10-26 的延後停在 2.87.31，2.87.32（10-26T15:24Z）發佈後自動過期——這是機制照設計運作，不是新缺陷。
  - **沒有升級。** 六處 pin 是上游持有，上游 `main`（`0e36dbc`）仍是同一個 SHA `0fd4636…`；`v2.79.15…v2.87.32` 之間 914 個 commit，動到 `action.yml`、`main.sh`，而 workflow 要的是精確版本工具（`cargo-nextest@0.9.136`、`cross@0.2.5`），只有推送後 fork 自己的 CI 跑得出來，本機無法驗證。改 `tool` 以外的上游 workflow 檔也會與上游下一次 bump 衝突。
  - **做法：** `deferredLatest` 改 2.87.32，理由寫明為什麼不升與觸發條件（上游 bump 時隨同步帶入；或 fork 開始自己維護 CI workflow）。該 action 約每 2–5 天一個 patch（v2.87.x 已 33 版），這個條目還會再過期；每次過期是「重新追問」，不是新決定。下限沒有調高。
- **第二個紅燈來源：開著的 Dependabot PR #5。** `dependency-freshness.yml` 把「有任何開著的 Dependabot PR」當作需要處理。#5 是 `certifi 2026.6.17 → 2026.10.18`，只改 `benchmarks/harbor-buzz-orchestra/testbed/uv.lock`，**+1672/−1672**，其中 1645 行是把來源從 `global.block-artifacts.com` 改成 `pypi.org`——正是 2026-10-26「維護者決定」第 1 條拒絕的整批重寫（`revision` 也從 3 變 5）。依該決定**不合併**；PR 應以註明該決定的留言關閉。關閉是對 fork 遠端的寫入，本輪未做（見回報）。注意：只要 pip 告警還在、自動安全更新開著，Dependabot 之後可能針對同一份鎖檔再開別的套件的 PR，紅燈會再出現；要根治需維護者決定：關掉 uv 的自動安全更新，或接受鎖檔來源改成 pypi.org（原決定的觸發條件）。

### Upstream check

- 首次失敗的 run（attempt 1）報告是「12 commits＋PR／issue **未檢查**」——`gh` 在 runner 上列舉失敗，`collect_new_tickets` 回 `None`，工具照設計報「未檢查」而不是「無新項目」。同一個 commit 重跑（attempt 2）PR／issue 都列舉成功（14 筆 PR、1 筆 issue）；本機兩個 `gh … list --limit 1000` 各約 7 秒、都成功。判斷為 runner 上的暫時性 `gh` 失敗（原因未知：`gh` 的 stderr 沒被保留）。觸發條件：再發生一次就讓工具把 `gh` 的 stderr 寫進報告。
- 紅燈本身是真的：上游在水位之後確實有東西。以下為審查。

## 2026-10-27 上游審查（commit `9e8c9fc → 209fcd2`；PR 8593 → 8610；issue 8592 → 8597）

**審查前提：** 本 fork 與水位 `9e8c9fc` 之間，產品目錄只有 7 個檔案不同（`git diff 9e8c9fc HEAD --stat -- crates desktop mobile web admin-web deploy`：`buzz-dev-mcp` 兩個測試檔、`desktop/src-tauri/Cargo.lock`，以及本輪帶入的 push-gateway 四檔）。判準六的結構性論證在此成立：上游這 13 個 commit 與 fork 的分歧處幾乎不重疊（見下），沒有「fork 專屬缺陷」需要另外移植。

**上游 CI 狀態（唯讀查 `0e36dbc` 的 check runs；之後的 `209fcd2` 只是 mobile 兩檔）：** 失敗三項——`Desktop`／`Desktop Domain / Desktop`／`Qualify relay image source`。`Desktop` 失敗的 job 是 `Desktop Tauri (core／compiled-flags)` 的「Install Tauri dependencies (Linux)」（`apt-get`），與本 fork 在 2026-10-26 見到的同一步驟（第 6 點）相同，屬 runner 環境問題，不是程式碼回歸；`a3a47e6`、`ab73cd9` 兩個 commit 上 `PostgreSQL Tests` 曾紅，tip 上已綠。

### Commit 軸（13 筆；審查途中上游又進了 `209fcd2`，連同 #8609、#8610 一併納入）

| commit | 內容 | 規模 | 與 fork 的重疊 | 處理 |
| --- | --- | --- | --- | --- |
| `d676c7b` #8592 | `p256` 0.13→0.14（RUSTSEC-2026-0387，crypto-bigint 0.5.5→0.7.9） | 5 檔 +98/−111 | **有**：fork 為此加了 `deny.toml` ignore | **帶入**（`3e0e7c8`，逐字 cherry-pick，`Cargo.lock` 無衝突）；移除 fork 的 0387 ignore；觸發條件（「p256 升到 crypto-bigint 0.7 線」）已成立。`cargo deny check`：advisories ok；`cargo check -p buzz-push-gateway --locked` 通過；該 crate 的測試因 dev-dependency 的 vendored OpenSSL 在本機（無 native perl／nmake）建不起來，留給 CI。 |
| `7ce4224` #8503 | mesh 過期的 peer 記錄與開機儀器 | 11 檔 +1018/−57 | 只有 `Cargo.lock`（自動合併）；`buzz-relay-mesh/Cargo.toml` 新增 `metrics`／`metrics-util`（workspace 已有） | 不獨立帶入，隨同步合併 |
| `4250014` #8520 | 使用者刪除改走已存檔的階段轉換 | 34 檔 +3732/−170 | 無 | 同上 |
| `4c7ba3b` #8567 | 文件：RELEASING.md 移除 NIP-FI migration gate | 1 檔 −39 | 無 | 同上 |
| `d0dee1c` #8575 | relay：一個 kind:9000 加入多人 | 11 檔 +1404/−200 | 無（動 `_ci-relay.yml` 三行測試清單，fork 未改該檔） | 同上 |
| `369ffa0` #8401 | relay：驗證 NIP-FI agent token | 36 檔 +3630/−548 | 無 | 同上 |
| `d727033` #8548 | 文件／提示：memory 當索引、來源標註 | 3 檔 +23/−4 | 無 | 同上 |
| `b8b1ab5` #8524 | push：避免空的投遞 claim | 5 檔 +584/−24 | 無 | 同上 |
| `d090ac2` #8490 | mobile：減少閒置與恢復時的同步 | 9 檔 +403/−38 | 無（mobile，fork 不建置） | 同上 |
| `ab73cd9` #8580 | mobile：在社群同步前還原快取的頻道 | 24 檔 +2424/−405 | 無 | 同上 |
| `a3a47e6` #8579 | relay：unlisted 頻道設定 | 25 檔 +1730/−101 | 無 | 同上 |
| `0e36dbc` #8495 | db：讀取連線池保溫、移除 pre-acquire ping | 8 檔 +863/−186 | 無 | 同上 |
| `209fcd2` #8608 | mobile：建立 push 訂閱時忽略不相干的靜音設定 | 2 檔 +22/−4 | 無（mobile） | 同上；它是 PR #8608 的 squash，新增行與我們審過的 PR head `69a6df7` 逐行相同 |

**「隨同步合併」的依據（可重跑）：** 在 `3e0e7c8` 之上 `git merge --no-commit --no-ff <上游 0e36dbc>` 自動合併完成、零衝突（`Cargo.lock` 也自動合併），且合併後 `cargo metadata --locked` 通過；之後 `git merge --abort`（當時上游 tip 是 `0e36dbc`；之後多的 `209fcd2` 只動兩個 mobile 檔，不與任何 fork 修補重疊）。**水位推進不等於產品碼已同步**：本檢查的「behind」是相對水位算的，推進後會顯示 behind 0，但產品碼實際仍落後這 12 個 commit（除 `d676c7b` 外的全部）。它們在此明列：合併的時機由維護者決定；建議先推送本輪三個 commit、看 CI 結果，再單獨合併上游（出現新紅燈才能歸因）。合併後新鮮度報告會多出新宣告的列（例如 `metrics`），屆時另行處理。

**隱藏內容掃描（判準八）：** 13 個 commit 的完整 diff（`9e8c9fc..209fcd2`，157＋2 檔）：行內長串空白後接內容、`eval(`／`new Function(`、`globalThis`／`global.require`、≥120 字元 base64／hex、零寬與雙向控制字元，皆無命中；超過 400 字元的新增行逐筆看過，都是文件表格（`NOSTR.md`、`NIP-FI`）、CLI help 字串、`Justfile` 的 nextest 篩選式、`base_prompt.md` 的提示文字與一則 Rust 文件註解。

### PR 軸（16 筆新項目；15 筆 open，#8608 已合併成 `209fcd2`，無已關閉未合併）

全部：**不引進，未合併前不審內容細節，上游合併後經 commit 軸審查**（同 #8593 的做法）；PR 水位推進到 8610。每筆取**審查當時**的 head 並掃描 diff（表中 head 是審查時的值；之後被 force-push 的見各列註記）（掃描方式同上；`+` 前綴加縮排造成的「長空白」誤判已排除）：

| PR | head | 規模 | 隱藏內容 | 與 fork 的關係 |
| --- | --- | --- | --- | --- |
| #8594 auto-join 預設頻道 | `502d016` | 18 檔 +1286/−86 | 無（最長新增行是 `NOSTR.md` 表格） | relay／db，fork 無分歧碼 |
| #8595 invites 走原生網路 | `3ed2df1` | 8 檔 +164/−137 | 無（`globalThis.window` 僅在 `invites.test.mjs` 當測試替身） | desktop |
| #8596 影片縮小再上傳 | `daff931` | 1 檔 +105/−12 | 無 | desktop |
| #8598 Rust 1.98.1（macOS 27） | `8b28f5f` | 29 檔 +85/−73 | 無 | **動 `_ci-rust.yml`、`release.yml`、`windows-canary.yml`、Dockerfile**：與 fork 的 `_ci-rust.yml` Windows 逾時修補同檔。觸發：上游合併時重驗該逾時修補是否還在、`docker.yml` 守衛是否衝突 |
| #8599 mobile QR 優先 onboarding | `37194be` | 13 檔 +563/−263 | 無 | mobile。**審查期間 head 換了三次：`0a4d964`（12 檔 +302/−101）→ `12c7d59`（13 檔 +563/−263）→ `37194be`（同規模）**；三個版本都掃過、沒有隱藏內容，以最後的 head 為準。主管覆核時（2026-10-27）head 已再換成 `86e250a`，未掃；不引進，上游合併後經 commit 軸審查 |
| #8600 draft：邀請同意移出瀏覽器 | `32767f9` | 2 檔 +60/−47 | 無 | web |
| #8601 邀請 handoff 的原生同意 | `a1d1703` | 16 檔 +848/−135 | 無（`globalThis.fetch`／`__TAURI_INTERNALS__` 僅在 `useClaimInvite.jsdom-test.mjs` 當測試替身） | desktop |
| #8602 專案卡片可刪 repository（#8597） | `810b5a3` | 9 檔 +527/−24 | 無 | desktop；對應下方 issue #8597 |
| #8603 持續重試失敗的 agent runtime 對帳（#8591） | `45625d4` | 4 檔 +100/−10 | 無 | desktop |
| #8604 保留 `child_pid`、認得 `codex` binary（#8590） | `a9695aa` | 3 檔 +16/−3 | 無 | `kill_process_group` 為 Unix 路徑，非 Unix 仍 fallback `start_kill()`，不是 Windows 專屬修正 |
| #8605 為假刪除流程產生使用者社群清單 | `987af1d` | 25 檔 +1405/−106 | 無 | admin／db。審查期間 head 由 `8b89997` 換成 `987af1d`（規模相同，疑似 rebase）；兩版都掃過 |
| #8606 draft：kind:9000 與成員寫入同一交易（#8575 的後續） | `d18e88f` | 5 檔 +425/−55 | 無（最長新增行是 `NOSTR.md` 表格） | relay |
| #8607 mobile 批次初始已讀種子 | `6a232ed` | 6 檔 +221/−61 | 無 | mobile |
| #8608 mobile 忽略不相干的靜音設定 | `69a6df7` | 2 檔 +22/−4 | 無 | mobile；**已合併為 `209fcd2`**，見 commit 軸 |
| #8609 push：跨版本接受正規 channel UUID | `0f5acd4` | 9 檔 +156/−10 | 無（最長新增行是 `NIP-PL.md` 表格） | relay／mobile |
| #8610 draft：把 push 設定失敗與 app 渲染隔離 | `e9a1068` | 8 檔 +573/−47 | 無 | mobile。主管覆核時（2026-10-27）head 已換成 `629c2c6`，未掃；不引進，上游合併後經 commit 軸審查 |

### Issue 軸（1 筆新項目）

- **#8597**（open）：桌面端刪除專案後，預設 repository 留下且無法刪除。對應 PR #8602。fork 的 `desktop/src` 與上游相同（`git diff 9e8c9fc HEAD -- desktop/src` 無輸出），所以這是 fork 同樣帶有的上游缺陷，不是 fork 專屬。不處理（不改產品碼）；觸發：上游合併 #8602。

### 水位

`tools/upstream_baseline.json`：`reviewed_through` → `209fcd21725b8728fed8b14dca1636018d175458`，`reviewed_pr_through` → 8610，`reviewed_issue_through` → 8597，`reviewed_date` → 2026-10-27。

## 2026-10-27 把上游 `209fcd2` 併進產品碼

上一節審查時產品碼只帶入 `d676c7b`（`3e0e7c8`），其餘 12 個 commit 明列為「隨同步合併」。本節是那次合併。fork 沒有壓縮過，與上游共同祖先是水位 `9e8c9fc`，所以用一般的 `git merge 209fcd2`（`--no-ff`），不是 cherry-pick。

- **結果：零衝突。** `Cargo.lock` 自動合併，相對合併前只多兩行（`buzz-relay-mesh` 的 `metrics`、`metrics-util`，workspace 本來就有這兩個 crate）。上游這 13 個 commit 沒有動任何 fork 修補檔：`deny.toml`、`docker.yml`、`sprig.yml`、`sprig-image.yml`、`_ci-rust.yml`、`desktop/src-tauri/Cargo.lock`、`pnpm-lock.yaml`、`crates/buzz-dev-mcp`；`FORK.md` 表中帶 `fork patch` 標記的檔案合併前後 `git diff` 為空。唯一動到的 workflow 是 `_ci-relay.yml`（三行測試清單，fork 未改）。
- **`d676c7b` 與 `3e0e7c8` 內容相同**，合併時沒有產生變動。
- **驗證（本機，`cargo` 在 `~/.cargo/bin`）：** `cargo deny check` 四項 ok（唯一與 advisory 相關的警告是上游自己的 `RUSTSEC-2026-0381` ignore「未命中」，合併前後鎖檔在該鏈沒有差異）；`cargo check --workspace --locked --exclude buzz-audio-client` 通過；`cargo metadata --locked` 對 `desktop/src-tauri` 通過，`cargo deny --manifest-path desktop/src-tauri/Cargo.toml check advisories` 沒有 vulnerability／unsound 條目，只有上一節已記的 `unic-*`／`mach`／`proc-macro-error` unmaintained。`buzz-audio-client` 排除的原因：它依賴 `opus` → `opusic-sys`，build script 需要 `cmake`，本機沒有（工作區內沒有其他 crate 依賴它，與本次合併無關；交給 CI）。未跑 Rust 測試（push-gateway 的測試依賴 vendored OpenSSL，本機建不起來；其餘交給 CI）。
- **新鮮度：** 合併前後的報告逐位元組相同（無新增列、無新的 `REVIEW UPDATE`）。`metrics` 系列在 workspace 本來就有宣告，狀態 OK。
- **上游已經又前進：** 審查與本合併都停在 `209fcd2`；唯讀 `ls-remote` 看到上游 `main` 目前是 `a38fedb`。水位**維持** `209fcd2`，之後的 commit 由下次 `upstream-check` 列出。
- **建議：** 推送後看 CI，出現的新紅燈（尤其 Desktop Tauri、Rust、Docker／Qualify relay image）要與上一節記的「上游 `0e36dbc` 的 check runs」基準（Desktop Tauri 的 apt-get 步驟、Qualify relay image source 已紅）比對再歸因。

## 2026-10-28 深度掃描第二輪（只掃 fork 自己加的東西）

範圍同上一輪：`git diff 209fcd2..main` 的 26 個檔案。`tools/check_upstream_updates.py` 是艦隊共用的正本（`SanHsien/repo-fleet-ops` `tools/canonical`），缺陷要回報正本、不在這裡改。

已修（測試在 `tests/fork/test_fork_tools.py`，每個都先確認修前失敗）：

1. **浮動 tag 加了非版本的註解就失去下限。** `uses: owner/repo@v6 # matches the runner image` 從註解取版本、取不到，列成 NO FLOOR，`v6` 從此不比較。現在只有註解本身是版本時才用註解。目前樹內沒有這種寫法（零列受影響）。
2. **`[target.'cfg(...)'.dev-dependencies]` 沒被讀取**，只寫在那裡的 crate 會無聲地從報告消失。目前樹內沒有這種表（零列受影響）。
3. **Cargo 的 `0.0.z` 需求只比到 `0.0`。** Cargo 的 caret 在 `0.0.z` 只允許那個 patch，`0.0.4` 出了仍顯示 OK。改為比三段；`0.y.z` 仍比 major.minor。目前樹內沒有 `0.0.z` 宣告（零列受影響）。

告警盤點（2026-10-28，open）：

- **CodeQL 161 筆，全部在上游持有的檔案**（rust 112、js/ts 28、actions 18、python 3 在 `benchmarks/`）。fork 新增的檔案沒有任何告警；fork 修補過的 workflow（`_ci-rust.yml`、`docker.yml`、`sprig*.yml`）也沒有。actions 告警在 `ci.yml`、`_ci-clients.yml`（缺 `permissions`）、`release.yml`、`codex-security-review.yml`（untrusted checkout），fork 都沒改過。不改，隨上游。
- **Dependabot 103 筆，全部在上游持有的 manifest／鎖檔**：pip 84（兩份 benchmarks `uv.lock`，見 2026-10-26 決定第 1 條）、rmcp 12（同第 2 條）、tiptap／prosemirror 3（同第 2 條）、glib 1（Tauri／gtk）、`postcss-selector-parser` 1、`@vitest/mocker` 2。
- **重試結果（第 4 條的觸發條件）：** `postcss-selector-parser` 6.0.10 是 `@tailwindcss/typography` 寫死的精確版本（最新版 0.5.20 仍是 `6.0.10`），只能改 manifest 加 override，不屬於鎖檔更新，維持現狀；觸發：typography 放寬範圍。`@vitest/mocker` 見下。glib 未變。
- **`@vitest/mocker`：已修。** 修補版 4.1.12 已可解析；只動鎖檔，把 vitest 家族由 4.1.11 升到 4.1.12（附帶 vitest 子樹的 chai、obug、std-env、tinyexec、tinyrainbow、`@jridgewell/sourcemap-codec`）。`pnpm install --frozen-lockfile` 對整個 workspace 與唯一使用者 admin-web 通過，`vitest run` 在 4.1.12 啟動正常（admin-web 沒有測試檔）。CI 因 Actions 被停用無法驗證（見下）。

觀察（不改；附觸發條件）：

- **Actions 從 2026-10-26T20:34Z 之後就沒有再跑過。** 最後一次是 `8b45094` 的推送（含上游合併 `9016812`，CI 全綠）；之後三次推送（`6c78657`、`683c8a8`、`4576562`，都只動 `tools/`、`tests/fork`）都沒有 run；`POST .../dispatches` 回 HTTP 422「Actions has been disabled for this repository」，但 `GET .../actions/permissions` 回 `enabled: true`、所有 workflow 都是 `active`。設定 API 與實際執行不一致，表示停用來自 GitHub 端而不是 repo 設定；同一現象也出現在 OpenMontage、AIHOT、reverse-skill、claude-obsidian，rea 的 Security log 有 GitHub 內部 IP 寫入的 `actions_policy_violation`。原因只能在維護者帳號的 Security log 或向 GitHub 客服查。**後果：** 那三個工具 commit 與本輪的 commit 只有本機驗證（`pytest tests/fork`、`pnpm install --frozen-lockfile`），`Fork tools` 的 Windows／Ubuntu 矩陣與 CodeQL 都沒跑。觸發：Actions 恢復後，對 main 手動跑 `CI`、`Fork tools`、`CodeQL`。
