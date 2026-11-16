# 2026-11-02 上游差異裁決

接續 [2026-10-30 裁決](UPSTREAM_REVIEW_2026-10-30.md)。範圍：commit `6d719c680a85c98153324809988be37425fba73e..d342cf141cb3211c8e5a6c74f881cf1d39ad3b12`（84 筆）；PR #8700–#8920 中檢查器列出的 195 筆；issue 15 筆（state=all）。機器證據（SHA、diff SHA-256、檔案清單、掃描命中）在 [JSON](UPSTREAM_REVIEW_2026-11-02.json)。

## 結論

- commit：84 筆，1 adopt、8 skip、75 defer（`c609d33e8c3e` 於 2026-11-07 由 defer 改 adopt，見下方「2026-11-07 修訂」）。
- PR：195 筆，1 adopt、55 skip、139 defer（#8711 同上）。
- issue：15 筆，0 adopt、5 skip、10 defer。

原審查時沒有 adopt：fork 的政策是產品行為與上游相同、不自行分岔（FORK.md），而這批變更橫跨行動端、桌面端、relay 與資料庫，fork 沒有對應的原生與 Postgres 驗收環境，採用等於未經驗收的產品改動。defer 項目的唯一出路是 ROADMAP「同步延後變更」整批帶入。沒有宣稱產品已同步、CI 已跑或告警已解除。

## 2026-11-07 修訂：兩項由 CI 紅燈觸發的 adopt

原結論的「fork 不自行分岔產品」針對產品行為；下面兩項只動 CI 與依賴政策，不改產品行為，且 fork 的 `main` 因它們實際紅燈，所以例外採用。皆以 `git cherry-pick -s -x` 逐字帶入，保留上游作者與 `(cherry picked from ...)` 行。

| 上游 | 觸發的紅燈 | 帶入內容 | 驗證與限制 |
| --- | --- | --- | --- |
| `c609d33e8c3e` / #8711（原 defer） | Mobile (Android)：`The Java version used for the build is 25.0.5, which is incompatible with Gradle 8.14.5`（ubuntu-latest 已是 26.04） | `.github/workflows/_ci-clients.yml` 在 `matrix.lane == 'android'` 加 `actions/setup-java`（temurin 17，釘 v6.1.0 的完整 SHA `b843ebf9b913`） | 無衝突；YAML 可解析。Android lane 能否變綠只有遠端 CI 能證明，本機未跑 |
| `c9b8f1176ece` / #8922（審查範圍 `d342cf1` 之後，新項目） | Security / Dependency policy（`cargo-deny check`）：RUSTSEC-2026-0433（pulldown-cmark 0.13.5）、RUSTSEC-2026-0429（zip 8.6.0） | `Cargo.lock` pulldown-cmark → 0.13.6；`deny.toml` 加 0429 ignore，與同路徑的 0367／0368／0369 同理由 | 本機 `cargo deny check advisories` 通過；`cargo tree -i zip@8.6.0 --locked` 確認 zip 8.6.0 在根目錄鎖檔只經 `buzz-mesh-smoke`（dev-dependencies）→ mesh-llm 0.76.2 到達，ignore 理由在 fork 仍成立 |

- 水位不動：#8922 在 `d342cf1`／PR 8920 之後，仍屬下次審查範圍；這裡只記它已因 CI 紅燈提前採用。#8711 在已審範圍內，只是改判。
- 沒有宣稱 CI 已綠。`desktop/src-tauri/Cargo.lock` 另有 zip 8.6.0，但 CI 的 `cargo-deny check` 只掃根目錄鎖檔，本次未處理；歸「隨上游遷移 rmcp、glib 與 lru 依賴鏈」那類盤點。
- 之前 defer 理由寫「與 fork 的 workflow 修補衝突」對 #8711 不成立：`_ci-clients.yml` 沒有 `fork patch` 標記也不在 FORK.md 修補表。其他 CI workflow commit 仍須逐一確認，不因此類推。

## 方法與掃描界限

commit：gh api repos/block/buzz/commits/<SHA> 的 diff；PR：pulls/<n> metadata（base／head SHA）加目前 head 的 diff；issue：issues/<n>（state=all 清單）。掃描只看新增行。

掃描樣式與 2026-10-30 一致（動態執行、零寬／雙向控制字元、120 字元以上 base64／hex、行內 40 空白以上），另加 DECISIONS.md 既有的「新增行 400 字元」門檻。命中一律依 UPSTREAM.md 字面拒收、不自行豁免；其中零寬／雙向控制字元命中全在測試向量或驗證碼（`sent_from_thread_vectors.json`、`verified_profile_test.dart`、slash command 測試、`definition_validation.rs`／`team_catalog.rs`），看起來是刻意的同形字／控制字元測試資料，但仍照規則 skip，等上游同步時整批重審。PR 掃的是查詢當下的 head，OPEN PR 的 head 會漂移，結論只對表中 head 有效。

PR #8918（closed 未合併）的 diff 端點回空，內容無法取得，因未被上游收下而 skip。

## Commit 軸（84 筆）

| Commit | 標題 | 裁決與理由 |
| --- | --- | --- |
| `ff284d00d387` | mobile: stop typing prune ticks from rebuilding channel pages (#8695) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ccfc1490e451` | perf(mobile): verify signatures with native libsecp256k1 (#8657) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `fffd8ca95784` | fix(mobile): recover Solo sync silently instead of showing a retry banner (#8701) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `762adad54f79` | fix(mobile): require lowercase hex in native verification (#8702) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `be1ac392e85c` | perf(mobile): render inbox and search previews as plain text (#8675) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `76cd4294f65b` | fix(relay): close a REQ whose history read failed instead of sending EOSE (#8692) | **skip**：本輪拒收：新增行超過 400 字元（ARCHITECTURE.md），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `f539ef4a8706` | docs(buzz-acp): fix stale prepare_reconnect doc comment (#8697) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `1fe120165f30` | BUZZ-272: Deny workflow runs for banned owners (#8242) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `c609d33e8c3e` | ci: pin JDK 17 for the Android lane (#8711) | **adopt**（2026-11-07 由 defer 改判）：ubuntu-latest 升到 26.04 後 Android lane 因 JDK 25 與 Gradle 8.14.5 不相容而紅燈；`cherry-pick -x` 帶入，`_ci-clients.yml` 無衝突（該檔沒有 fork 修補），setup-java 維持上游釘的 v6.1.0 SHA |
| `050d545264a8` | perf(mobile): skip unchanged message footer layout (#8433) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `1f16f621d87c` | perf(relay): cut connect-burst CPU in log filtering and open-channel lookup (#8670) | **skip**：本輪拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `4b21a10c4b10` | fix: don't notify workflow owners through their attribution tag (#8694) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `a94ebece0eb1` | Revert "fix(mobile): push every message in your own Solo chats (#8615)" (#8690) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `64312fa5bed4` | fix(mobile): address #8650 second-pass review (#8691) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `efcdf00101f5` | relay: open the search pool lazily so a dead reader can't block boot (#8662) | **skip**：本輪拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `425284aa2c25` | test(desktop): measure inline video controls against their player (#8683) | **defer**：桌面端（Tauri／Windows）變更，需實機驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `428f0dcd22ac` | test(desktop): settle composer edits and press hover-only row actions by keyboard (#8682) | **defer**：桌面端（Tauri／Windows）變更，需實機驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `0052b2354eb5` | test(desktop): gate flaky E2E specs on the state they assume (#8681) | **defer**：桌面端（Tauri／Windows）變更，需實機驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `b1f76ef4d20f` | ci: cache the Tauri apt .debs and fit a cold Windows Rust run in its cap (#8679) | **defer**：CI workflow 變更，與 fork 的 workflow 修補（FORK.md）衝突，同步時一併重做；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `1893c3ab5a13` | test: dedupe collect_until_eose by event id and uncap two shell tests (#8677) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ef4130da4bfe` | fix(db): keep lease releases durable and deflake PostgreSQL lane tests (#8676) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `0e8fb49bd09c` | test(relay): fix main's build after the test-state helper rename (#8718) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `ef0fce8c5103` | ci(loadgen): publish buzz-loadgen as ghcr.io/block/buzz-loadgen (#8717) | **defer**：CI workflow 變更，與 fork 的 workflow 修補（FORK.md）衝突，同步時一併重做；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `d263e2c7f712` | fix(mobile): resolve iOS pushes on a fresh connection and retry a stale one (#8722) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `fae3f0346c44` | test(mobile): keep late callbacks and fixed sleeps from failing tests (#8678) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `158b3bf562b0` | test(scripts): stop file-size fixtures leaking git repos and fsmonitor daemons (#8727) | **defer**：腳本／工具變更，隨產品同步一併帶入；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `1eb67bb525d6` | fix(desktop): fix the product races behind four E2E flakes (#8680) | **defer**：桌面端（Tauri／Windows）變更，需實機驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `cc04cdca1a7a` | perf(relay): route author- and #p-scoped global subscriptions by selector (#8666) | **skip**：本輪拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `aae0081a9083` | fix(mobile): show agent DM typing and balance reply bubble padding (#8731) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `a57349b237c6` | feat(relay): add incremental artifact reads (#8523) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `5d70622ac0b1` | Restyle community invitations (#8728) | **defer**：web 前端變更，需瀏覽器與部署驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `75854111b826` | fix(mobile): retain invite keys and reject incomplete onboarding (#8753) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `a56966b77727` | feat(relay): NIP-AR sync subscriptions (#8522) | **skip**：本輪拒收：新增行超過 400 字元（docs/nips/NIP-AR.md），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `4cf2a3bd6684` | feat(loadgen): add a hot-thread stressor and teardown (#8746) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `c0c606e2e3ee` | Polish mobile navigation and restore community switch animation (#8732) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `0c82435ae0ad` | Add Buzz background and flying bees to invitations (#8763) | **defer**：web 前端變更，需瀏覽器與部署驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `f3a7bab098a5` | Clarify mobile community onboarding and saved identity selection (#8729) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `851250524efe` | feat(mobile): show your agents working in a thread on its root message (#8754) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `aa5f3e7bde9c` | feat(mobile): show conversation activity by the composer, as buzz-app does (#8765) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `704f2b8c27a0` | test(desktop): keep unit tests away from the real ~/.buzz nest (#8749) | **defer**：桌面端（Tauri／Windows）變更，需實機驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `d14e95f90ec8` | test: stop desktop, buzz-agent and mobile tests leaking temp files (#8748) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `b7b545f090bf` | test(db): drop scratch databases and roles even when a test fails (#8747) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `6e6f4e8a0de2` | test(mobile): check the title fade's animation, wait 10 s for the alert (#8741) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `547de61aa5fe` | fix(mobile): show channel posts before a burst of join notices (#8798) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `fc0bb778b06d` | test(desktop): settle five E2E flake classes and clear a draft by Backspace (#8744) | **defer**：桌面端（Tauri／Windows）變更，需實機驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `eafd77e9f6e9` | ci: bound Hermit fetches and let relay builds run without sccache (#8739) | **defer**：CI workflow 變更，與 fork 的 workflow 修補（FORK.md）衝突，同步時一併重做；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `9c3ba83adbce` | Simplify signed-in mobile community onboarding (#8852) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `4de1b6aeac3e` | Simplify mobile Solo and DM empty states (#8851) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `5f13984a1950` | Bring buzz.xyz branding and animated bees to mobile welcome (#8853) | **skip**：本輪拒收：新增行超過 400 字元（mobile/assets/images/welcome-bee.svg），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `cfcaef4e9fb5` | Update mobile toast animations (#8855) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `7d00c708059d` | feat(relay): publish NIP-FI verified profiles (BUZZ-433) (#8774) | **defer**：relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `2ca77747d11b` | Fix mobile Add Community loading and membership restoration (#8796) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `0a46f329c0ba` | Fade welcome bees with the QR scanner transition (#8859) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `120cbae8e56f` | fix(mobile): restore inline typing groups and keep working thread links (#8865) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `d14f33a17088` | fix(mobile): keep toasts above native navigation and sheets (#8866) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `b80217de3267` | fix(mobile): end #channel tokens at apostrophes, quotes and dashes (#8860) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `e3b1ef0d843e` | docs(agents): mark desktop/ as legacy, not a reference for mobile (#8868) | **defer**：文件變更，隨產品同步一併帶入；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `20742a236db9` | fix(mobile): only render known channels as #channel chips (#8862) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `a2540fbe3d8a` | Align Android profile setup with iOS steps (#8871) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `a12ad1cdd29d` | feat(mobile): refine agent profiles and model selection (#8773) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `f59b3265682f` | Fix mobile onboarding policy loading, browser cancellation and pairing feedback (#8874) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `acf56fff6fbf` | fix(mobile): use the desktop agent squircle for every agent avatar (#8873) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `db4478e8d2d8` | feat(mobile): organization sign-in for NIP-FI relays (#8700) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `2e4aacc9e05b` | fix(mobile): find open channels in search and stop the stuck spinner (#8764) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `e71fbe23df5c` | fix(mobile): keep loaded timeline visible while reconnecting (#8864) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `83ec9c0e2b51` | fix(mobile): show hosted community names consistently (#8872) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `5f98a1fa0424` | mobile: quiet agent messages and caught-up channel highlights (#8876) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `b41caeb5100b` | fix(mobile): time out relay connects that never finish the handshake (#8878) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `543ecf2b1f23` | fix(mobile): list the same owned agents as desktop (#8857) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `90772a43e999` | fix(mobile): keep avatars and images loading on slow links (#8879) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `e18d422d7260` | fix(mobile): fill uploaded avatars on the Agents page (#8882) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `21a9839826ba` | Fix mobile unread state retaining deleted messages (#8883) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `cde6c1bf5b1f` | feat(relay): auto-join new community members to default channels (#8594) | **skip**：本輪拒收：新增行超過 400 字元（NOSTR.md, crates/buzz-cli/src/lib.rs），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `634f48a8bda1` | Mobile: open Solo chats with Bestie and workspace controls (#8884) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `93b8b8febc85` | Standardize mobile navigation edges (#8895) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `53ca047cd3ea` | fix(mobile): keep mention rows still and cache directory searches (#8875) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `76fd0c6151a5` | fix(mobile): show Bestie as a continuous conversation (#8890) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `2e0abbcc0c3a` | fix(mobile): let slow image downloads finish (#8881) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `f6f6d9a673b5` | chore(mobile): delete dead code with no remaining UI path (#8880) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `220cec677a32` | fix(mobile): keep community icons on originals and record thumbnail 404s at fetch (#8896) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `985de41f1462` | feat(mobile): show NIP-FI verified names (#8858) | **skip**：本輪拒收：含零寬／雙向控制字元（mobile/test/shared/verified_profiles/verified_profile_test.dart），命中 UPSTREAM.md 的拒收規則；不自行豁免。重審條件：上游改寫該行或維護者明確決定 |
| `9d1b68445572` | fix(mobile): show remote agent instructions from the registry (#8908) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `464448c7b2ae` | fix(mobile): resync read state from the last fetch, not the whole week (#8903) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |
| `d342cf141cb3` | fix(mobile): catch up unread from the newest message already seen (#8901) | **defer**：行動端變更，需 iOS／Android 原生驗收環境；依既有「不自行分岔產品」政策不帶入，列入 ROADMAP「同步延後變更」 |

## PR 軸（195 筆）

| PR | 狀態 | head | 標題 | 裁決與理由 |
| --- | --- | --- | --- | --- |
| #8700 | MERGED | `b18807e5954b` | feat(mobile): organization sign-in for NIP-FI relays | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8701 | MERGED | `b431062e7cbd` | fix(mobile): recover Solo sync silently instead of showing a retry banner | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8702 | MERGED | `d9b94ee4fcbf` | fix(mobile): require lowercase hex in native verification | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8703 | OPEN | `69b4df4373da` | fix(push): bind and atomically apply management requests | **skip**：本輪拒收：新增行超過 400 字元（crates/buzz-push-gateway/src/postgres.rs, crates/buzz-push-gateway/tests/vectors/app_attest_transcripts.json），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8704 | OPEN | `9b16e4309167` | fix(push): reserve delivery quota for each relay | **skip**：本輪拒收：新增行超過 400 字元（crates/buzz-push-gateway/src/postgres.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8705 | OPEN | `4353f060f407` | fix(push): reserve request capacity for revocation | **defer**：OPEN，head 釘在 4353f060f407，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8706 | OPEN | `4cd6bcc05a3e` | fix(push): persist client revocation until it succeeds | **defer**：OPEN，head 釘在 4cd6bcc05a3e，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8707 | OPEN | `4d1a143cd771` | fix(push): restore grants after APNs endpoint rotation | **defer**：OPEN，head 釘在 4d1a143cd771，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8708 | OPEN | `6faad526554a` | fix(push): rotate APNs storage keys safely | **defer**：OPEN，head 釘在 6faad526554a，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8709 | OPEN | `d7d3c5e0b64f` | feat(workflows): approval gates persist and resume, with duration validation (   WF-08) | **defer**：OPEN，head 釘在 d7d3c5e0b64f，合併後走 commit 軸；腳本／工具變更，隨產品同步一併帶入 |
| #8711 | MERGED | `8c438f56132e` | ci: pin JDK 17 for the Android lane | **adopt**（2026-11-07 由 defer 改判）：同 commit 軸 `c609d33e8c3e`，fork 的 Android lane 因 ubuntu 26.04 的 JDK 25 紅燈 |
| #8712 | MERGED | `bfb2aa5e39b9` | fix(mobile): finish public account setup before returning to Buzz | **skip**：本輪拒收：新增行超過 400 字元（ARCHITECTURE.md, Justfile），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8713 | OPEN | `397acae706ac` | feat(desktop): models dashboard on the Agents page — usage by model + landscape | **defer**：OPEN，head 釘在 397acae706ac，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8714 | OPEN | `3232d47f7927` | feat(relay): push per-community storage usage to kgoose | **defer**：OPEN，head 釘在 3232d47f7927，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8715 | OPEN | `17255e9e7aad` | Fix duplicate timeline rows while reading history | **defer**：OPEN，head 釘在 17255e9e7aad，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8716 | MERGED | `ac6920635dfb` | fix(mobile): use account status to resume saved setup | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8717 | MERGED | `c24ee76b0378` | ci(loadgen): publish buzz-loadgen as ghcr.io/block/buzz-loadgen | **defer**：已合併，內容經 commit 軸抵達；CI workflow 變更，與 fork 的 workflow 修補（FORK.md）衝突，同步時一併重做 |
| #8718 | MERGED | `d27db0b5f67c` | test(relay): fix main's build after the test-state helper rename | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8719 | OPEN | `0527d57bdfe5` | Fix relay PostgreSQL test setup after helper rename | **defer**：OPEN，head 釘在 0527d57bdfe5，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8720 | OPEN | `fe7e55e8db47` | Wait for agent inventory updates in the desktop test | **defer**：OPEN，head 釘在 fe7e55e8db47，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8722 | MERGED | `0bee7e95fb0c` | fix(mobile): resolve iOS pushes on a fresh connection and retry a stale one | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8723 | OPEN | `a2dbaff4a617` | test(desktop): identify duplicate voice players by message ID | **defer**：OPEN，head 釘在 a2dbaff4a617，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8726 | OPEN | `d09f5f51d1be` | docs(acp): what a custom harness agent must expect, with a worked example | **skip**：本輪拒收：新增行超過 400 字元（crates/buzz-acp/README.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8727 | MERGED | `1828e97c5018` | test(scripts): stop file-size fixtures leaking git repos and fsmonitor daemons | **defer**：已合併，內容經 commit 軸抵達；腳本／工具變更，隨產品同步一併帶入 |
| #8728 | MERGED | `9f9a902dc78d` | Restyle community invitations | **defer**：已合併，內容經 commit 軸抵達；web 前端變更，需瀏覽器與部署驗收 |
| #8729 | MERGED | `cec8fc98754b` | Clarify mobile community onboarding and saved identity selection | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8730 | CLOSED | `53c8f468144c` | relay: a bare no-bridge kind:9002 edit is a recognized metadata edit | **skip**：本輪拒收：新增行超過 400 字元（TESTING.md）、行內長串空白（desktop/scripts/build-kannaka.mjs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8731 | MERGED | `172e5ba75882` | fix(mobile): show agent DM typing and balance reply bubble padding | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8732 | MERGED | `bfeb0fecda57` | Polish mobile navigation and restore community switch animation | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8733 | OPEN | `15fed03c3d5d` | feat(mobile): accept mentions with Tab and send with Enter on hardware keyboards | **defer**：OPEN，head 釘在 15fed03c3d5d，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8734 | OPEN | `4bf87e8d7564` | feat(mobile): remember mentioned agents in the next draft | **defer**：OPEN，head 釘在 4bf87e8d7564，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8735 | CLOSED | `e4bdc14b9c59` | feat(mobile): pair by pasting a pairing code into the community link field | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8736 | OPEN | `93b42ef375d9` | feat(mobile): run natively on iPad | **defer**：OPEN，head 釘在 93b42ef375d9，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8737 | OPEN | `2ecd0a28f6f2` | feat(mobile): mute push notifications from agents | **defer**：OPEN，head 釘在 2ecd0a28f6f2，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8739 | MERGED | `9297a5aa408d` | ci: bound Hermit fetches and let relay builds run without sccache | **defer**：已合併，內容經 commit 軸抵達；CI workflow 變更，與 fork 的 workflow 修補（FORK.md）衝突，同步時一併重做 |
| #8740 | OPEN | `ee0089ec0d8a` | test(relay): hold the replica's second aux page and move media's DB tests | **defer**：OPEN，head 釘在 ee0089ec0d8a，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8741 | MERGED | `a1a6ac1a97a2` | test(mobile): check the title fade's animation, wait 10 s for the alert | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8742 | OPEN | `08887d57c746` | fix(desktop): hold a deep-linked message against bottom settles | **defer**：OPEN，head 釘在 08887d57c746，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8743 | OPEN | `3b102926b40e` | test(desktop): stop four E2E specs racing scroll settles and focus | **defer**：OPEN，head 釘在 3b102926b40e，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8744 | MERGED | `389ee76ed5b9` | test(desktop): settle five E2E flake classes and clear a draft by Backspace | **defer**：已合併，內容經 commit 軸抵達；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8745 | OPEN | `500829a9f69d` | docs(nips): define verified profiles (BUZZ-433) | **skip**：本輪拒收：新增行超過 400 字元（docs/nips/NIP-FA.md, docs/nips/NIP-FI.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8746 | MERGED | `281920048737` | feat(loadgen): add a hot-thread stressor and teardown | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8747 | MERGED | `f832c7a64571` | test(db): drop scratch databases and roles even when a test fails | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8748 | MERGED | `3671dc226fee` | test: stop desktop, buzz-agent and mobile tests leaking temp files | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8749 | MERGED | `9ac05c66a010` | test(desktop): keep unit tests away from the real ~/.buzz nest | **defer**：已合併，內容經 commit 軸抵達；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8750 | CLOSED | `bc976c96fe92` | fix(dev): don't override an outside core.hooksPath when installing git hooks | **skip**：本輪拒收：新增行超過 400 字元（AGENTS.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8751 | OPEN | `aef6369a35fc` | feat(mobile): collapse agent-only messages | **defer**：OPEN，head 釘在 aef6369a35fc，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8752 | OPEN | `644a8133989a` | fix(relay): bound mesh dials and keep failing pods out of the mesh | **skip**：本輪拒收：新增行超過 400 字元（Justfile），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8753 | MERGED | `4564b3562a33` | fix(mobile): retain invite keys and reject incomplete onboarding | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8754 | MERGED | `3caa17a2065c` | feat(mobile): show your agents working in a thread on its root message | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8755 | CLOSED | `c20e46525145` | feat(desktop): ⌘⇧\ reacts to the latest message; emoji picker follows app theme | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8756 | OPEN | `8a89654ef1b5` | fix(acp): failure notices never wake sibling agents under OwnerOnly | **defer**：OPEN，head 釘在 8a89654ef1b5，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8757 | OPEN | `dd5c62cdfa1b` | feat(desktop): add /giphy composer command | **defer**：OPEN，head 釘在 dd5c62cdfa1b，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8759 | OPEN | `ccbffe0f9f81` | feat(cli): manage sidebar sections with `buzz sidebar sections` | **defer**：OPEN，head 釘在 ccbffe0f9f81，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8760 | OPEN | `ff259ae4481c` | Enforce unique channel names per community | **defer**：OPEN，head 釘在 ff259ae4481c，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8763 | MERGED | `1c7f83bc7192` | Add Buzz background and flying bees to invitations | **defer**：已合併，內容經 commit 軸抵達；web 前端變更，需瀏覽器與部署驗收 |
| #8764 | MERGED | `85042b1a4a25` | fix(mobile): find open channels in search and stop the stuck spinner | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8765 | MERGED | `3480ad238c15` | feat(mobile): show conversation activity by the composer, as buzz-app does | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8766 | CLOSED | `41ddb692a62e` | feat(cli): scope messages search by channel and time; fix --broadcast and set-presence doc | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8767 | CLOSED | `e3e003db0aca` | fix(cli): workflow run history and approvals via relay HTTP API | **skip**：本輪拒收：新增行超過 400 字元（desktop/src-tauri/src/managed_agents/nest_skill.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8768 | CLOSED | `0232faf1b3bd` | feat(cli): user status expiry and status read | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8769 | CLOSED | `d0f29ab0718e` | feat(cli): send a thread message to the channel | **skip**：本輪拒收：含零寬／雙向控制字元（crates/buzz-cli/src/commands/sent_from_thread_vectors.json）、新增行超過 400 字元（desktop/src-tauri/src/managed_agents/nest_skill.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8770 | CLOSED | `088674db5c91` | feat(cli): repo state and channel template list | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8771 | CLOSED | `b480f9f0010c` | feat(cli): community member management and invite links | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8772 | OPEN | `839b4c2bfa7b` | fix(media): keep transparency in image thumbnails | **defer**：OPEN，head 釘在 839b4c2bfa7b，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8773 | MERGED | `32af47a2f6cf` | feat(mobile): refine agent profiles and model selection | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8774 | MERGED | `13c011c289f1` | feat(relay): publish NIP-FI verified profiles (BUZZ-433) | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8775 | OPEN | `0c2ef5ab632d` | feat(cli): scope messages search by channel and time; fix --broadcast and set-presence doc | **defer**：OPEN，head 釘在 0c2ef5ab632d，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8776 | OPEN | `08e188d546af` | fix(cli): workflow run history and approvals via relay HTTP API | **defer**：OPEN，head 釘在 08e188d546af，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8777 | OPEN | `bb4deb024098` | feat(cli): user status expiry and status read | **defer**：OPEN，head 釘在 bb4deb024098，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8778 | OPEN | `d50c2de82a3d` | feat(cli): send a thread message to the channel | **skip**：本輪拒收：含零寬／雙向控制字元（crates/buzz-cli/src/commands/sent_from_thread_vectors.json），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8779 | OPEN | `cfee5c420c03` | feat(cli): repo state and channel template list | **defer**：OPEN，head 釘在 cfee5c420c03，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8780 | OPEN | `5fec6e96545f` | feat(cli): community member management and invite links | **defer**：OPEN，head 釘在 5fec6e96545f，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8781 | OPEN | `929eaf2a5b65` | feat(cli): sidebar stars, mutes, and project pins | **defer**：OPEN，head 釘在 929eaf2a5b65，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8782 | OPEN | `9ee09a619bce` | fix(relay): refuse a second listed open channel with the same name | **defer**：OPEN，head 釘在 9ee09a619bce，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8783 | OPEN | `e965b9abee9f` | feat(relay): add kind 30180 custom emoji entry | **skip**：本輪拒收：新增行超過 400 字元（docs/nips/NIP-CE.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8784 | OPEN | `f0a8b9789635` | feat(cli): sidebar sort mode per group | **defer**：OPEN，head 釘在 f0a8b9789635，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8785 | OPEN | `82f5582b9417` | feat(cli): PR reviews and issue/PR comments | **defer**：OPEN，head 釘在 82f5582b9417，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8786 | OPEN | `d8e4dfc43133` | feat(cli): reminders (NIP-ER) | **defer**：OPEN，head 釘在 d8e4dfc43133，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8787 | OPEN | `a2dcffce7fe5` | feat(db): enforce unique listed channel names with an index | **defer**：OPEN，head 釘在 a2dcffce7fe5，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8788 | OPEN | `a9a9b90d2a4c` | feat(cli): search and resolve catalog emoji | **defer**：OPEN，head 釘在 a9a9b90d2a4c，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8789 | OPEN | `7f30aa6575f1` | feat(cli): read-only unread state (NIP-RS) | **skip**：本輪拒收：新增行超過 400 字元（crates/buzz-cli/src/lib.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8790 | OPEN | `fbdfe0ef6a01` | feat(cli): read-only agent activity (observer frames) | **defer**：OPEN，head 釘在 fbdfe0ef6a01，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8792 | OPEN | `22c6af3f9481` | fix(emoji): bound the legacy custom-emoji union and keep the last good mobile palette | **defer**：OPEN，head 釘在 22c6af3f9481，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8793 | OPEN | `db28347a11eb` | feat(cli): read-only persona, team, and agent metric catalogs | **defer**：OPEN，head 釘在 db28347a11eb，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8795 | CLOSED | `6513b796fa45` | feat(desktop): auto-join an existing #announcements as a starter channel | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8796 | MERGED | `68a061ae2198` | Fix mobile Add Community loading and membership restoration | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8797 | CLOSED | `f612ce0d731a` | feat(desktop): search catalog emoji from the relay | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8798 | MERGED | `7a38763af2a8` | fix(mobile): show channel posts before a burst of join notices | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8800 | OPEN | `2dc3a94316ad` | feat(mobile): search catalog emoji from the relay | **defer**：OPEN，head 釘在 2dc3a94316ad，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8801 | CLOSED | `5faf0788d0eb` | Verify HMAC-signed workflow webhooks and let owners set a caller-supplied secret | **skip**：本輪拒收：新增行超過 400 字元（ARCHITECTURE.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8802 | OPEN | `538cda70edc8` | fix(db): auto-migrate artifact sync indexes on small databases | **defer**：OPEN，head 釘在 538cda70edc8，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8803 | OPEN | `16fb80835c81` | Specify composer slash commands | **defer**：OPEN，head 釘在 16fb80835c81，合併後走 commit 軸；文件變更，隨產品同步一併帶入 |
| #8807 | OPEN | `5561e32dd383` | fix(mobile): show a taken channel name plainly and keep invites working | **defer**：OPEN，head 釘在 5561e32dd383，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8808 | OPEN | `eed24860a597` | Add mobile slash command framework and /shrug | **defer**：OPEN，head 釘在 eed24860a597，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8809 | OPEN | `ebbc4628f6e2` | feat(cli): pin, unpin, and list channel messages with `buzz pins` | **defer**：OPEN，head 釘在 ebbc4628f6e2，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8810 | OPEN | `57a098152f4c` | feat(cli): buzz emoji migrate for bulk Slack catalogs | **defer**：OPEN，head 釘在 57a098152f4c，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8811 | OPEN | `a6e85e8d7010` | Render CommonMark backslash escapes on mobile | **defer**：OPEN，head 釘在 a6e85e8d7010，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8812 | OPEN | `86ef26045c55` | feat(mobile): /away, /active and /status slash commands | **skip**：本輪拒收：含零寬／雙向控制字元（mobile/test/features/channels/slash_commands/slash_presence_commands_test.dart），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8813 | OPEN | `63d16e794b65` | feat(mobile): /remind slash command with standalone reminders | **defer**：OPEN，head 釘在 63d16e794b65，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8814 | OPEN | `2f8b974b5d14` | feat(mobile): slash commands /invite, /remove, /join, /leave, /who | **defer**：OPEN，head 釘在 2f8b974b5d14，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8815 | OPEN | `cce6f14b77f0` | Add mobile /rename, /archive, and /mute slash commands | **defer**：OPEN，head 釘在 cce6f14b77f0，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8816 | OPEN | `73ba455a50da` | Add /dm and /huddle slash commands to mobile | **defer**：OPEN，head 釘在 73ba455a50da，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8817 | CLOSED | `5f00664d14b6` | Add desktop composer slash-command framework and /shrug | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8818 | CLOSED | `82a069d98519` | Add desktop /away, /active and /status slash commands | **skip**：本輪拒收：含零寬／雙向控制字元（desktop/src/features/slash-commands/lib/splitStatusArgs.test.mjs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8819 | OPEN | `4b841ec2e020` | feat: user groups (@handle) with relay-checked mentions and `buzz groups` CRUD | **skip**：本輪拒收：新增行超過 400 字元（docs/nips/NIP-PL.md, docs/user-groups.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8820 | CLOSED | `78f09894622e` | Add desktop /remind with standalone reminders | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8821 | CLOSED | `2931a6d49db6` | Desktop slash commands: /invite, /remove, /join, /leave, /who | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8822 | CLOSED | `f928f1f1514f` | Add desktop channel admin slash commands (/rename, /archive, /mute, /topic) | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8823 | OPEN | `28929613ff03` | fix(mobile): require informed consent before cloud key backup | **defer**：OPEN，head 釘在 28929613ff03，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8826 | CLOSED | `2d782a43b271` | Add desktop /dm, /huddle and /gif slash commands | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8827 | CLOSED | `c57b02ca4a7f` | feat: forward messages to channels and people | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8828 | OPEN | `23d039808668` | feat(cli): read and set the community theme | **skip**：本輪拒收：新增行超過 400 字元（crates/buzz-cli/src/lib.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8829 | OPEN | `9c9ec98e8bd9` | feat(cli): report a message to relay moderators | **skip**：本輪拒收：新增行超過 400 字元（crates/buzz-cli/src/lib.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8830 | OPEN | `bfe204b9dd81` | feat(cli): list huddles and their participants | **defer**：OPEN，head 釘在 bfe204b9dd81，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8831 | OPEN | `3d8251deaf65` | feat(cli): mark channels read with a CLI-owned NIP-RS slot | **skip**：本輪拒收：新增行超過 400 字元（crates/buzz-cli/src/lib.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8833 | OPEN | `2cfe77132837` | feat(cli): cancel an agent turn and switch its model | **defer**：OPEN，head 釘在 2cfe77132837，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8835 | OPEN | `32809c04674c` | feat(relay): compare-and-set for addressable event replacement | **defer**：OPEN，head 釘在 32809c04674c，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8836 | OPEN | `23b058a7a704` | feat(cli): read and write NIP-AR channel artifacts | **skip**：本輪拒收：新增行超過 400 字元（crates/buzz-cli/src/lib.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8837 | OPEN | `025a2b1d7b7b` | feat(cli): validate persona and team catalog entries with Desktop's rules | **skip**：本輪拒收：含零寬／雙向控制字元（crates/buzz-core/src/definition_validation.rs, crates/buzz-core/src/team_catalog.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8839 | CLOSED | `8e744f6ecbd9` | feat(cli): ask the owner to delete an agent through a Desktop draft | **skip**：本輪拒收：新增行超過 400 字元（crates/buzz-acp/src/base_prompt.md, desktop/src-tauri/src/managed_agents/nest_skill.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8840 | OPEN | `d41ef265ac57` | docs: mark desktop/ as the deprecated Buzz 0.X app | **defer**：OPEN，head 釘在 d41ef265ac57，合併後走 commit 軸；文件變更，隨產品同步一併帶入 |
| #8841 | OPEN | `640785772c7f` | feat: per-community flat threads (NIP-TP) | **skip**：本輪拒收：新增行超過 400 字元（docs/multi-tenant-conformance.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8842 | OPEN | `ef02df68f6be` | fix(desktop): cap Hermes agent parallelism at 3 | **defer**：OPEN，head 釘在 ef02df68f6be，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8843 | OPEN | `e5608099e327` | fix(desktop): bound the observer archive to recently used channels | **defer**：OPEN，head 釘在 e5608099e327，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8846 | OPEN | `7b8b9878fdfa` | perf(relay): cut writer-pool round trips past the 48k relay ceiling | **defer**：OPEN，head 釘在 7b8b9878fdfa，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8847 | CLOSED | `cb241b3f1aea` | Handle Android sign-in browser cancellation and show Cancel | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8848 | CLOSED | `4f9d9b6c5ce5` | docs(nip-fi): verified names on open relays without membership | **skip**：本輪拒收：新增行超過 400 字元（docs/nips/NIP-FI.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8849 | MERGED | `b7dacd5c970f` | feat(relay): verified names on open relays without membership | **defer**：已合併，內容經 commit 軸抵達；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8850 | CLOSED | `91ff67f42f97` | test(relay): reserve each boot_lifecycle test's ports together | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8851 | MERGED | `6d68f3b2b222` | Simplify mobile Solo and DM empty states | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8852 | MERGED | `b46eff85c41d` | Simplify signed-in mobile community onboarding | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8853 | MERGED | `7bafe1c780f6` | Bring buzz.xyz branding and animated bees to mobile welcome | **skip**：本輪拒收：新增行超過 400 字元（mobile/assets/images/welcome-bee.svg），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8854 | OPEN | `0cd3f0087a1e` | feat(cli): split custom emoji sets into parts for 100k-emoji palettes | **defer**：OPEN，head 釘在 0cd3f0087a1e，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8855 | MERGED | `5886cac7d172` | Update mobile toast animations | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8857 | MERGED | `fe1f9fc99b28` | fix(mobile): list the same owned agents as desktop | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8858 | MERGED | `9add40e30c52` | feat(mobile): show NIP-FI verified names | **skip**：本輪拒收：含零寬／雙向控制字元（mobile/test/shared/verified_profiles/verified_profile_test.dart），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8859 | MERGED | `5de3994df4b2` | Fade welcome bees with the QR scanner transition | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8860 | MERGED | `c190ded8a9c4` | fix(mobile): end #channel tokens at apostrophes, quotes and dashes | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8862 | MERGED | `5e66a6e89b7b` | fix(mobile): only render known channels as #channel chips | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8863 | OPEN | `89dce357e1b7` | feat(mobile): mark edited messages after the body | **defer**：OPEN，head 釘在 89dce357e1b7，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8864 | MERGED | `50beb64d2ebb` | fix(mobile): keep loaded timeline visible while reconnecting | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8865 | MERGED | `5df48ad4ba52` | fix(mobile): restore inline typing groups and keep working thread links | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8866 | MERGED | `1bd37c46771b` | fix(mobile): keep toasts above native navigation and sheets | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8867 | CLOSED | `76dee4013cb0` | fix(desktop): measure the timeline floor from the DOM during a Virtua shift | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8868 | MERGED | `750de2b1870e` | docs(agents): mark desktop/ as legacy, not a reference for mobile | **defer**：已合併，內容經 commit 軸抵達；文件變更，隨產品同步一併帶入 |
| #8869 | CLOSED | `2ce754343c3c` | fix(mobile): discover open channels through search | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8870 | OPEN | `3f7302a09c11` | fix(mobile): load earlier edits to thread replies when a thread opens | **defer**：OPEN，head 釘在 3f7302a09c11，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8871 | MERGED | `f43dbc572736` | Align Android profile setup with iOS steps | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8872 | MERGED | `34a61bc8ed1f` | fix(mobile): show hosted community names consistently | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8873 | MERGED | `43b2516dd28f` | fix(mobile): use the desktop agent squircle for every agent avatar | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8874 | MERGED | `b7aaaa788db2` | Fix mobile onboarding policy loading, browser cancellation and pairing feedback | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8875 | MERGED | `ca643e9fcfa6` | fix(mobile): keep mention rows still and cache directory searches | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8876 | MERGED | `5fe633298180` | mobile: quiet agent messages and caught-up channel highlights | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8877 | OPEN | `479603198449` | feat(relay): support explicit operator listener thread watches | **defer**：OPEN，head 釘在 479603198449，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8878 | MERGED | `e83052d5be2d` | fix(mobile): time out relay connects that never finish the handshake | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8879 | MERGED | `cd2af1facace` | fix(mobile): keep avatars and images loading on slow links | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8880 | MERGED | `f8ea8900092d` | chore(mobile): delete dead code with no remaining UI path | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8881 | MERGED | `1006d9f78f8a` | fix(mobile): let slow image downloads finish | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8882 | MERGED | `a00826826ce0` | fix(mobile): fill uploaded avatars on the Agents page | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8883 | MERGED | `028aacc82493` | Fix mobile unread state retaining deleted messages | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8884 | MERGED | `b836ca79e0cf` | Mobile: open Solo chats with Bestie and workspace controls | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8885 | OPEN | `d08481c24f54` | fix(relay): let browsers cache CORS preflights for authenticated requests | **defer**：OPEN，head 釘在 d08481c24f54，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8886 | OPEN | `465b60d28d76` | perf(relay): set TCP_NODELAY on accepted connections | **defer**：OPEN，head 釘在 465b60d28d76，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8887 | OPEN | `c3054ea6291a` | fix(desktop): remember each agent's huddle voice | **defer**：OPEN，head 釘在 c3054ea6291a，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8888 | OPEN | `f3b9646a40be` | feat(agents): add Meta (Muse) harness via the muse-acp bridge | **defer**：OPEN，head 釘在 f3b9646a40be，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8890 | MERGED | `3f00c971933e` | fix(mobile): show Bestie as a continuous conversation | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8891 | CLOSED | `83602a4990d5` | fix(mobile): open Solo chats at the composer with agent and workspace controls | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8892 | OPEN | `dde98d52ad01` | fix(buzz-acp): keep agents alive and heard while background work is pending | **skip**：本輪拒收：新增行超過 400 字元（crates/buzz-acp/src/base_prompt.md），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8893 | OPEN | `3193c5ccb961` | feat(relay): BUZZ_DB_ACQUIRE_TIMEOUT_SECS overrides the Postgres acquire timeout | **defer**：OPEN，head 釘在 3193c5ccb961，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8895 | MERGED | `e37fd3faf209` | Standardize mobile navigation edges | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8896 | MERGED | `ca84affce9be` | fix(mobile): keep community icons on originals and record thumbnail 404s at fetch | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8897 | OPEN | `91ff89236cc4` | feat(mobile): use HTTP/2 on iOS through app-wide URLSessions | **defer**：OPEN，head 釘在 91ff89236cc4，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8898 | OPEN | `f7d8043d8c3a` | fix(relay): publish group state from one locked snapshot | **defer**：OPEN，head 釘在 f7d8043d8c3a，合併後走 commit 軸；relay／資料庫／部署變更，需 Postgres 雙模式與 relay 驗收 |
| #8899 | CLOSED | `28b5c8429d16` | test(relay-e2e): pre-join the relay owner before toggling auto_join | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8900 | CLOSED | `d0e0307aeb79` | fix(relay): fence kind:39000/39001 snapshots behind the replacement lock | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8901 | MERGED | `236e74adb7c9` | fix(mobile): catch up unread from the newest message already seen | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8902 | CLOSED | `3098b318e4f2` | fix(mobile): ask only for newer latest messages on refresh | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8903 | MERGED | `8df185957ee5` | fix(mobile): resync read state from the last fetch, not the whole week | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8904 | CLOSED | `ae637b39c484` | fix(mobile): carry another device's read marks over at most once a minute | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8905 | CLOSED | `a4f750bfb2a6` | feat(relay): report memberships removed since a time | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8906 | CLOSED | `b42d6e848a6c` | feat(mobile): refresh memberships from what changed since the last read | **skip**：closed 未合併，上游未收；非 Windows／CJK 專屬缺陷，不採用 |
| #8907 | OPEN | `8fa16c78df1d` | fix(mobile): prompt Builderlab sign-in instead of labeling agents desktop-only | **defer**：OPEN，head 釘在 8fa16c78df1d，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8908 | MERGED | `194c5a4a6692` | fix(mobile): show remote agent instructions from the registry | **defer**：已合併，內容經 commit 軸抵達；行動端變更，需 iOS／Android 原生驗收環境 |
| #8909 | OPEN | `c9249696e29b` | feat(relay): guarded archive and restore for task channels (NEXUS-4111) | **skip**：本輪拒收：新增行超過 400 字元（crates/buzz-relay/src/api/git/settings_tests.rs），命中 UPSTREAM.md 的拒收規則（取目前 head 掃描）；不自行豁免 |
| #8910 | OPEN | `8175c9fe5605` | mobile: read the channel list after live changes, not every minute | **defer**：OPEN，head 釘在 8175c9fe5605，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8911 | OPEN | `c702a943fe2f` | fix(desktop): skip a starter channel the relay will never create | **defer**：OPEN，head 釘在 c702a943fe2f，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |
| #8912 | OPEN | `a8e04f76891c` | feat(mobile): open a prefilled Create agent form from Builderlab agent cards | **defer**：OPEN，head 釘在 a8e04f76891c，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8913 | OPEN | `0c9c90cab948` | mobile: keep a thumbnail fallback apart from a direct load of the same URL | **defer**：OPEN，head 釘在 0c9c90cab948，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8914 | OPEN | `a0eb8bc67687` | fix(mobile): open the public Builderlab login the iOS bridge allows | **defer**：OPEN，head 釘在 a0eb8bc67687，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8915 | OPEN | `01bfc23146bc` | fix(mobile): hide the Flutter debug banner | **defer**：OPEN，head 釘在 01bfc23146bc，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8916 | OPEN | `e5515f765767` | fix(mobile): answer push snapshot bridge calls at user-initiated QoS; report hop latency o | **defer**：OPEN，head 釘在 e5515f765767，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8917 | OPEN | `4542eeb21d8b` | fix(mobile): mark an Inbox item read when it is opened | **defer**：OPEN，head 釘在 4542eeb21d8b，合併後走 commit 軸；行動端變更，需 iOS／Android 原生驗收環境 |
| #8918 | CLOSED | `17ac479cf4fc` | test: prove campaign lead return path | **skip**：closed 未合併；上游 diff 端點回空（無法取得內容），上游未收，不採用 |
| #8920 | OPEN | `337a4a8fba2b` | fix(desktop): keep the AUTH rejection reason on a terminal relay session | **defer**：OPEN，head 釘在 337a4a8fba2b，合併後走 commit 軸；桌面端（Tauri／Windows）變更，需實機驗收 |

## Issue 軸（15 筆）

| Issue | 狀態 | 標題 | 裁決與理由 |
| --- | --- | --- | --- |
| #8738 | open | buzz-acp: busy-owner hold forks under channel policy are never reclaimed; pool-wide idle s | **defer**：buzz-acp 的 busy-owner hold 回收缺陷；fork 不改 buzz-agent／acp 行為，等上游修正後隨 commit 軸帶入 |
| #8758 | open | DM messages sent from some Desktop surfaces carry no p-tags, so agents in `mentions` mode  | **defer**：Desktop 部分入口的 DM 缺 p-tag；產品行為缺陷，等上游修正 |
| #8761 | open | fix(desktop): enroll owned DM agents when starting huddle | **skip**：body 僅「test」，沒有可審內容 |
| #8762 | open | fix(desktop): DM huddle enroll owner-attributed agents (patch) | **defer**：上游桌面 huddle 修補提案（patch）；等上游合併後隨 commit 軸帶入 |
| #8791 | open | Mobile: offer organization sign-in when adding an organization relay by link | **defer**：行動端組織登入的功能請求；行動端需原生驗收 |
| #8794 | open | Desktop sign-in blocked: Turnstile widget never loads on login.builderlab.xyz (“Verificati | **skip**：macOS 桌面登入跳到上游託管的 login.builderlab.xyz，Turnstile 載入失敗；是上游託管服務問題，fork 沒有該服務 |
| #8805 | open | Relay compare-and-set for sidebar sections snapshot writes | **defer**：relay 側邊欄 section 快照寫入的 CAS 提案；等上游設計 |
| #8806 | open | Share persona and team catalog validation between Desktop and buzz-cli | **defer**：Desktop 與 buzz-cli 共用 persona／team 驗證的重構提案；等上游 |
| #8824 | open | Make the search allowlist maintenance script online and batched | **defer**：搜尋 allowlist 維護腳本改線上批次；等上游，需 Postgres 驗收 |
| #8845 | open | Proposal: Slack-style composer slash commands on mobile | **skip**：行動端 slash command 的功能提案，非缺陷 |
| #8856 | open | Windows Desktop 0.5.28 remains “Can’t reach the relay” with a healthy self-hosted relay | **defer**：Windows Desktop 0.5.28 連自架 relay 顯示「Can't reach the relay」。回報者已發現與 BUZZ_CORS_ORIGINS 有關並持續調查，約每 64 秒一次短命 WebSocket；上游無修正、無根因。fork 目前不發行桌面版也無 Windows 實機驗收環境。重審條件：上游釘出根因或修正 commit，或維護者實際在 Windows 桌面重現 |
| #8861 | open | Inbox: Unread + Mentions shows threads where the mention was already read | **defer**：Inbox 未讀＋提及篩選缺陷；產品行為，等上游 |
| #8889 | closed | push-gateway: five defects block every real iOS device (found self-hosting with a TestFlig | **skip**：已 closed；push-gateway 對 iOS 實機的缺陷，fork 不營運 push gateway |
| #8894 | open | buzz-acp 0.5.28 (and current main): an owner-only agent silently discards a same-owner age | **defer**：buzz-acp owner-only 在寄件者 profile 查詢失敗時丟訊息；產品缺陷，等上游修正 |
| #8919 | open | Provide a way to disable "AI provider" and "AI subscription" login flows | **skip**：關閉 AI provider 登入流程的功能請求，非缺陷 |
