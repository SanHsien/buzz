# Fork 維護說明

本 repo fork 自 [`block/buzz`](https://github.com/block/buzz)（前身 `block/sprout`），沿用 Apache-2.0 與完整 Git 歷史。

## 為什麼維護 fork

- 追蹤 Buzz（中繼器、桌面、行動端、AI 代理整合的通訊平台）。
- 產品**功能**與上游相同；本 fork 沒有自己的功能或行為變更。但下表的「上游持有檔的修補」不是零：
  鎖檔升級會改變實際建置進去的依賴版本，workflow 修補會改變 fork 上的 CI 行為。

**回貢判準：修的是上游的 bug 就送回去；這裡獨創的維護骨架留在這裡。**
回貢前必須在當次對話取得維護者明確同意；「fork」「建環境」「開 PR」都不是同意。

## 與上游的差異

| 項目 | 說明 |
|---|---|
| `FORK.md`、`NOTICE.md`、`docs/fork/` | 來源、授權、決策與同步說明 |
| `tools/check_upstream_updates.py`、`tools/upstream_baseline.json` | 上游 commit／PR／issue 增量檢查與水位 |
| `tools/check_dependency_freshness.py`、`.github/dependency-deferrals.json` | 每月比對宣告的依賴下限（npm、Cargo、workflow pins） |
| `.github/workflows/upstream-check.yml`、`dependency-freshness.yml`、`codeql.yml`、`fork-tools.yml` | 上述檢查、CodeQL、維護工具測試 |
| `.github/dependabot.yml` | 上游用 Renovate，本 fork 改用 Dependabot |
| `.cursor/rules/no-upstream-pr.mdc` | 防呆：禁止誤對上游開 PR 或推送 |
| `tests/fork/`、`tools/dev_check.ps1` | 維護工具的測試與本機 gate |

### 上游持有檔的修補

同步上游時衝突一律以上游為準，再重做修補。帶 `fork patch (SanHsien/buzz)` 標記的檔案由
`tests/fork` 核對一定列在這裡；沒有標記的（鎖檔、測試碼）在下表明列。

| 檔案 | 修補 |
|---|---|
| `.github/workflows/docker.yml`、`.github/workflows/sprig-image.yml` | 非 `block` owner 只 build、不 push（映像名固定在 `ghcr.io/block/*`） |
| `.github/workflows/sprig.yml` | 滾動 release 與 `sprig-v*` tag release 兩個發佈 job 都只在 `block` owner 執行 |
| `.github/workflows/_ci-rust.yml` | 非 `block` owner 時 Windows Rust 逾時 45 → 90 分鐘（無暖快取） |
| `deny.toml` | `RUSTSEC-2026-0253`（lru 0.16.4）一條帶影響評估與移除條件的 ignore（`RUSTSEC-2026-0387` 已由上游 `d676c7b` 的 p256 0.14 取代，ignore 移除）；`RUSTSEC-2026-0459` 的註解加註「只對根 workspace 成立」；`RUSTSEC-2026-0462` 的 ignore 與 rmcp 的 `bans` wrapper／feature 圍欄隨 buzz-agent 遷移移除 |
| `.github/workflows/_ci-security.yml`、`desktop/src-tauri/deny.toml`（fork 新增） | 根目錄 `cargo-deny check` 不讀 `desktop/src-tauri`（獨立 workspace 與鎖檔）；加一步以桌面自己的 `deny.toml`、`--all-features` 檢查 advisories／bans／sources，RUSTSEC-2026-0459 等例外各帶理由與退出條件（2026-11-11 獨立覆核發現）。根目錄 `deny.toml` 的 0459 註解改為只對根 workspace 成立 |
| `Cargo.lock`、`desktop/src-tauri/Cargo.lock`、`pnpm-lock.yaml`、`benchmarks/harbor-buzz-orchestra/uv.lock`、`benchmarks/harbor-buzz-orchestra/testbed/uv.lock` | 相容的鎖檔升級（tokio、hickory、vite、tiptap、benchmark 的 Python 依賴、桌面鎖的 rmcp 3.9.0 等），**manifest 宣告不動**；清單見 `docs/fork/DECISIONS.md` |
| `crates/buzz-push-gateway/Cargo.toml`、`src/app_attest/{authenticator,certificate}.rs`、`src/app_attest_assertion_tests.rs`（含 `Cargo.lock` 的 p256 鏈） | 逐字帶入上游 `d676c7b`（p256 0.13 → 0.14，RUSTSEC-2026-0387）；不是 fork 自己的設計，下次合併上游時內容相同，不會衝突 |
| `.github/workflows/_ci-clients.yml`、`deny.toml`、`Cargo.lock`（pulldown-cmark 0.13.6） | 逐字帶入上游 `c609d33e8`（#8711，Android lane 釘 JDK 17，ubuntu 26.04 預設 JDK 25）與 `c9b8f1176`（#8922，RUSTSEC-2026-0433／0429）；`cherry-pick -x` 保留出處，下次合併上游時內容相同，不會衝突 |
| `desktop/src/features/messages/lib/useRichTextEditor.ts`、`desktop/scripts/tiptap-lock-alignment.test.mjs` | 相容 tiptap ≥ 3.23（`Editor.destroy()` 之後 `editor.commands` 會丟錯）：`clearContent`／`setContent`／`focusEnd`／`focusPreserve` 改走 `editor.chain().<cmd>().run()`（已銷毀時為 no-op）；測試核對鎖檔裡 `@tiptap/*` 同一版。原因與取捨見 `docs/fork/DECISIONS.md` 2026-11-08（再續）；上游若自己補了防護就丟掉 |
| `.github/workflows/_ci-desktop.yml`（`desktop-smoke-e2e`）、`.github/workflows/_ci-relay.yml`（`desktop-e2e-integration-shard`） | 兩個要裝 Playwright chromium 的 job 釘 `ubuntu-24.04`：鎖定的 Playwright 1.60.0 不支援 ubuntu 26.04，fork 沒有上游那份暖瀏覽器快取 |
| `README.md` | 標題下加一段「Maintained fork」說明，寫明上游 `block/buzz`、原作者 Block, Inc. 與 Apache-2.0，並連到本檔與 `NOTICE.md`（2026-11-08 出處盤點的 README 缺口）；合併上游時保留這一段 |
| `crates/buzz-agent/Cargo.toml`、`crates/buzz-agent/src/mcp.rs`（含兩份 `Cargo.lock` 移除 rmcp 1.8.0） | rmcp 1.8 → 3.9.0 遷移（公告 RUSTSEC-2026-0462 等的修補版只有 3.x）：產品碼只有 `tool_result_content` 的型別改名（`Content`／`RawContent` → `ContentBlock`，該 enum 是 `#[non_exhaustive]`，多一個保底分支把未知區塊以標記略過）；`TokioChildProcess` 的用法不用改。行為與上游相同，是產品碼的例外，已用 `fork patch` 標記；同步上游時以上游為準（上游自己遷移時內容應相同）（2026-11-11 獨立覆核發現） |
| `Cargo.toml`（根）、`crates/buzz-dev-mcp/Cargo.toml` | rmcp 宣告：`buzz-dev-mcp` 下限 3.4.1 → 3.9.0（與鎖檔實際版本一致，3.9.0 以下含公告）；根 `[workspace.dependencies]` 沒有任何成員繼承的 `rmcp = "1.1.0"` 移除（2026-11-11 獨立覆核發現）。這是 manifest 宣告的例外，鎖檔不變 |
| `crates/buzz-dev-mcp/src/{shell,read_file}.rs` | 只動 `#[cfg(test)]`：Windows 平行測試共用一把 env 鎖（`e3561ee`），不影響執行期 |

上游持有的 `AGENTS.md`、`CLAUDE.md` 等**不改**，避免日後同步衝突。唯一的例外是 `README.md` 標題下那段「Maintained fork」說明，見上表，合併上游時要保留。

## 分支與 remote

- `origin/main`：`SanHsien/buzz`，主要維護線。
- `upstream`：`block/buzz`，只追蹤、不推送。

不要 `git push upstream`。同步方式見 [`docs/fork/UPSTREAM.md`](docs/fork/UPSTREAM.md)。

## 開發環境

```powershell
git clone https://github.com/SanHsien/buzz.git
cd buzz
gh repo set-default SanHsien/buzz
pwsh -NoProfile -File tools/dev_check.ps1
```

`dev_check.ps1` 只跑維護工具的測試（不編譯 Rust、不啟動桌面視窗）。產品本身的建置與測試依上游 `CONTRIBUTING.md`／`TESTING.md`。
