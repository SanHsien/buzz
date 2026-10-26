# Fork 維護說明

本 repo fork 自 [`block/buzz`](https://github.com/block/buzz)（前身 `block/sprout`），沿用 Apache-2.0 與完整 Git 歷史。

## 為什麼維護 fork

- 追蹤 Buzz（中繼器、桌面、行動端、AI 代理整合的通訊平台）。
- 目前**產品碼與上游逐位元組相同**；本 fork 只加維護骨架，不改產品。

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

上游持有的 `README.md`、`AGENTS.md`、`CLAUDE.md` 等**不改**，避免日後同步衝突。

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
