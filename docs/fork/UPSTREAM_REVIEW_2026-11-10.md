# 2026-11-10 上游差異裁決

接續 [2026-11-02 裁決](UPSTREAM_REVIEW_2026-11-02.md)。範圍：commit `d342cf141cb3211c8e5a6c74f881cf1d39ad3b12..44b3c4823f0cf1f7715f85dbf5566cb64e848162`（238 筆）；PR #8921–#9311 中檢查器列出的 359 筆；issue 25 筆（state=all）。機器證據（SHA、diff SHA-256、檔案清單、掃描命中）在 [UPSTREAM_REVIEW_2026-11-10.json](UPSTREAM_REVIEW_2026-11-10.json)。

## 結論

- commit：238 筆，1 adopt、32 skip、205 defer。
- PR：359 筆，1 adopt、75 skip、283 defer。
- issue：25 筆，0 adopt、14 skip、11 defer。

這批沒有新採用的項目；commit 軸與 PR 軸各有的 1 筆 adopt 是 `c9b8f1176`／#8922，2026-11-07 已因紅燈採用，這裡只歸帳。其餘不採用的原因：fork 的政策是產品行為與上游相同、不自行分岔（FORK.md），而這批橫跨行動端、桌面端、relay 與資料庫，fork 沒有對應的原生與 Postgres 驗收環境。也沒有像 2026-11-07 的 #8711／#8922 那樣的例外觸發：2026-11-10 查 fork `main` 最新一次 CI、CodeQL、Docker image、helm chart、Sprig 皆 success，沒有紅燈需要上游修補。defer 項目的唯一出路是 ROADMAP「同步延後變更」。

## 方法與掃描界限

commit：gh api repos/block/buzz/commits/<SHA> 的 diff；PR：pulls/<n> metadata（base／head SHA）加目前 head 的 diff；issue：gh issue list（state=all）的內文。掃描只看新增行；issue 內文只記錄樣式命中，不當作拒收依據（UPSTREAM.md 的拒收規則針對 diff）。

掃描樣式與 2026-11-02 完全一致（動態執行、零寬／雙向控制字元、120 字元以上 base64／hex、行內 40 空白以上，另加新增行 400 字元門檻）。為確認腳本與上次一致，先拿同一組樣式重掃 2026-11-02 的 84 個 commit：84 筆的掃描命中全部與當時記錄相同。命中一律依 UPSTREAM.md 字面拒收、不自行豁免；下列非長行的命中逐筆讀過命中行，結論不變：

- `303157f53`（#8778）：`crates/buzz-cli/src/commands/sent_from_thread_vectors.json` 有 288 行含 U+FEFF 等字元，是刻意的 Unicode 測試向量。
- `b6d440314`／#9113：命中 `eval(VALIDATE_SCRIPT, &keys)`，是 Rust 對 Redis Lua 腳本的呼叫（`crates/buzz-relay/src/tunnel/directory.rs`），不是動態執行字串，但樣式命中，仍依規則拒收。
- #8983：命中的是 `docs/community-auth-upgrade-acceptance.md` 一行 GitHub 檔案 URL（含 40 字元 commit hash 與長路徑），不是編碼負載，樣式命中，仍依規則拒收。
- #9203：`channel_name_postgres_tests.rs` 兩處測試字串含 U+200D（emoji ZWJ 序列），是「拒絕不可見頻道名」的測試資料。

其餘命中全是新增行超過 400 字元（Justfile、Markdown 長行、JSON 向量、SVG 等）。issue 內文的樣式命中（長行）只記在 JSON 的 `body_notes`，內容是貼上的日誌或表格，不執行也不帶入，不構成拒收。

## 逐項人工確認

- **ROADMAP 觸發條件逐條對照，沒有觸發：** #8856（Windows Desktop 連自架 relay）仍 OPEN，`updatedAt` 為 2026-11-01，審查範圍內沒有新的修正 commit；#8643（Hermes 發訊）仍 OPEN；#8624 仍 CLOSED；`ttsLiveMessages.ts`（code scanning js/redos #22）與 `useRichTextEditor.ts`（fork 的 chain() 防護）在範圍內沒有任何 commit 動到，沒有上游修正可跟進，也沒有上游自補防護可丟；上游根目錄 `Cargo.lock` 仍有 `webpki-roots 0.26.11`，RUSTSEC-2026-0381 ignore 的移除條件未成立；範圍內動 `deny.toml` 的只有已於 11-07 採用的 `c9b8f1176`。
- **fork 持有檔：** 範圍內碰到 `.github/workflows/docker.yml` 的是 `e8a4bc159`（#9310）與 `3e9d2e90c`（#9303）；`sprig*.yml`、`_ci-rust.yml` 沒有被動到。這兩個 commit 都 defer，同步時重做 owner guard。這次沒有改任何上游持有檔，所以 FORK.md 不需更新。
- **Windows／CJK：** 對新增行掃 `cfg(windows)`、`.exe`、`tauri.localhost`、`IME`、`isComposing`、`Windows`、CJK 字元等樣式。commit 命中：`e3a0f3d59`、`c8d736642` 是 CLI 說明「桌面憑證提供者尚不支援 Windows」，`b329e05c5` 是路徑分隔字元註解，`a1efbf63b` 是行動端 IME 處理，`303157f53` 與 `dafe31bfe` 是 CJK 測試字串；沒有任何一個修的是 Windows 或 CJK 專屬缺陷。非合併 PR 命中：#8924（OpenCode 無 PowerShell 安裝器的註解）、#9008（accent 摺疊；CJK 只出現在「日本語原樣通過」的回歸測試）、#9025／#9248（iOS 輸入法）、#9193（路徑分隔註解），同樣都不是。35 筆 closed 未合併 PR 逐一看過標題與檔案數，沒有可採用的 Windows／CJK 缺陷修補。
- **合進非 main 分支的 PR：** #9000、#9020、#9078、#9175、#9232、#9289、#9294 狀態為 MERGED，但 base 是 `mobile-v0.27` 或功能分支，沒有對應的 main commit，不能說「內容經 commit 軸抵達」；各自標在 PR 軸的理由裡。
- **編號落在水位之前的 commit：** commit 軸有 29 個 commit 的 PR 編號 ≤ 8920（PR 軸不會再列），其 diff 以 commit 為準逐筆裁決。

## Commit 軸（238 筆）

| Commit | 標題 | 裁決與理由 |
| --- | --- | --- |
| `a83926da5d0d` | test(desktop): stop four E2E specs racing scroll settles and focus (#8743) | **defer**：桌面端（Tauri／Windows）變更，需實機驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `322fdbf086cd` | test(relay): hold the replica's second aux page and move media's DB tests (#8740) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `c9b8f1176ece` | fix(deps): clear RUSTSEC-2026-0433 and RUSTSEC-2026-0429 from the dependency policy (#8922) | **adopt**：2026-11-07 已因 Security / Dependency policy 紅燈採用（fork commit e74c2e4e3，cherry-pick -x 帶入 Cargo.lock 與 deny.toml）；這次只把它歸進水位，詳見 DECISIONS.md 同日條目 |
| `b4509dee8b5a` | feat(mobile): add Buzzies and refresh agent avatar picker (#8921) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `daeb463f37fc` | fix(mobile): prompt Builderlab sign-in instead of labeling agents desktop-only (#8907) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `9f8913dd1b86` | mobile: keep a thumbnail fallback apart from a direct load of the same URL (#8913) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `3ae2b6a3771b` | fix(mobile): hide the Flutter debug banner (#8915) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `f99807a79ae0` | fix(desktop): skip a starter channel the relay will never create (#8911) | **defer**：桌面端（Tauri／Windows）變更，需實機驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `da93ce3f6290` | fix(mobile): open the public Builderlab login the iOS bridge allows (#8914) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `f1ce1c5d4744` | docs(nip-fa): make assertion lifetime issuer operator policy (#8934) | **skip**：拒收：新增行超過 400 字元（docs/nips/NIP-FA.md），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `5f8d0aab9829` | fix(relay): refuse a second listed open channel with the same name (#8782) | **skip**：拒收：新增行超過 400 字元（NOSTR.md），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `54ca2a3cc6b8` | fix(mobile): render Markdown backslash escapes (#8925) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `2fd5c122e8bb` | fix(mobile): load earlier edits to thread replies when a thread opens (#8870) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `b5b69d3de8e9` | fix(mobile): let the issuer choose relay assertion lifetime (#8935) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `35df866b334c` | fix(mobile): split escaped voice-note links into their own segment (#8940) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `8f83c6320994` | fix(db): preserve partition reader grants (#8485) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `97ff4e19d15b` | docs(mobile): describe the role split in the media image keys (#8932) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `61b8455a3c26` | fix(mobile): open unjoined channels from links and search results (#8923) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `fa395e9e80e3` | feat(mobile): open a prefilled Create agent form from Builderlab agent cards (#8912) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `009dc103f615` | perf(mobile): read the channel list after live changes, not every minute (#8910) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `949f61dfab06` | fix(search): cancel abandoned searches and bound the search pool (#8954) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `02925ceb6e73` | fix(relay): cap bridge searches in flight per user (#8956) | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `46da35810d65` | db: recycle pool connections after 5 minutes instead of 30 (#8951) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `0ec74838a5bd` | fix(mobile): open consent for scanned and pasted invites (#8952) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `cdd2af1a3525` | fix(mobile): let starter setup retry after a connection failure (#8967) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `205ff47744bd` | fix(mobile): retry failed channel searches after reconnecting (#8968) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `1c143a40b77a` | fix(mobile): show the Join prompt when an invite launches Buzz (#8970) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `83bd8b1caed7` | fix(loadgen): sign public URLs when dialling connect_addr in plaintext (#8926) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `6684f7e2f0dc` | fix(mobile): make the Join button readable in dark mode (#8969) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `09b21cbe632c` | fix(mobile): label community switching consistently (#8979) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `972e89ac8972` | fix(mobile): allow community removal without a cached push grant (#8978) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ff6ab96e42b1` | fix(mobile): drop the # from Solo chat names in push notifications (#8955) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `76bc66acfcae` | mobile: hold a queued list read for the 10s gap (#8958) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `478cf0a97e4e` | docs(mobile): recommend Xcode 27.1 (#8949) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `fc9e652c0ee8` | perf(mobile): format a channel timeline only when its events change (#8929) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `cad7f1d53d2c` | perf(mobile): build composer channel names once per channel list (#8943) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `eee75a1c7ba1` | perf(mobile): verify owned-agent registrations natively (#8938) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `369e1ef3229d` | perf(mobile): stop re-parsing message markdown on every rebuild (#8928) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `58eb36dd5791` | perf(mobile): cheaper identity-name rebuilds for large rosters (#8936) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `d005c7bb9cff` | fix(search): skip message prefix search below three characters (#8947) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `d44031f4187b` | perf(relay): cut writer-pool round trips past the 48k relay ceiling (#8846) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `0e5a69962e5c` | perf(mobile): evict verified-profile interest in constant time (#8931) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `344f007f364c` | Add mobile Bestie onboarding and fix remote agent presence (#8957) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `a66cb5f7ab77` | Modernize mobile channel and DM creation sheets (#8942) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `3f03aa045085` | fix(mobile): restore ordinary DM behavior for Bestie (#8987) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `d3a4909ccad7` | perf(search): rank only the newest prefix matches and plan with the real tsquery (#8976) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `33eaa73c8313` | fix(mobile): let users sign out after leaving all communities (#8993) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `40fe4b5d9a98` | perf(mobile): evict verified-profile interest in one pass (#9007) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `7d40a661264f` | fix(ios): stop repeating an old message in push notifications (#8973) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ce47aefdc3fc` | fix(relay): send membership notices on channel delete, moderation kick and moderation DM (#8977) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `a9aa1f73b01b` | Enable incremental artifact reads on every relay (#8975) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `bf13f7c83bdd` | fix(ios): mint NIP-FI assertions in the notification extension (#8982) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `f6198f699750` | feat(relay): record NIP-FI enforce denials at parity with shadow (#8974) | **skip**：拒收：新增行超過 400 字元（crates/buzz-relay/src/nip_fi_shadow.rs），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `298a555e341f` | perf(db): bind the channel scope as one array (#8946) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `b8b425e8b1bf` | fix(db): drop a superseded head's mention rows with it (#8948) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `88697f1c597c` | fix(relay): apply kind 5 / 9005 deletions atomically (#8944) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `152441ae0a56` | feat(loadgen): model desktop clients and large-community shape (#9005) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `c24b0f472e47` | Open the new Bestie's chat after creating it (#8972) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `6847882b149f` | fix(relay): stop logging unmapped-host NIP-FI denials as server failures (#8997) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `8312419652d9` | fix(mobile): size reply labels correctly with Bold Text (#9013) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `fa7a3bfbda83` | feat(relay): push per-community storage usage to kgoose (#8714) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `0a06c0b3cb17` | feat(relay): log reads, logins and connections on access target (#8376) | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `dafe31bfe550` | feat(mobile): persist frontier-only NIP-RS read state across devices and restarts (#8998) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `9f88eb9c459d` | mobile: hide self-joins and leaves, collapse membership runs like desktop (#8962) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `865b150371d4` | fix(db): use ScratchDb in the storage usage delivery test (#9032) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `b14899ffb1d2` | docs(nip-fa): define agent grant, assertion and revocation routes (#9015) | **skip**：拒收：新增行超過 400 字元（docs/nips/NIP-FA.md），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `1bef1da77d4c` | fix(mobile): show newly created remote agents in the new-chat picker (#9030) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `83d0bd32034e` | fix(mobile): stop QR pairing to organization relays from hanging (#9001) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `3d26ed7dfdd2` | feat(relay): match verified names in profile search (#9019) | **skip**：拒收：新增行超過 400 字元（migrations/0081_nip_fi_profile_head_names.sql），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `38a5d9a1ffe2` | mobile: tap the settings version footer to copy it (#9021) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `1055f79d048e` | fix(mobile): show a taken channel name plainly and keep invites working (#8807) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `069cb9a0fe7a` | fix(desktop): hold a deep-linked message against bottom settles (#8742) | **defer**：桌面端（Tauri／Windows）變更，需實機驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `14037e32780e` | fix(mobile): show progress after pairing QR scans (#9009) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ba7d7825ea8e` | fix(mobile): show organization sign-in after pairing (#9028) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `f04fa0904c99` | fix(mobile): close the community switcher when the org relay refuses the key (#9042) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `0dd778f800af` | mobile: start new agents on Sonnet at medium effort (#9034) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `49fcab332454` | mobile: refine message avatars, metadata and reply gestures (#9046) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `d21f0c0fdbec` | perf(relay): keep 1 s read caches warm when the pool is saturated (#9012) | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `f9ef721e6888` | fix(media): keep transparency in image thumbnails with WebP (#9003) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `0bdad8ea965d` | mobile: simplify verified profiles and prioritize full names (#9051) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `5b738eb647fb` | Restyle mobile organization sign-in prompts as toasts (#9050) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `25abfc41177b` | fix(loadgen): bound desktop reads at stop, keep timely EOSEs, model presence and probes (#9016) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `4813b8cd1541` | relay: time every WebSocket read and every stored EVENT outcome (#9052) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `a1f79e3aba6f` | feat(relay): persist NIP-FI upgrades (BUZZ-510) (#8985) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `90de03aa63f3` | feat(mobile): back up nsec to org builderlab account (#9029) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ce94656b0d81` | fix(mobile): use join template for community creation (#9072) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `99873459e940` | Keep sign-in toasts usable at large text sizes (#9057) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `7b3c2f95f217` | fix(mobile): bound notices to loaded message history (#9062) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `041956ea446c` | fix(ios): saturate the push dedupe cutoff so extreme timestamps can't crash (#9010) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `7157a55f5f3d` | fix(mobile): keep the iOS 27 header blur in long chats (#8971) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `f09956179d5b` | fix(mobile): keep the composer focused through iOS inactive spells (#9055) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ec21753e1b4c` | Make mobile New DM and Add members pick recipients like mention autocomplete (#9065) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `af54258f19ac` | fix(mobile): streamline identity setup and community selection (#9070) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `5d44038ea544` | mobile: invite new users to create their first agent with a bold card (#9036) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `9c5032b63bcf` | perf(mobile): derive keys natively and hash NIP-98 bodies faster (#8965) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `237d794acbce` | perf(mobile): skip re-decrypting read-state blobs (#8966) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `e558f15faa49` | Mobile: one New chat screen (#9079) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `34174214fcaf` | fix(mobile): restore keysForNsec after the native key derivation change (#9085) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `506a588f889b` | refactor(relay): remove database usage-metric queries (#9040) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `64d12e297519` | BUZZ-511: Honor relay mode for community NIP-FI enforcement (#8988) | **skip**：拒收：新增行超過 400 字元（ARCHITECTURE.md, Justfile, docs/multi-tenant-conformance.md），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `700e69019321` | feat(db): enforce unique listed channel names with an index (#8787) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `920b1e64bdd0` | perf(mobile): keep covered pages still while the keyboard moves (#8941) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `6b8a72e83551` | fix(mobile): send hosted relay auth with iOS custom emoji downloads (#9056) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `aa749a862ef6` | perf(db): serve single-root thread reply reads from thread_metadata (#9075) | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `bc99726f5c89` | docs(agents): add Review-Proven Rule 9, design client paths for the whole fleet (#9106) | **defer**：文件變更，隨產品同步一併帶入；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ab399231c29a` | docs: mark desktop/ as the deprecated Buzz 0.X app (#8840) | **defer**：文件變更，隨產品同步一併帶入；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ff15c347c2f6` | fix(db): auto-migrate prebuild-guarded indexes on small databases (#8802) | **skip**：拒收：新增行超過 400 字元（crates/buzz-db/src/runtime/migration.rs），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `50c10dc7b26e` | perf(relay): cache the community-active check on socket admission (#9109) | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `5e36d65c9e64` | fix(mobile): inflate gzip read-state snapshot responses (#9089) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `e34acb0ac5db` | fix(mobile): keep reply counts on screen while a reconnect catches up (#9100) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `3ff4154ca61c` | fix(mobile): back off push bootstrap retries (#9092) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `244038b49529` | mobile: reuse channel message rows that did not change (#9115) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `cf8fbbba5570` | fix(mobile): keep verified names on screen in channels with over 1,024 members (#9111) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `dce37f74d787` | fix(mobile): skip the read-state snapshot when nothing needs publishing (#9093) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `8a113ed99e04` | fix(desktop): show upgrade guidance (BUZZ-517) (#9033) | **skip**：拒收：新增行超過 400 字元（desktop/src-tauri/tests/fixtures/nip_fi/buzz_main_6b8a72e835_optional.json, desktop/src-tauri/tests/fixtures/nip_fi/buzz_main_6b8a72e835_optional_capable.json, desktop/src-tauri/tests/fixtures/nip_fi/buzz_main_6b8a72e835_required.json），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `c848b6dcadee` | fix(mobile): offer a new identity beside saved keys on unclaimed accounts (#9107) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `9aa70124bae4` | perf(mobile): validate each verified profile once, not on every publish (#9101) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `6793cbd25b7f` | fix(mobile): focus the search field when search opens (#9120) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `120d75d9762e` | Expose strict code-entry pairing and live authorization bindings (#9061) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `97ede701c0a1` | fix(mobile): send hosted relay assertion from native media and tombstone paths (#9069) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `9b4b73eb088d` | fix(relay): bound mesh dials and keep failing pods out of the mesh (#8752) | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `74abe2f0fe1a` | perf(db): split newest-first events reads at a month floor so Postgres prunes partitions (#9091) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `1b9b3071765f` | fix(mobile): renew expired assertions for native media and drop retired-session avatars (#9134) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `1ce831645c5f` | mobile: stop re-parsing messages on every resume (#9140) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `7ac16b2917bf` | perf(mobile): memoize npub labels (#9137) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `47be2e2d3f2a` | fix(db): keep busy-reader history reads off the writer and cap them per pod (#9132) | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `a22ff133b49a` | test(relay,db): remove three timing races from Postgres and E2E tests (#9098) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `580caca66714` | fix(db): unlock the storage-accounting lease before its session closes (#9097) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `1a42b5c39cde` | fix(relay): read kind:39000/39001 inputs behind the replacement lock (#9035) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `bdd76baea552` | fix(desktop): compensate head trims from the unclamped scroll offset (#9094) | **defer**：桌面端（Tauri／Windows）變更，需實機驗收；同時動到 fork 持有修補的檔案（pnpm-lock.yaml），同步時衝突以上游為準再重做修補；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `cec918ae7a13` | perf(mobile): show a static placeholder for posterless videos (#9138) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `4c7c15a9c2b9` | fix(db): end each table's maintenance transaction before the next (#9096) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `e94b547f600d` | fix(desktop): keep an own send out of the frozen timeline tail (#9095) | **defer**：桌面端（Tauri／Windows）變更，需實機驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `46cdc52d234c` | test(mobile): lock in invite-page and bare-host community link entry (#9047) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `2bd491782534` | fix(mobile): answer push snapshot bridge calls at user-initiated QoS; report hop latency on callback timeout (#8916) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `f82944e3180e` | docs(agents): add open-source boundary and drop private repo list (#9114) | **skip**：拒收：新增行超過 400 字元（AGENTS.md），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `198c4c3e9bff` | feat(cli): list huddles and their participants (#8830) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `0ada1d37077f` | buzz-db: read explicit #h sets one channel at a time (#9110) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `82bc5a47c5e5` | feat(cli): report a message to relay moderators (#8829) | **skip**：拒收：新增行超過 400 字元（crates/buzz-cli/src/lib.rs），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `171100f30871` | feat(cli): read-only unread state (NIP-RS) (#8789) | **skip**：拒收：新增行超過 400 字元（crates/buzz-cli/src/lib.rs），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `5c91e0d6fe4e` | feat(relay): add kind 30180 custom emoji entry (#8783) | **skip**：拒收：新增行超過 400 字元（docs/nips/NIP-CE.md），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `303157f53d28` | feat(cli): send a thread message to the channel (#8778) | **skip**：拒收：含零寬／雙向控制字元（crates/buzz-cli/src/commands/sent_from_thread_vectors.json），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `b0f68a06ad25` | feat(cli): user status expiry and status read (#8777) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `4aae6c22aa73` | fix(mobile): delay iOS message actions until a deliberate hold (#9049) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `b6d4403149af` | perf(redis): index mesh ready records and share one Redis connection (#9113) | **skip**：拒收：含 eval(／new Function(／global.require 樣式（crates/buzz-relay/src/tunnel/directory.rs），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `0cfa50ac70b2` | perf(db): use exact event timestamps for transactional deletion (#9130) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `997ce3a2c9cd` | perf(db): prune post-commit push enqueue by signed event timestamp (#9128) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `cec47c20a3f1` | perf(db): hydrate search hits with exact event timestamps (#9126) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `66c3d6917ddd` | feat(protocol): define compact membership discovery (BUZZ-615) (#9117) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `c39ee507b273` | fix(mobile): find verified people who have no profile (#9086) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `e3a0f3d59dfd` | feat(cli): send NIP-FI evidence via credential chain and Buzz desktop (#8999) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `133c883b8ca1` | fix(mobile): confirm before starting a Huddle from the header (#9155) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `bd1b17dee834` | perf(db): plan multi-value #d reads with their values (#9131) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `fba8a7a94feb` | feat(relay): log WebSocket EVENT writes on the access target (#9154) | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `fc85b0d1547d` | test(mobile): check posterless video previews renew the relay assertion (#9144) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `5d094cd76992` | release(mobile): push candidate tags as the operator, not the App (#9084) | **skip**：拒收：新增行超過 400 字元（scripts/test-mobile-release-contract.sh），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `1a30e51689b9` | mobile: start new agents on the server-recommended model (#9151) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `fd0ec105050d` | perf(mobile): rank search channels once per query (#9136) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `bb3c5f717504` | feat(relay): project compact viewer memberships (BUZZ-615) (#9118) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `8ae35c5c9269` | perf(db): stop the events recent pass at a ceiling for regular-kind reads (#9157) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `1bb44ae9effd` | fix(relay): close a WS search whose hit hydration fails instead of sending EOSE (#9148) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `fbfbf3d64f02` | test(mobile): drop the video preview step removed with native frame loading (#9164) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `a1efbf63bddb` | fix(mobile): delete composer chips as one unit (#9133) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `b894fb02ffb1` | fix(mobile): show transparent avatars without a black background (#9105) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `4e28176f1395` | fix(relay): close legacy sockets after community FI upgrades (#8991) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `9a6cb3ffdfe8` | mobile: make the first-agent card stand out in dark mode (#9171) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `32997e2e1b57` | Cache channel memberships once per user (#9060) | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `962b3fdd882b` | Add avatar color backdrop to mobile agent creation (#9184) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `b329e05c5b75` | fix(cli): list DMs, attach any file, validate kinds, default the relay (#9168) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `3fdd8c6ff1ca` | feat(loadgen): model agent turns and sustained holds (#9182) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `1bb2ad443d4e` | fix(relay): regenerate missing image thumbnails on request (#9174) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `0a4d209046ee` | Show mobile floating dates while scrolling (#9185) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `e43d57c6ba2d` | feat(cli): manage sidebar sections with `buzz sidebar sections` (#9191) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `abb2586f8ca6` | Pin sqlx to the upstream fix for a cancelled BEGIN (#9192) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `744f3946f6fe` | perf(relay): serve restriction rows for 10 s with cross-pod invalidation (#9199) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `c8d736642e1c` | fix(cli): clearer desktop pairing errors, paired default relay, and auth desktop list (#9196) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `a25f3cd1d794` | fix(mobile): match Agents sign-in to Home’s reconnect capsule (#9204) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `0d5edb8bb36b` | perf(db): bound since-limited events reads with the month-floor literal (#9197) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `27ab6a085a66` | fix(relay): deliver multi-node fan-out concurrently and never drop silently (#9195) | **skip**：拒收：新增行超過 400 字元（ARCHITECTURE.md, Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `01d9778606bd` | fix(relay): route live REQ events by each filter's own channel scope (#8519) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `a17243d846c8` | feat(relay): runtime-tunable history-read and AUTH concurrency caps via feature flags (#9170) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `e670b672b8b2` | perf(loadgen): spread seed writes across channel creators (#9206) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `446e9e0762a4` | Allow operators to set initial NIP-FI policy on create (#9211) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `beec0553003e` | feat(mobile): move Activity to a Home bell and align Home spacing (#9212) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `6c3ffd160bc0` | fix(relay): set received_at in the system-channel fan-out test helper (#9214) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `597a8d197030` | feat(mobile): rename Activity and add header filters (#9213) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `38795ada8749` | fix(db): keep retained fence proofs when a probe fails (#9200) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `39d5159caf74` | [buzz] Recover interrupted default-channel auto-joins (#9045) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `2cd40badb85d` | Manage community NIP-FI policy with enable, disable and status (#9176) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `96af488d968a` | fix(media): revoke private channel attachment reads (#9077) | **skip**：拒收：新增行超過 400 字元（Justfile, crates/buzz-db/src/store/media_postgres_tests.rs），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `b58ee0840454` | fix(mobile): request hosted relay assertions only when NIP-FI is required (#9225) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `794ee6418341` | fix(ios): mint hosted NIP-FI assertions in the notification extension (#9228) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `12f3d510011b` | feat(mobile): one Builderlab per build, internal and public distributions (#9224) | **skip**：拒收：新增行超過 400 字元（docs/adr/0001-internal-and-public-mobile-builds.md），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `f3b127e3af5c` | fix(mobile): keep Home bell tappable while scrolled (#9241) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `1a0dae77bfc3` | fix(mobile): shimmer loading photos in the iOS carousel (#9167) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `e86d0e23a335` | feat(mobile): long-press a Solo chat to open its details sheet (#9163) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `a7a534d47692` | mobile: long-press a message link for open, copy and share (#9135) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `d839d3731a11` | fix(mobile): swipe left to reply so swipe-back keeps rightward drags (#9127) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `8130cd9fc7d8` | fix(cli): preserve attachments across successive edits (#9226) | **skip**：拒收：新增行超過 400 字元（crates/buzz-db/src/store/media.rs），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `8cce12f59198` | feat(mobile): consolidate Solo chat settings in one sheet (#9255) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `4bfe60197e8c` | fix(relay): say "channel owner or admin" in the call_webhook save refusal (#9169) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `31fa53174d5b` | Record why relay connections close and quiet close warnings (#9245) | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `65e864301d2e` | feat: send a User-Agent on relay WebSocket upgrades (#9246) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `22d96d94ef04` | [buzz] Recover database pool capacity after stalled connections (#9267) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `439d7bcc12c5` | fix(mobile): keep a sent thread reply above the composer (#9026) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `733d164e8068` | mobile: persist user profiles so names and avatars render on launch (#9116) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ad5699d05aa2` | fix(mobile): start no threads in Solo chats (#9123) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `40cfa72cd411` | mobile: add follow and remind actions to inbox row menu (#9142) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ac2c5831f32f` | fix(mobile): show already-loaded custom emoji in the iOS reactions sheet (#9150) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `e1e1cd50abdc` | fix(mobile): keep Home's header clean under sheets (#9152) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `58696ff577c9` | fix(mobile): show the channel name as the notification subtitle (#9173) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `f38285562c6d` | fix(mobile): read only shown events from filtered Activity rows (#9215) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `15174bc2b263` | fix(relay): deliver slow cross-node events late instead of closing their recipients (#9235) | **skip**：拒收：新增行超過 400 字元（ARCHITECTURE.md），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `52cb6818face` | perf(mobile): keep remote images on disk and show small ones as thumbnails (#9158) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `5f5994054481` | fix(mobile): steady New DM picker rows and animate picks (#9249) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `c502e53e634b` | feat(mobile): tag the reacted-to message author on reactions (#9141) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `34bab2f64b6a` | feat(ci): allow admin dispatch of desktop candidate validation (#9288) | **defer**：CI workflow 變更，未動 fork 修補的檔案；fork 的 main CI 沒有紅燈觸發採用；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `658253009c51` | fix: unblock image audit with patched MCP SDK (#9287) | **defer**：依賴鎖檔／政策變更，fork 的鎖檔升級與 deny.toml 修補須在同步時重做；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `3071279cd863` | NEXUS-4336: Wait for desktop-provider socket ownership proof (#9270) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `838976d6e454` | Add invite preview video and fallback poster (#9282) | **skip**：拒收：新增行超過 400 字元（previews/invite-video/README.md, previews/invite-video/preview.js），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `b082b1464ce5` | test(relay): give every media e2e upload its own blob hash (#9272) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `c1ce2ca8001c` | fix(mobile): read mentions taller than the screen (#9243) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `2bbaa061d023` | Enable mobile huddles with Codex agents (#9269) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `49511f02b602` | fix(mobile): show observed thread replies in Activity (#9286) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `66095e559857` | fix: inline ARM64 atomics in Sprig image build (#9291) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `2b16d0ea1a55` | feat(relay): let an operator mint invites for a community owner or admin (#9265) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `15c2ca1b018d` | test(desktop): wait on real readiness signals in audience and community-rail specs (#9277) | **defer**：桌面端（Tauri／Windows）變更，需實機驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ea548da80895` | test(ios): wait for a key, foreground-active window before presenting in RunnerTests (#9275) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `d2c3234cb982` | fix(ci): classify hermit retry timeouts by watchdog kill, not whole seconds (#9274) | **defer**：腳本／工具變更，隨產品同步一併帶入；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `85996fdff491` | test: fix timing-dependent unit tests in buzz-cli, buzz-agent and buzz-admin (#9273) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `dd9da3ac6d85` | fix(relay): never close connections when cross-node fan-out falls behind (#9302) | **skip**：拒收：新增行超過 400 字元（ARCHITECTURE.md），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `5b1698ec244d` | fix(db): give the replica-fence probe its own pool and instrument it (#9297) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `18f3e35413c6` | docs: point the README to Buzz 1.0 in block/buzz-app (#9296) | **defer**：文件變更，隨產品同步一併帶入；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `773849665e05` | Serve video and poster previews for invite links (#9306) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `402bd1897f8b` | fix(mobile): bump Flutter to 3.47.9 for Android TLS fix (#9309) | **defer**：腳本／工具變更，隨產品同步一併帶入；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `3e9d2e90ce87` | Add manual-only relay image publishing (#9303) | **defer**：新增發佈映像的 workflow `docker-manual.yml`（手動觸發）；fork 的發布 guard 規則要求非 `block` owner 不得 push 映像，同步時須先補 owner guard 並讓 tests/fork 的發佈 job 檢查通過；fork 的 main CI 沒有紅燈觸發採用；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `e8a4bc15917e` | ci(docker): skip relay image publishes for main pushes outside the build context (#9310) | **defer**：CI workflow 變更，與 fork 的 workflow 修補（.github/workflows/docker.yml）衝突，同步時一併重做；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `44b3c4823f0c` | Add swipeable photo stacks and native iOS gallery preview (#9259) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |

## PR 軸（359 筆）

| PR | 狀態 | head | 標題 | 裁決與理由 |
| --- | --- | --- | --- | --- |
| #8921 | MERGED | `af78b2686bef` | feat(mobile): add Buzzies and refresh agent avatar picker | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8922 | MERGED | `ab44abfc9920` | fix(deps): clear RUSTSEC-2026-0433 and RUSTSEC-2026-0429 from the dependency policy | **adopt**：同 commit 軸 `c9b8f1176ece`：2026-11-07 已因 Security / Dependency policy 紅燈採用，這次只歸進水位 |
| #8923 | MERGED | `4becf4a1dbaf` | fix(mobile): open unjoined channels from links and search results | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8924 | CLOSED | `8ce2f7f740b1` | feat: promote OpenCode to a tier-1 ACP runtime | **skip**：closed 未合併；拒收：新增行超過 400 字元（crates/buzz-acp/README.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8925 | MERGED | `d5b415abfb74` | fix(mobile): render Markdown backslash escapes | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8926 | MERGED | `7011f24baf57` | fix(loadgen): sign public URLs when dialling connect_addr in plaintext | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8928 | MERGED | `cc0071e76df0` | perf(mobile): stop re-parsing message markdown on every rebuild | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8929 | MERGED | `f417bf0e3665` | perf(mobile): format a channel timeline only when its events change | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8930 | OPEN | `b92183751606` | Honor issuer-selected mobile assertion lifetimes | **defer**：OPEN，head 釘在 b92183751606，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #8931 | MERGED | `20517514378f` | perf(mobile): evict verified-profile interest in constant time | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8932 | MERGED | `f8e9e918e787` | docs(mobile): describe the role split in the media image keys | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8933 | OPEN | `5a767cf70059` | fix(relay): certify artifact sync visibility durably | **defer**：OPEN，head 釘在 5a767cf70059，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；草稿／WIP |
| #8934 | MERGED | `a2acb929da64` | docs(nip-fa): make assertion lifetime issuer operator policy | **skip**：拒收：新增行超過 400 字元（docs/nips/NIP-FA.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8935 | MERGED | `f2024a5ac57a` | fix(mobile): let the issuer choose relay assertion lifetime | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8936 | MERGED | `11501a47a994` | perf(mobile): cheaper identity-name rebuilds for large rosters | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8937 | OPEN | `6a97868f8a41` | Budget agent events per owner and channel | **skip**：拒收：新增行超過 400 字元（ARCHITECTURE.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8938 | MERGED | `4045c584dc96` | perf(mobile): verify owned-agent registrations natively | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8939 | CLOSED | `235768afe7ff` | fix(mobile): keep the native Join button readable in dark mode | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #8940 | MERGED | `e588abac225a` | fix(mobile): split escaped voice-note links into their own segment | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8941 | MERGED | `2a92ddd4941e` | perf(mobile): keep covered pages still while the keyboard moves | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8942 | MERGED | `ce1c498ff2c1` | Modernize mobile channel and DM creation sheets | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8943 | MERGED | `d10c167b82b9` | perf(mobile): build composer channel names once per channel list | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8944 | MERGED | `9e5a7ce83284` | fix(relay): apply kind 5 / 9005 deletions atomically | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8945 | OPEN | `45f75bf51c39` | feat(mobile): render messages with gpt_markdown 1.3.4 plusparse | **defer**：OPEN，head 釘在 45f75bf51c39，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #8946 | MERGED | `801b57594f03` | perf(db): bind the channel scope as one array | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8947 | MERGED | `9b131a578645` | fix(search): skip message prefix search below three characters | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8948 | MERGED | `d8a28add113e` | fix(db): drop a superseded head's mention rows with it | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8949 | MERGED | `f62cebd3bb74` | docs(mobile): recommend Xcode 27.1 | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8951 | MERGED | `fbe5d12bb564` | db: recycle pool connections after 5 minutes instead of 30 | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8952 | MERGED | `f31f8f8505f4` | fix(mobile): open consent for scanned and pasted invites | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8953 | OPEN | `4b54486e3c63` | feat(mobile): let owners rename and re-avatar remote agents | **defer**：OPEN，head 釘在 4b54486e3c63，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #8954 | MERGED | `c05cef6f8f69` | fix(search): cancel abandoned searches and bound the search pool | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8955 | MERGED | `12f9343f9fae` | fix(mobile): drop the # from Solo chat names in push notifications | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8956 | MERGED | `6fee6a645d39` | fix(relay): cap bridge searches in flight per user | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8957 | MERGED | `cbfc0787e5d9` | Add mobile Bestie onboarding and fix remote agent presence | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8958 | MERGED | `c0f693015f5f` | mobile: hold a queued list read for the 10s gap | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8959 | OPEN | `205cca5adf81` | Add standalone agent database deletion handler | **defer**：OPEN，head 釘在 205cca5adf81，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；草稿／WIP |
| #8961 | CLOSED | `d4dff005abc8` | mobile: drop the leading space iOS dictation adds to an empty composer | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #8962 | MERGED | `db96b00f8b96` | mobile: hide self-joins and leaves, collapse membership runs like desktop | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8963 | OPEN | `2a9902506cac` | feat(mobile): add channel and solo access controls | **defer**：OPEN，head 釘在 2a9902506cac，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8964 | CLOSED | `f823c6addf99` | fix(search): bound every search statement with the read deadline | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #8965 | MERGED | `d08f598a55ee` | perf(mobile): derive keys natively and hash NIP-98 bodies faster | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8966 | MERGED | `04ad2e3f5327` | perf(mobile): skip re-decrypting read-state blobs | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8967 | MERGED | `5a95f8a85fde` | fix(mobile): let starter setup retry after a connection failure | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8968 | MERGED | `4264a1af9cb8` | fix(mobile): retry failed channel searches after reconnecting | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8969 | MERGED | `1cf9be4e95d6` | fix(mobile): make the Join button readable in dark mode | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8970 | MERGED | `11b16d8c1618` | fix(mobile): show the Join prompt when an invite launches Buzz | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8971 | MERGED | `ae443e711a4c` | fix(mobile): keep the iOS 27 header blur in long chats | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8972 | MERGED | `cc4b8f2e3e34` | Open the new Bestie's chat after creating it | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8973 | MERGED | `a696c0c5268d` | fix(ios): stop repeating an old message in push notifications | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8974 | MERGED | `7d93b92dcfdb` | feat(relay): record NIP-FI enforce denials at parity with shadow | **skip**：拒收：新增行超過 400 字元（crates/buzz-relay/src/nip_fi_shadow.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8975 | MERGED | `62b26ad7386c` | Enable incremental artifact reads on every relay | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8976 | MERGED | `d14f256d730b` | perf(search): rank only the newest prefix matches and plan with the real tsquery | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8977 | MERGED | `52e367dd9a92` | fix(relay): send membership notices on channel delete, moderation kick and moderation DM | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8978 | MERGED | `6bd3f09af049` | fix(mobile): allow community removal without a cached push grant | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8979 | MERGED | `41ab0a46471f` | fix(mobile): label community switching consistently | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8981 | OPEN | `db27b0b08d56` | feat(import): consented conversation import with original timestamps (NIP-CI) | **skip**：拒收：新增行超過 400 字元（NOSTR.md, docs/nips/NIP-CI.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8982 | MERGED | `1a19e5741bac` | fix(ios): mint NIP-FI assertions in the notification extension | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8983 | OPEN | `c23ab22a79e3` | docs(auth): define BUZZ-516 upgrade acceptance | **skip**：拒收：含 120 字元以上 base64／hex 樣式（docs/community-auth-upgrade-acceptance.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8984 | CLOSED | `5e9dfb00f095` | BUZZ-517: Prepare mobile auth requirement discovery | **skip**：closed 未合併；拒收：新增行超過 400 字元（mobile/test/fixtures/nip_fi/buzz_511_d3ae4935b_optional.json, mobile/test/fixtures/nip_fi/buzz_511_d3ae4935b_optional_capable.json, mobile/test/fixtures/nip_fi/buzz_511_d3ae4935b_required.json），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8985 | MERGED | `12ed9f93803a` | feat(relay): persist NIP-FI upgrades (BUZZ-510) | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8986 | CLOSED | `79c96c0b00fe` | feat(mobile): offer "Create your first agent" in DMs | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #8987 | MERGED | `c6fef5d80cf2` | fix(mobile): restore ordinary DM behavior for Bestie | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8988 | MERGED | `39dfe79b1fc0` | BUZZ-511: Honor relay mode for community NIP-FI enforcement | **skip**：拒收：新增行超過 400 字元（ARCHITECTURE.md, Justfile, docs/multi-tenant-conformance.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8990 | OPEN | `cb9d5ea64ff1` | fix(desktop): keep dropped files from replacing the onboarding window | **defer**：OPEN，head 釘在 cb9d5ea64ff1，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收；草稿／WIP |
| #8991 | MERGED | `1c74532516f6` | fix(relay): close legacy sockets after community FI upgrades | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8993 | MERGED | `92b83cd71b9a` | fix(mobile): let users sign out after leaving all communities | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8994 | OPEN | `ff27111a236d` | feat(relay): add guarded task lifecycle API (NEXUS-4111) | **defer**：OPEN，head 釘在 ff27111a236d，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補；草稿／WIP |
| #8995 | OPEN | `30645f53e5ca` | fix(relay): serialize archived channel writes (NEXUS-4111) | **skip**：拒收：新增行超過 400 字元（crates/buzz-relay/src/api/git/settings_tests.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8997 | MERGED | `4979893b97eb` | fix(relay): stop logging unmapped-host NIP-FI denials as server failures | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8998 | MERGED | `5d8ed0dc6829` | feat(mobile): persist frontier-only NIP-RS read state across devices and restarts | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8999 | MERGED | `f4ad4ed9f876` | feat(cli): send NIP-FI evidence via credential chain and Buzz desktop | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補 |
| #9000 | MERGED | `6f20f1952fba` | Add persistent mobile Bestie welcome | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9001 | MERGED | `27733cc1505d` | fix(mobile): stop QR pairing to organization relays from hanging | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9002 | CLOSED | `346a125b7eb5` | feat(mobile): attach files dropped onto the iOS app | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9003 | MERGED | `05561b406935` | fix(media): keep transparency in image thumbnails with WebP | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補 |
| #9004 | CLOSED | `e2474bf7f760` | relay: send 44101 on channel delete and moderation kick | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9005 | MERGED | `15135c9db900` | feat(loadgen): model desktop clients and large-community shape | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9006 | OPEN | `680ed5acfd2a` | relay: refuse a reaction or deletion whose h names another channel | **skip**：拒收：新增行超過 400 字元（NOSTR.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9007 | MERGED | `210c28dc0652` | perf(mobile): evict verified-profile interest in one pass | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9008 | OPEN | `ce44a08b50ce` | fix(search): match names regardless of accents | **defer**：OPEN，head 釘在 ce44a08b50ce，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收；草稿／WIP |
| #9009 | MERGED | `12e6d5b74fc2` | fix(mobile): show progress after pairing QR scans | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9010 | MERGED | `291ca2783211` | fix(ios): saturate the push dedupe cutoff so extreme timestamps can't crash | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9011 | CLOSED | `2077924c593c` | fix(desktop): collapse a membership run into one timeline row | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9012 | MERGED | `23735c0590ca` | perf(relay): keep 1 s read caches warm when the pool is saturated | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9013 | MERGED | `063ad66abb09` | fix(mobile): size reply labels correctly with Bold Text | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9014 | CLOSED | `e7471f210995` | feat(relay): post no join or leave notices for guests in announce channels | **skip**：closed 未合併；拒收：新增行超過 400 字元（NOSTR.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9015 | MERGED | `d79937670a38` | docs(nip-fa): define agent grant, assertion and revocation routes | **skip**：拒收：新增行超過 400 字元（docs/nips/NIP-FA.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9016 | MERGED | `446d31fe3d3b` | fix(loadgen): bound desktop reads at stop, keep timely EOSEs, model presence and probes | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9017 | CLOSED | `94b12e43e6ec` | feat(channels): record admission roles in join notices | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9018 | OPEN | `450acb253c24` | feat(mobile): configure hosted account and relay endpoints at build time | **defer**：OPEN，head 釘在 450acb253c24，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9019 | MERGED | `28980c1cf004` | feat(relay): match verified names in profile search | **skip**：拒收：新增行超過 400 字元（migrations/0081_nip_fi_profile_head_names.sql），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9020 | MERGED | `801476ac20fe` | feat(cli): Buzz desktop as a credential provider | **defer**：已合併，但合進非 main 分支（elrond/cli-credential-chain），內容不一定經 commit 軸抵達 main；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補 |
| #9021 | MERGED | `4355d50af2aa` | mobile: tap the settings version footer to copy it | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9022 | OPEN | `6ba49663a44d` | fix(mobile): sanitize images picked as file attachments | **defer**：OPEN，head 釘在 6ba49663a44d，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9023 | OPEN | `8613ae03c9d7` | feat(mobile): accept drag and drop of files on iOS | **defer**：OPEN，head 釘在 8613ae03c9d7，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9024 | OPEN | `e724f24378bd` | feat(mobile): run the iOS app full screen on iPad | **defer**：OPEN，head 釘在 e724f24378bd，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9025 | OPEN | `cb1f03265a8b` | feat(mobile): send with hardware Enter in the composer | **defer**：OPEN，head 釘在 cb1f03265a8b，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9026 | MERGED | `ca7d5f42b234` | fix(mobile): keep a sent thread reply above the composer | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9027 | CLOSED | `0e0cabf9a10f` | fix(ios): dismiss the attachment popover on any outside touch | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9028 | MERGED | `1b39b93584ef` | fix(mobile): show organization sign-in after pairing | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9029 | MERGED | `c6474c4faea6` | feat(mobile): back up nsec to org builderlab account | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9030 | MERGED | `7b0e69bda99f` | fix(mobile): show newly created remote agents in the new-chat picker | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9031 | OPEN | `7934d83ec9ac` | feat: implement workflow send_dm and add edit_message action | **defer**：OPEN，head 釘在 7934d83ec9ac，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9032 | MERGED | `127b09faf3b8` | fix(db): use ScratchDb in the storage usage delivery test | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9033 | MERGED | `71689b47087a` | fix(desktop): show upgrade guidance (BUZZ-517) | **skip**：拒收：新增行超過 400 字元（desktop/src-tauri/tests/fixtures/nip_fi/buzz_main_6b8a72e835_optional.json, desktop/src-tauri/tests/fixtures/nip_fi/buzz_main_6b8a72e835_optional_capable.json, desktop/src-tauri/tests/fixtures/nip_fi/buzz_main_6b8a72e835_required.json），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9034 | MERGED | `256063f9552f` | mobile: start new agents on Sonnet at medium effort | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9035 | MERGED | `274d4992ee45` | fix(relay): read kind:39000/39001 inputs behind the replacement lock | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9036 | MERGED | `f24234d319af` | mobile: invite new users to create their first agent with a bold card | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9037 | OPEN | `cb35d4b5e87d` | fix(relay): expose agent identity separately from channel roles | **defer**：OPEN，head 釘在 cb35d4b5e87d，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9038 | OPEN | `df68f3b40d3c` | fix(relay): publish group state from a locked channel read | **defer**：OPEN，head 釘在 df68f3b40d3c，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9039 | CLOSED | `dd941b98096e` | feat: add Condensed conversation density | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9040 | MERGED | `83e93a3d36d8` | refactor(relay): remove database usage-metric queries | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9041 | OPEN | `3232eda06f0e` | feat: add wait_for workflow step | **defer**：OPEN，head 釘在 3232eda06f0e，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；草稿／WIP |
| #9042 | MERGED | `8076d3734a8a` | fix(mobile): close the community switcher when the org relay refuses the key | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9043 | OPEN | `ce8b7f21d21f` | feat(relay): serve storage usage as an operator pull feed | **defer**：OPEN，head 釘在 ce8b7f21d21f，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；草稿／WIP |
| #9044 | CLOSED | `92c735a219a5` | Add attachment drag forwarding | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9045 | MERGED | `91ea7c292c62` | [buzz] Recover interrupted default-channel auto-joins | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9046 | MERGED | `e2cfde363319` | mobile: refine message avatars, metadata and reply gestures | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9047 | MERGED | `b6b8c037f95b` | test(mobile): lock in invite-page and bare-host community link entry | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9049 | MERGED | `8fff8704b890` | fix(mobile): delay iOS message actions until a deliberate hold | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9050 | MERGED | `fd147bfee7e7` | Restyle mobile organization sign-in prompts as toasts | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9051 | MERGED | `e8c6cd25f8d4` | mobile: simplify verified profiles and prioritize full names | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9052 | MERGED | `b314df43f206` | relay: time every WebSocket read and every stored EVENT outcome | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9053 | OPEN | `8ea070d51e37` | fix(mobile): offer linked identity import when only other backups exist | **defer**：OPEN，head 釘在 8ea070d51e37，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9054 | CLOSED | `0d2538ec11ab` | Unhide DMs when new messages arrive | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9055 | MERGED | `8c79c3be1467` | fix(mobile): keep the composer focused through iOS inactive spells | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9056 | MERGED | `0d98bc3ea38b` | fix(mobile): send hosted relay auth with iOS custom emoji downloads | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9057 | MERGED | `1dbffb9dddd5` | Keep sign-in toasts usable at large text sizes | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9060 | MERGED | `a79a40cc5a6e` | Cache channel memberships once per user | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9061 | MERGED | `7734ddbb2813` | Expose strict code-entry pairing and live authorization bindings | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9062 | MERGED | `f8bbe7078323` | fix(mobile): bound notices to loaded message history | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9064 | OPEN | `f19781aad5c1` | fix(relay): Git pushes report and publish what actually landed | **defer**：OPEN，head 釘在 f19781aad5c1，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9065 | MERGED | `aa43c717b63a` | Make mobile New DM and Add members pick recipients like mention autocomplete | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9067 | OPEN | `4a3abc61637c` | refactor(mobile): drop client-side starter channel setup | **defer**：OPEN，head 釘在 4a3abc61637c，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9068 | CLOSED | `e1ce080d2e98` | fix(mobile): let # open channel suggestions after a selected mention | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9069 | MERGED | `963e8faa3adf` | fix(mobile): send hosted relay assertion from native media and tombstone paths | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9070 | MERGED | `f114c0e2287e` | fix(mobile): streamline identity setup and community selection | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9071 | OPEN | `6b65c3a9e23d` | mobile: let admins set who joins a channel and default channels | **defer**：OPEN，head 釘在 6b65c3a9e23d，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9072 | MERGED | `9530ecbbd726` | fix(mobile): use join template for community creation | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9073 | OPEN | `1d4fdef22160` | feat: pin channel messages (kind 40004) in the relay, SDK and CLI | **defer**：OPEN，head 釘在 1d4fdef22160，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9074 | OPEN | `84b21610b9ea` | relay: let a later NIP-IA archive request add the replacement key | **skip**：拒收：新增行超過 400 字元（docs/nips/NIP-IA.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9075 | MERGED | `01ec530b6663` | perf(db): serve single-root thread reply reads from thread_metadata | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9076 | CLOSED | `046b4f5f5895` | fix(mobile): open pasted mentions and keep prose @ queries closed | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9077 | MERGED | `3d1aa7431cc4` | fix(media): revoke private channel attachment reads | **skip**：拒收：新增行超過 400 字元（Justfile, crates/buzz-db/src/store/media_postgres_tests.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9078 | MERGED | `5bff9d58c4d6` | fix(mobile): streamline identity setup and community selection (backport #9070 to 0.27) | **defer**：已合併，但合進非 main 分支（mobile-v0.27），內容不一定經 commit 軸抵達 main；行動端變更，需 iOS／Android 原生驗收環境 |
| #9079 | MERGED | `c2a224e29e6a` | Mobile: one New chat screen | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9080 | OPEN | `20b01efba67c` | mobile: derive the open mention query from text alone | **defer**：OPEN，head 釘在 20b01efba67c，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9081 | OPEN | `d52dcad45fc0` | Keep relay-signed pull request cards for channels that follow a GitHub repository | **defer**：OPEN，head 釘在 d52dcad45fc0，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；草稿／WIP |
| #9082 | CLOSED | `ab6ebcfddbb9` | fix(search): find people by name in kind-0 search, with an opt-in users-table path | **skip**：closed 未合併；拒收：新增行超過 400 字元（TESTING.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9083 | OPEN | `f49a9eda7a91` | fix(desktop): keep a failed send's voice note when text was typed during its upload | **defer**：OPEN，head 釘在 f49a9eda7a91，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收；草稿／WIP |
| #9084 | MERGED | `5ab794d4306f` | release(mobile): push candidate tags as the operator, not the App | **skip**：拒收：新增行超過 400 字元（scripts/test-mobile-release-contract.sh），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9085 | MERGED | `a489390fa241` | fix(mobile): restore keysForNsec after the native key derivation change | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9086 | MERGED | `65372a74fba2` | fix(mobile): find verified people who have no profile | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9087 | OPEN | `6f9caa1bde3c` | feat(push-gateway): report Postgres pool utilization and checkout waits | **defer**：OPEN，head 釘在 6f9caa1bde3c，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9089 | MERGED | `aff808e23255` | fix(mobile): inflate gzip read-state snapshot responses | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9090 | OPEN | `eefce94ba01b` | perf(mobile): stop replaying stored read state on every resume | **defer**：OPEN，head 釘在 eefce94ba01b，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9091 | MERGED | `8f62e0088507` | perf(db): split newest-first events reads at a month floor so Postgres prunes partitions | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9092 | MERGED | `905d51266b1e` | fix(mobile): back off push bootstrap retries | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9093 | MERGED | `23a7d99f0ef4` | fix(mobile): skip the read-state snapshot when nothing needs publishing | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9094 | MERGED | `38baf091864c` | fix(desktop): compensate head trims from the unclamped scroll offset | **defer**：已合併，內容經 commit 軸抵達；桌面端（Tauri／Windows）變更，需實機驗收；同時動到 fork 持有修補的檔案（pnpm-lock.yaml），同步時衝突以上游為準再重做修補 |
| #9095 | MERGED | `82af4ceb773a` | fix(desktop): keep an own send out of the frozen timeline tail | **defer**：已合併，內容經 commit 軸抵達；桌面端（Tauri／Windows）變更，需實機驗收 |
| #9096 | MERGED | `9648801edcbe` | fix(db): end each table's maintenance transaction before the next | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9097 | MERGED | `5940a40611f5` | fix(db): unlock the storage-accounting lease before its session closes | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9098 | MERGED | `f0d3179b1323` | test(relay,db): remove three timing races from Postgres and E2E tests | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9099 | CLOSED | `b8a70871109a` | fix(mobile): keep agent names and roles through a reconnect | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9100 | MERGED | `cf6ff874d4bd` | fix(mobile): keep reply counts on screen while a reconnect catches up | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9101 | MERGED | `920f383d955c` | perf(mobile): validate each verified profile once, not on every publish | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9102 | OPEN | `09d0e553121a` | Retry a failed mention relay check before calling it unauthorized | **defer**：OPEN，head 釘在 09d0e553121a，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #9103 | OPEN | `f4b907a87b9e` | fix(desktop): tag the agent when replying directly to its message | **defer**：OPEN，head 釘在 f4b907a87b9e，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #9104 | OPEN | `b88721a9fa3f` | fix(mobile): mark remote agents with a cloud | **defer**：OPEN，head 釘在 b88721a9fa3f，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9105 | MERGED | `e669549285e1` | fix(mobile): show transparent avatars without a black background | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9106 | MERGED | `563f94644940` | docs(agents): add Review-Proven Rule 9, design client paths for the whole fleet | **defer**：已合併，內容經 commit 軸抵達；文件變更，隨產品同步一併帶入 |
| #9107 | MERGED | `3eb23f4c7726` | fix(mobile): offer a new identity beside saved keys on unclaimed accounts | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9108 | OPEN | `72f43b5c8f99` | WIP feat(relay): community landing channel and welcome message | **skip**：拒收：新增行超過 400 字元（NOSTR.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9109 | MERGED | `4733df5dbd2e` | perf(relay): cache the community-active check on socket admission | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9110 | MERGED | `ba4581e41a96` | buzz-db: read explicit #h sets one channel at a time | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9111 | MERGED | `818d838aa3f4` | fix(mobile): keep verified names on screen in channels with over 1,024 members | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9113 | MERGED | `b9fb17bae667` | perf(redis): index mesh ready records and share one Redis connection | **skip**：拒收：含 eval(／new Function(／global.require 樣式（crates/buzz-relay/src/tunnel/directory.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9114 | MERGED | `2d78ffa4b4ef` | docs(agents): add open-source boundary and drop private repo list | **skip**：拒收：新增行超過 400 字元（AGENTS.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9115 | MERGED | `8b66a96c739f` | mobile: reuse channel message rows that did not change | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9116 | MERGED | `bdbd4a48c130` | mobile: persist user profiles so names and avatars render on launch | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9117 | MERGED | `57c95a368199` | feat(protocol): define compact membership discovery (BUZZ-615) | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9118 | MERGED | `5c0c35400ab2` | feat(relay): project compact viewer memberships (BUZZ-615) | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9120 | MERGED | `d6d6b02eb447` | fix(mobile): focus the search field when search opens | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9121 | OPEN | `0a1bbb9da341` | feat(cli): tag the target author on `buzz reactions add` | **defer**：OPEN，head 釘在 0a1bbb9da341，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9122 | OPEN | `4ca7e0f93c87` | feat(mobile): optimistic send with iMessage-style status and retry (prototype) | **defer**：OPEN，head 釘在 4ca7e0f93c87，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9123 | MERGED | `3c03ad74be3f` | fix(mobile): start no threads in Solo chats | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9124 | OPEN | `71b5785e2cac` | fix(workflows): let agent owners trigger workflows | **defer**：OPEN，head 釘在 71b5785e2cac，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；草稿／WIP |
| #9125 | OPEN | `0279a892e1fc` | feat(relay): grow DMs in place, identified by their people | **defer**：OPEN，head 釘在 0279a892e1fc，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9126 | MERGED | `e74abf32ccf1` | perf(db): hydrate search hits with exact event timestamps | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9127 | MERGED | `0b8e8203bdba` | fix(mobile): swipe left to reply so swipe-back keeps rightward drags | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9128 | MERGED | `9a8f722831ae` | perf(db): prune post-commit push enqueue by signed event timestamp | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9129 | OPEN | `a2b47e2c6911` | fix(mobile): give large roster and read-state reads a 30s timeout | **defer**：OPEN，head 釘在 a2b47e2c6911，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9130 | MERGED | `39093b6ecea6` | perf(db): use exact event timestamps for transactional deletion | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9131 | MERGED | `49bb40fef8fc` | perf(db): plan multi-value #d reads with their values | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9132 | MERGED | `d45c14c139a8` | fix(db): keep busy-reader history reads off the writer and cap them per pod | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9133 | MERGED | `220021f8820f` | fix(mobile): delete composer chips as one unit | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9134 | MERGED | `02788901c7d1` | fix(mobile): renew expired assertions for native media and drop retired-session avatars | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9135 | MERGED | `a137b4d43325` | mobile: long-press a message link for open, copy and share | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9136 | MERGED | `233d78f1b7e0` | perf(mobile): rank search channels once per query | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9137 | MERGED | `14d93fca745c` | perf(mobile): memoize npub labels | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9138 | MERGED | `d3d5ce837a7d` | perf(mobile): show a static placeholder for posterless videos | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9139 | CLOSED | `a36361e784cf` | mobile: never fall back from a relay thumbnail to the original upload | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9140 | MERGED | `4d9d3fe0cf62` | mobile: stop re-parsing messages on every resume | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9141 | MERGED | `fdecbca77c48` | feat(mobile): tag the reacted-to message author on reactions | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9142 | MERGED | `17117ae7bf91` | mobile: add follow and remind actions to inbox row menu | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9144 | MERGED | `d80cc6ccbc0f` | test(mobile): check posterless video previews renew the relay assertion | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9145 | CLOSED | `d3a0dda7c760` | feat(cli): send the NIP-FI assertion, and mint it through the NIP-FA adapter as Desktop does | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9146 | CLOSED | `e34eea028ae2` | mobile: persist remote images on disk, per community | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9147 | OPEN | `14576a0610ca` | fix(db): seek replaceable heads by channel | **defer**：OPEN，head 釘在 14576a0610ca，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9148 | MERGED | `2c6e70729686` | fix(relay): close a WS search whose hit hydration fails instead of sending EOSE | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9149 | OPEN | `dd0ebe8bd291` | Add a community creation policy | **defer**：OPEN，head 釘在 dd0ebe8bd291，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；草稿／WIP |
| #9150 | MERGED | `e47b32c07b22` | fix(mobile): show already-loaded custom emoji in the iOS reactions sheet | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9151 | MERGED | `9942be2ab71f` | mobile: start new agents on the server-recommended model | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9152 | MERGED | `6f3e9fa9be72` | fix(mobile): keep Home's header clean under sheets | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9153 | OPEN | `401d18230555` | feat(mobile): add people and agents to a DM | **defer**：OPEN，head 釘在 401d18230555，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9154 | MERGED | `a0e3aad9ae0f` | feat(relay): log WebSocket EVENT writes on the access target | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9155 | MERGED | `67f643cd4564` | fix(mobile): confirm before starting a Huddle from the header | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9156 | OPEN | `fa4c91f008a7` | fix(mobile): only say "Community changed" when the community changed | **defer**：OPEN，head 釘在 fa4c91f008a7，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9157 | MERGED | `fd63c8194e90` | perf(db): stop the events recent pass at a ceiling for regular-kind reads | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9158 | MERGED | `6ef82c8e8c13` | perf(mobile): keep remote images on disk and show small ones as thumbnails | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9159 | OPEN | `cef50110d20d` | fix(push): limit public request work | **defer**：OPEN，head 釘在 cef50110d20d，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9160 | OPEN | `6533f5fd0a89` | fix(push): limit deliveries per relay | **skip**：拒收：新增行超過 400 字元（docs/push-gateway-deployment.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9161 | OPEN | `ec6b359baaae` | fix(push): retain pending opt-outs until revoked | **defer**：OPEN，head 釘在 ec6b359baaae，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9163 | MERGED | `b5c3fc607769` | feat(mobile): long-press a Solo chat to open its details sheet | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9164 | MERGED | `ac02ada17bda` | test(mobile): drop the video preview step removed with native frame loading | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9165 | OPEN | `574f534afcaa` | test(mobile): remove stale video preview assertions | **defer**：OPEN，head 釘在 574f534afcaa，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9166 | OPEN | `9280c788fece` | docs: refresh README feedback community invite | **defer**：OPEN，head 釘在 9280c788fece，合併後走 commit 軸；文件變更，隨產品同步一併帶入；草稿／WIP |
| #9167 | MERGED | `12f4d4af3678` | fix(mobile): shimmer loading photos in the iOS carousel | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9168 | MERGED | `dabddf988201` | fix(cli): list DMs, attach any file, validate kinds, default the relay | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9169 | MERGED | `3850c6bf6416` | fix(relay): say "channel owner or admin" in the call_webhook save refusal | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9170 | MERGED | `3f09cb33e831` | feat(relay): runtime-tunable history-read and AUTH concurrency caps via feature flags | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補 |
| #9171 | MERGED | `2e717a80dde7` | mobile: make the first-agent card stand out in dark mode | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9172 | CLOSED | `b3d067e87877` | feat(relay): add FI default for new communities | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9173 | MERGED | `229105cc4039` | fix(mobile): show the channel name as the notification subtitle | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9174 | MERGED | `aedb3f1f4dae` | fix(relay): regenerate missing image thumbnails on request | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9175 | MERGED | `fe0970ab28e4` | fix(mobile): read-state gzip sync and new identity beside saved keys (backport #9089, #9093, #9107 to 0.27) | **defer**：已合併，但合進非 main 分支（mobile-v0.27），內容不一定經 commit 軸抵達 main；行動端變更，需 iOS／Android 原生驗收環境 |
| #9176 | MERGED | `33a1c0bb87a6` | Manage community NIP-FI policy with enable, disable and status | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補 |
| #9177 | OPEN | `df4add6a112a` | fix(relay): retry push wakes when the deletion lease check times out | **defer**：OPEN，head 釘在 df4add6a112a，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9178 | OPEN | `bcb80800342d` | perf(relay): skip fan-out access reads with no local subscriber and mention reads without '@' | **defer**：OPEN，head 釘在 bcb80800342d，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9179 | OPEN | `d472447031d9` | perf(media): read the sidecar once per media GET | **defer**：OPEN，head 釘在 d472447031d9，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9180 | OPEN | `81f85421bd0e` | fix(relay): reject NUL bytes at ingest and close a backfill that cannot be delivered | **defer**：OPEN，head 釘在 81f85421bd0e，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9182 | MERGED | `d4f4afd39f4d` | feat(loadgen): model agent turns and sustained holds | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9183 | OPEN | `27b9cafe64b5` | fix(relay): reject NUL bytes in read filters | **defer**：OPEN，head 釘在 27b9cafe64b5，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9184 | MERGED | `6936bee1d4d9` | Add avatar color backdrop to mobile agent creation | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9185 | MERGED | `d20666f23a27` | Show mobile floating dates while scrolling | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9186 | CLOSED | `6bbf0005757e` | feat(mobile): bring Activity feed and filters to mobile | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9187 | CLOSED | `854ac071019e` | Refine mobile Home and Inbox spacing | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9188 | OPEN | `56dd2c3ea8fc` | feat(mobile): add agents section to settings page | **defer**：OPEN，head 釘在 56dd2c3ea8fc，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9189 | OPEN | `47b6ce96c8ef` | feat(mobile): allow owners to edit remote agent instructions | **defer**：OPEN，head 釘在 47b6ce96c8ef，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9191 | MERGED | `7fe3e6f9c3fc` | feat(cli): manage sidebar sections with `buzz sidebar sections` | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9192 | MERGED | `34eddf00f978` | Pin sqlx to the upstream fix for a cancelled BEGIN | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補 |
| #9193 | CLOSED | `dc940d87fab5` | feat(mobile): move Inbox to Home bell and align spacing | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9194 | OPEN | `38798a49806b` | feat(desktop): add "Also send to channel" to the thread composer | **defer**：OPEN，head 釘在 38798a49806b，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收；草稿／WIP |
| #9195 | MERGED | `d1ba7ee67781` | fix(relay): deliver multi-node fan-out concurrently and never drop silently | **skip**：拒收：新增行超過 400 字元（ARCHITECTURE.md, Justfile），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9196 | MERGED | `d9b63b2e3eda` | fix(cli): clearer desktop pairing errors, paired default relay, and auth desktop list | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9197 | MERGED | `e3e8ccf5a8eb` | perf(db): bound since-limited events reads with the month-floor literal | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9198 | OPEN | `bae11caf0b3d` | fix(media): run thumbnail regeneration tests in CI and cap rebuild pixels | **defer**：OPEN，head 釘在 bae11caf0b3d，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9199 | MERGED | `85d3a2858c59` | perf(relay): serve restriction rows for 10 s with cross-pod invalidation | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9200 | MERGED | `6aea653362d2` | fix(db): keep retained fence proofs when a probe fails | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9202 | OPEN | `ac4fa22db5d2` | fix(cli): treat a retried sidebar write the relay already stored as success | **defer**：OPEN，head 釘在 ac4fa22db5d2，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9203 | OPEN | `d106503ae114` | fix(channels): reject invisible channel names | **skip**：拒收：含零寬／雙向控制字元（crates/buzz-db/src/store/channel_name_postgres_tests.rs, crates/buzz-relay/src/handlers/channel_name_postgres_tests.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9204 | MERGED | `2d4807505bda` | fix(mobile): match Agents sign-in to Home’s reconnect capsule | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9206 | MERGED | `34e2e653d723` | perf(loadgen): spread seed writes across channel creators | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9209 | CLOSED | `bfcc40a72c55` | release(mobile): backport tag-as-operator to mobile-v0.27 | **skip**：closed 未合併；拒收：新增行超過 400 字元（scripts/test-mobile-release-contract.sh），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9210 | OPEN | `c75ed5738bfc` | refactor(db): rename since_prunes to since_above_floor | **defer**：OPEN，head 釘在 c75ed5738bfc，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9211 | MERGED | `bf16a1e0aba1` | Allow operators to set initial NIP-FI policy on create | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9212 | MERGED | `e54bf0cc9641` | feat(mobile): move Activity to a Home bell and align Home spacing | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9213 | MERGED | `6999bb9a8d2e` | feat(mobile): rename Activity and add header filters | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9214 | MERGED | `9655a90419e6` | fix(relay): set received_at in the system-channel fan-out test helper | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9215 | MERGED | `b2414cf6d88a` | fix(mobile): read only shown events from filtered Activity rows | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9216 | OPEN | `4bcf2a417131` | fix(mobile): keep forum unreads off the app badge | **defer**：OPEN，head 釘在 4bcf2a417131，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9221 | CLOSED | `34a1a69b6f67` | docs(agents): RFC for community-managed webhook runtimes | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9222 | OPEN | `99c07da83aee` | perf(relay): index default channels and read them from the replica at AUTH | **defer**：OPEN，head 釘在 99c07da83aee，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9223 | OPEN | `1b7d0e691076` | fix(relay): gate git repos on the name registry | **defer**：OPEN，head 釘在 1b7d0e691076，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9224 | MERGED | `4ebb7554c6d4` | feat(mobile): one Builderlab per build, internal and public distributions | **skip**：拒收：新增行超過 400 字元（docs/adr/0001-internal-and-public-mobile-builds.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9225 | MERGED | `e98c10922038` | fix(mobile): request hosted relay assertions only when NIP-FI is required | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9226 | MERGED | `c630c4ebf0b2` | fix(cli): preserve attachments across successive edits | **skip**：拒收：新增行超過 400 字元（crates/buzz-db/src/store/media.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9227 | OPEN | `8d3d43bf1847` | feat(workflow): add owner-only agent mentions for workflow messages | **defer**：OPEN，head 釘在 8d3d43bf1847，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補；草稿／WIP |
| #9228 | MERGED | `d5a9ecf8b8e7` | fix(ios): mint hosted NIP-FI assertions in the notification extension | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9229 | OPEN | `f4dc6ddf3d02` | fix(relay): apply ingest's content checks to workflow SendMessage | **defer**：OPEN，head 釘在 f4dc6ddf3d02，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；草稿／WIP |
| #9230 | OPEN | `88d76f7f1d94` | fix(relay): saturate filter limits instead of casting | **defer**：OPEN，head 釘在 88d76f7f1d94，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9231 | OPEN | `ca729388a74b` | fix(relay): share one overflow-free created_at skew check | **defer**：OPEN，head 釘在 ca729388a74b，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；草稿／WIP |
| #9232 | MERGED | `752d97fec575` | fix(mobile): hosted NIP-FI assertions (backport #9056, #9069, #9134, #9225, #9228 to 0.27) | **defer**：已合併，但合進非 main 分支（mobile-v0.27），內容不一定經 commit 軸抵達 main；行動端變更，需 iOS／Android 原生驗收環境 |
| #9233 | OPEN | `ae7d4ec0b9e1` | fix(relay): make filters with an empty set match nothing in SQL | **defer**：OPEN，head 釘在 ae7d4ec0b9e1，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；草稿／WIP |
| #9234 | OPEN | `a0987ab65b10` | fix(relay): keep database error text off WebSocket replies | **defer**：OPEN，head 釘在 a0987ab65b10，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9235 | MERGED | `3d067a8b4dcc` | fix(relay): deliver slow cross-node events late instead of closing their recipients | **skip**：拒收：新增行超過 400 字元（ARCHITECTURE.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9236 | OPEN | `23afef733e68` | fix(relay): parse env settings strictly and refuse invalid values | **defer**：OPEN，head 釘在 23afef733e68，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；草稿／WIP |
| #9237 | OPEN | `33cab2c61a53` | fix(mobile): keep an internal build's session across relaunch; any Builderlab host on iOS | **defer**：OPEN，head 釘在 33cab2c61a53，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9238 | OPEN | `827b59509779` | fix(desktop): adopt unpinned Welcome agents during provisioning | **defer**：OPEN，head 釘在 827b59509779，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #9239 | OPEN | `38fd83bf881f` | docs(agents): RFC for community-managed application agents | **skip**：拒收：新增行超過 400 字元（docs/external-agent-webhook-rfc.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9240 | CLOSED | `b09cbb884f53` | fix(relay): require private visibility for direct messages | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9241 | MERGED | `c9da22b91a98` | fix(mobile): keep Home bell tappable while scrolled | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9242 | OPEN | `f55868e7b833` | fix(workflow): replace NUL in webhook output and trigger fields | **defer**：OPEN，head 釘在 f55868e7b833，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9243 | MERGED | `8579f4f60cb5` | fix(mobile): read mentions taller than the screen | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9245 | MERGED | `7793cfafe3f4` | Record why relay connections close and quiet close warnings | **skip**：拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9246 | MERGED | `07e9da8cd0c5` | feat: send a User-Agent on relay WebSocket upgrades | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9247 | CLOSED | `8d8d97e58d75` | test(mobile): swipe left in the message link reply tests | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9248 | OPEN | `ae90540bd799` | feat(mobile): prefill the agents you last tagged in a conversation | **defer**：OPEN，head 釘在 ae90540bd799，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9249 | MERGED | `330805cfc413` | fix(mobile): steady New DM picker rows and animate picks | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9250 | OPEN | `c048fca27bc6` | feat(mobile): put your Bestie first among your agents in pickers | **defer**：OPEN，head 釘在 c048fca27bc6，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9251 | OPEN | `dd32b8250b8b` | feat(mobile): start a Solo chat from a message or inbox row | **defer**：OPEN，head 釘在 dd32b8250b8b，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9253 | OPEN | `1b619472cda1` | fix(mobile): join an open channel from the chat footer | **defer**：OPEN，head 釘在 1b619472cda1，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9254 | OPEN | `b836cb25d754` | fix(mobile): hide Bestie launcher animation on self-hosted communities (#9244) | **defer**：OPEN，head 釘在 b836cb25d754，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9255 | MERGED | `73efa3514030` | feat(mobile): consolidate Solo chat settings in one sheet | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9256 | CLOSED | `ba10e48fbdfa` | mobile: add opt-in native hard-edge navigation | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9258 | CLOSED | `a1d4378f1c2e` | feat(desktop): ephemeral read receipts with Seen indicator | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9259 | MERGED | `2b5bac3075f3` | Add swipeable photo stacks and native iOS gallery preview | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9260 | OPEN | `93a791df772d` | mobile: add opt-in hard-edge navigation and alignment | **defer**：OPEN，head 釘在 93a791df772d，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9262 | OPEN | `eae9feeb1600` | mobile: show account communities in the switcher and sync saved destinations | **defer**：OPEN，head 釘在 eae9feeb1600，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9263 | OPEN | `801d4f832371` | fix(mobile): name the failing step in sign-in errors | **defer**：OPEN，head 釘在 801d4f832371，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9264 | CLOSED | `5e1e409e8e48` | docs(nip-fa): name the browser-login callback errors a client may act on | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9265 | MERGED | `8e3140dded19` | feat(relay): let an operator mint invites for a community owner or admin | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9266 | OPEN | `2d658f7a61a6` | fix(mobile): sync communities with the Builderlab account's known list | **defer**：OPEN，head 釘在 2d658f7a61a6，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9267 | MERGED | `50634902f9e6` | [buzz] Recover database pool capacity after stalled connections | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；同時動到 fork 持有修補的檔案（Cargo.lock），同步時衝突以上游為準再重做修補 |
| #9268 | OPEN | `b09cbb884f53` | fix(relay): require private visibility for direct messages | **defer**：OPEN，head 釘在 b09cbb884f53，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9269 | MERGED | `59726dabbf81` | Enable mobile huddles with Codex agents | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9270 | MERGED | `e933fee6dfbd` | NEXUS-4336: Wait for desktop-provider socket ownership proof | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9271 | OPEN | `e803da93c68e` | feat(mobile): opening a channel quiets its list row | **defer**：OPEN，head 釘在 e803da93c68e，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9272 | MERGED | `80db5f58e7d0` | test(relay): give every media e2e upload its own blob hash | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9273 | MERGED | `dcaecb34852d` | test: fix timing-dependent unit tests in buzz-cli, buzz-agent and buzz-admin | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9274 | MERGED | `bdf8ab645add` | fix(ci): classify hermit retry timeouts by watchdog kill, not whole seconds | **defer**：已合併，內容經 commit 軸抵達；腳本／工具變更，隨產品同步一併帶入 |
| #9275 | MERGED | `01c224e68ff4` | test(ios): wait for a key, foreground-active window before presenting in RunnerTests | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9276 | OPEN | `53192ba1443d` | fix(desktop): start the message target highlight when the row is on screen | **defer**：OPEN，head 釘在 53192ba1443d，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #9277 | MERGED | `0737d665bc16` | test(desktop): wait on real readiness signals in audience and community-rail specs | **defer**：已合併，內容經 commit 軸抵達；桌面端（Tauri／Windows）變更，需實機驗收 |
| #9278 | OPEN | `5fb1e10d1f36` | [buzz] Log minimal APNs rejection diagnostics without personal data | **defer**：OPEN，head 釘在 5fb1e10d1f36，合併後走 commit 軸；腳本／工具變更，隨產品同步一併帶入；草稿／WIP |
| #9279 | CLOSED | `782b6b26d235` | fix(relay): distinguish unavailable tenant lookups from missing hosts | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9280 | OPEN | `598acbf040a6` | fix(github): pin API version 2026-03-10 for the Buzz releases lookup | **defer**：OPEN，head 釘在 598acbf040a6，合併後走 commit 軸；web 前端變更，需瀏覽器與部署驗收 |
| #9281 | OPEN | `1138ace5605c` | ci: prevent Codex review hangs from retained log streams | **defer**：OPEN，head 釘在 1138ace5605c，合併後走 commit 軸；CI workflow 變更，未動 fork 修補的檔案；fork 的 main CI 沒有紅燈觸發採用；草稿／WIP |
| #9282 | MERGED | `1e036068c54a` | Add invite preview video and fallback poster | **skip**：拒收：新增行超過 400 字元（previews/invite-video/README.md, previews/invite-video/preview.js），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9283 | OPEN | `56c02a43f6be` | fix(mobile): let a mouse drag scroll lists | **defer**：OPEN，head 釘在 56c02a43f6be，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9284 | OPEN | `15ff7d888139` | feat(mobile): sync Builderlab known communities across devices | **defer**：OPEN，head 釘在 15ff7d888139，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9285 | OPEN | `c95758507e65` | feat(relay): index reactions under their target author for #p reads | **defer**：OPEN，head 釘在 c95758507e65，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9286 | MERGED | `d35a9a08c56c` | fix(mobile): show observed thread replies in Activity | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #9287 | MERGED | `1013c30aff99` | fix: unblock image audit with patched MCP SDK | **defer**：已合併，內容經 commit 軸抵達；依賴鎖檔／政策變更，fork 的鎖檔升級與 deny.toml 修補須在同步時重做 |
| #9288 | MERGED | `23d7c713395a` | feat(ci): allow admin dispatch of desktop candidate validation | **defer**：已合併，內容經 commit 軸抵達；CI workflow 變更，未動 fork 修補的檔案；fork 的 main CI 沒有紅燈觸發採用 |
| #9289 | MERGED | `d6d3295eb95f` | perf(mobile): reuse the owned agent directory for Codex voice | **defer**：已合併，但合進非 main 分支（mobile-codex-huddle-20261108），內容不一定經 commit 軸抵達 main；行動端變更，需 iOS／Android 原生驗收環境 |
| #9290 | OPEN | `b98dcc063037` | docs(vision): add information flow vision for agents | **skip**：拒收：新增行超過 400 字元（NOSTR.md, VISION_INFORMATION_FLOW.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9291 | MERGED | `d8857138c56f` | fix: inline ARM64 atomics in Sprig image build | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9292 | OPEN | `42b31525aa4b` | fix(mobile): add agents to channels with the bot role | **defer**：OPEN，head 釘在 42b31525aa4b，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9293 | CLOSED | `a61492fcbec6` | fix(desktop): refresh relay agents after adding an agent to a channel | **skip**：closed 未合併，上游未收；標題與檔案清單看不出 Windows／CJK 專屬缺陷，不採用 |
| #9294 | MERGED | `41edb5cd9d01` | fix(mobile): label Activity rows by the event they show | **defer**：已合併，但合進非 main 分支（kennylopez-mobile-thread-activity-20261109），內容不一定經 commit 軸抵達 main；行動端變更，需 iOS／Android 原生驗收環境 |
| #9295 | OPEN | `eb2f48375c97` | fix(mobile): keep a thread tail behind the keyboard unread | **defer**：OPEN，head 釘在 eb2f48375c97，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9296 | MERGED | `a223481eb434` | docs: point the README to Buzz 1.0 in block/buzz-app | **defer**：已合併，內容經 commit 軸抵達；文件變更，隨產品同步一併帶入 |
| #9297 | MERGED | `d3739c190a22` | fix(db): give the replica-fence probe its own pool and instrument it | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9298 | OPEN | `c898c4e7eaab` | docs(mobile): add REVIEWING.md with mobile review principles | **defer**：OPEN，head 釘在 c898c4e7eaab，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |
| #9300 | OPEN | `6407c9db7122` | feat(mobile): link to Builderlab web from Settings | **defer**：OPEN，head 釘在 6407c9db7122，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #9301 | OPEN | `35f8cda95b44` | Add operator identity retirement with a durable execution hold | **skip**：拒收：新增行超過 400 字元（docs/database.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9302 | MERGED | `aa2bf78d2d16` | fix(relay): never close connections when cross-node fan-out falls behind | **skip**：拒收：新增行超過 400 字元（ARCHITECTURE.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9303 | MERGED | `55260c24ffb3` | Add manual-only relay image publishing | **defer**：已合併，內容經 commit 軸抵達；CI workflow 變更，未動 fork 修補的檔案；fork 的 main CI 沒有紅燈觸發採用 |
| #9304 | OPEN | `21df5ece379b` | Keep community deletion working across a new tenant table's migration | **skip**：拒收：新增行超過 400 字元（docs/database.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9305 | OPEN | `3f00a616ebbc` | fix(relay): bound each cross-node delivery attempt | **skip**：拒收：新增行超過 400 字元（ARCHITECTURE.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9306 | MERGED | `eac46e230ff9` | Serve video and poster previews for invite links | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #9307 | OPEN | `9e28cfbdadb8` | Refuse opening a private channel that has other members | **skip**：拒收：新增行超過 400 字元（NOSTR.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #9308 | OPEN | `abb803103ffd` | fix(relay): bound invite preview host lookup | **defer**：OPEN，head 釘在 abb803103ffd，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；草稿／WIP |
| #9309 | MERGED | `228ecee91c46` | fix(mobile): bump Flutter to 3.47.9 for Android TLS fix | **defer**：已合併，內容經 commit 軸抵達；腳本／工具變更，隨產品同步一併帶入 |
| #9310 | MERGED | `24dd2bc7582a` | ci(docker): skip relay image publishes for main pushes outside the build context | **defer**：已合併，內容經 commit 軸抵達；CI workflow 變更，與 fork 的 workflow 修補（.github/workflows/docker.yml）衝突，同步時一併重做 |
| #9311 | OPEN | `a5fc23be5fc9` | fix(mobile): list known people in recipient pickers before a name is typed | **defer**：OPEN，head 釘在 a5fc23be5fc9，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境；草稿／WIP |

## Issue 軸（25 筆）

| Issue | 狀態 | 標題 | 裁決與理由 |
| --- | --- | --- | --- |
| #8927 | closed | Follow-ups to unique listed channel names: starter channels on the relay, remove the operator rename | **defer**：已 closed 的後續追蹤（starter channel 在 relay 端、移除 operator rename）；對應的 relay 修正 5f8d0aa 與桌面 f99807a 已在 commit 軸裁決，隨產品同步一併帶入 |
| #8950 | open | feat(acp): send `additionalDirectories` at session start, with per-agent extra folders | **skip**：ACP additionalDirectories 的功能請求，非缺陷 |
| #8980 | open | Workflow send_message: optional username and avatar (Slack webhook parity) | **skip**：workflow send_message 加 username／avatar 的功能請求，非缺陷 |
| #8992 | open | Agent owners can't edit, pause, or trigger workflows their agent created | **defer**：agent 擁有者無法管理 agent 建立的 workflow（relay 回 forbidden）；產品權限缺陷，等上游修正 commit 隨軸帶入 |
| #9048 | open | Desktop: a transient relay query failure during send-time mention revalidation shows "Could not authorize a mentioned agent" (no retry) | **defer**：Desktop 送訊時 mention 重驗遇暫時性 relay 查詢失敗就報「Could not authorize a mentioned agent」且不重試；桌面行為缺陷，等上游修正，fork 無桌面實機驗收 |
| #9059 | open | feat(deep-link): Open channels with prefilled message drafts | **skip**：deep link 帶預填草稿的功能請求，非缺陷 |
| #9063 | open | Cloudflare Workers get error 526 from my communities.buzz.xyz relay | **skip**：Cloudflare Worker 對 communities.buzz.xyz 託管 relay 得到 526；是上游託管服務與 Cloudflare 設定問題，fork 沒有該服務 |
| #9066 | open | Desktop 0.7 preview: canvas side panel opens in edit mode only, with no rendered (read) view | **defer**：Desktop 0.7 preview（macOS）canvas 側欄只有編輯模式、沒有唯讀渲染；桌面產品行為，等上游 |
| #9088 | open | Feature request: per-community origin-scoped gateway authentication headers in Buzz Desktop | **skip**：Desktop 對自架社群附加 origin 範圍閘道驗證標頭的功能請求，非缺陷 |
| #9112 | open | Preview PDFs and spreadsheets in chat without downloading | **skip**：聊天中預覽 PDF／試算表的功能請求，非缺陷 |
| #9181 | open | buzz-app: allow explicitly tool-less ACP sessions without HTTP MCP support | **skip**：屬於 block/buzz-app（不在 block/buzz 程式碼內）的 ACP 工具列表議題；fork 不含該程式 |
| #9190 | closed | desktop: "Add agents" lists personas only, so an agent running outside the desktop cannot be added to a channel | **defer**：已 closed；桌面「Add agents」只列 persona、看不到外部執行的 agent；產品行為，若有修正 commit 隨軸帶入 |
| #9201 | open | feat(cli): idempotent `buzz sidebar sections apply` for declarative sidebar layouts | **skip**：buzz sidebar sections apply 的功能請求，非缺陷 |
| #9205 | open | desktop/harness: DM messages are dropped when the DM channel has no dm metadata | **defer**：desktop／harness 在 DM 頻道缺 dm metadata 時丟訊息；產品缺陷，等上游修正 |
| #9207 | open | buzz-acp: provider quota/billing exhaustion (429/402) is retried for ~25 min, then the message is dropped and the author isn't notified | **defer**：buzz-acp 把供應商配額／餘額耗盡（429／402）當暫時性錯誤重試約 25 分鐘後丟棄；fork 不改 buzz-agent／acp 行為，等上游修正 |
| #9208 | open | buzz-acp: a failed steer/interrupt cancel (error or idle timeout) goes through plain requeue(), losing the steer framing and any cancelled carryover | **defer**：buzz-acp 的 steer／interrupt cancel 失敗改走一般 requeue、遺失 steer 框架；fork 不改 acp 行為，等上游修正 |
| #9217 | open | Mobile: derive the app badge from the channel list's highlight state | **skip**：行動端 app badge 改由頻道列表 highlight 推導的重構提案，非缺陷 |
| #9218 | open | Mobile: app badge can over-count before read state is ready | **defer**：行動端 app badge 在 read state 就緒前可能多算；行動端需原生驗收，等上游修正 |
| #9219 | open | Mobile: refresh the app badge when read state changes on another device | **skip**：行動端在另一裝置讀取後刷新 badge 的功能請求，非缺陷 |
| #9220 | open | Feature request: community-managed agents with an open runtime contract and per-user access control | **skip**：社群層級代管 agent 與開放 runtime 契約的功能請求，非缺陷 |
| #9244 | open | Mobile: Bestie launcher shows on self-hosted communities, where it can’t work | **defer**：行動端 Bestie 啟動鈕在自架社群顯示但不可用；行動端需原生驗收，等上游修正 |
| #9252 | open | iOS: Solo workspaces can be created but not deleted | **skip**：iOS Solo workspace 無法刪除；作者自述是缺少功能的請求，行動端，非缺陷回報 |
| #9257 | open | Mobile: Hide unused Solo filter or provide a setting and explain its empty state | **skip**：行動端隱藏空的 Solo 篩選或加設定的 UX 請求，非缺陷 |
| #9261 | open | Desktop shows Claude Code as Ready with an empty model dropdown when the adapter rejects initialize (claude-agent-acp 0.101.0) | **defer**：Desktop 在 claude-agent-acp 0.101.0 拒絕 initialize 時仍顯示 Claude Code「Ready」且模型下拉為空；桌面行為缺陷，等上游修正 |
| #9299 | open | Design question: one signed receipt per billable turn and per paid job | **skip**：每次計費回合一份簽章收據的設計提問，非缺陷 |
