# 2026-10-29 上游差異初篩證據（未完成）

範圍：commit `24a370606044c0c7be787cc2fd98ec0bfe1d606b..39b8b2b6a6d065b3da981e096b1a3881f1c63fd4`；PR 8644–8688；issue 8642–8688。只讀取 GitHub；本輪不採用產品變更。

## Commit 清單（尚未逐筆完成採用審查）

| Commit | 標題 |
| --- | --- |
| `3ed07e5c758fe14c3712e6e8309dfe90942f1d81` | fix(deps): bump pulldown-cmark to 0.13.5 for RUSTSEC-2026-0414 (#8644) |
| `78b5dae1f608a33850137b5be5a1909390035cce` | fix(relay): store a kind:9000 and its membership writes in one transaction (#8606) |
| `646ef8abf9bc5ac3e698826b38811033537a4806` | Stop requiring the 0032 roster trigger at relay startup (#8611) |
| `9e18d17a36d338b8a8e006d51ce5f971865d37c5` | fix(mobile): open new DMs without waiting for a full channel reload (#8638) |
| `2c28e07133d306ced204ca17f97c4cb93c916f72` | BUZZ-413: Add user deletion fence storage (#8632) |
| `b310fea05b2ed2c2d04cc0da4ad16f38108b6a3c` | mobile: find DMs opened ahead of the list everywhere (#8646) |
| `0a362eef150ab16453993d442a8037baad766797` | perf(db,relay): bound thread participant scans and coalesce live summaries (#8635) |
| `d6196a16c1eec7268e1fc5124ca89ee3d03d6d3e` | fix(relay): revoke invitations and restrict claims (#8237) |
| `4ff02bf03b73b6e07ac45beca833652e0272478a` | perf(mobile): sign events with native libsecp256k1 on iOS and Android (#8654) |
| `bad9d26142eaa9df8027b51a3b1bea0ca984309a` | fix(mobile): push every message in your own Solo chats (#8615) |
| `974495fd4a5d77310efd9de45a6f4339e881446a` | fix(mobile): resume reconnect replay from the last live point and spread reconnects (#8659) |
| `713b864e2f6cc70889c41a1bcf5c7207547c104a` | fix(push-gateway): log which App Attest certificate check failed (#8671) |
| `82b27813766b6ae38602769a1166024cdc191260` | fix(mobile): rebuild buzz_secp256k1 when vendored headers change (#8664) |
| `eda26b9423328a06960bb0d5fd4c1af54600c419` | ci: repeat changed tests ten times on pull requests (#8613) |
| `6e332f46c7f0b046c37355a1aca8f8189e6718c5` | chore(desktop): point `just staging` at the new Block staging relay (#8623) |
| `7c165c371845792b6752c642c6351a16b025268c` | Smooth profile avatar editor transitions (#8640) |
| `39b8b2b6a6d065b3da981e096b1a3881f1c63fd4` | feat(mobile): unify Messages navigation with Solo and Team filters (#8649) |

## PR 清單快照與新增行初篩

| PR | 狀態 | head | 新增行 | 掃描待判讀數 | 標題 |
| --- | --- | --- | --- | --- | --- |
| #8644 | MERGED | `2593bf12f174f5a2f628a0baa47ea54b24a9ccb7` | 3 | 0 | fix(deps): bump pulldown-cmark to 0.13.5 for RUSTSEC-2026-0414 |
| #8645 | OPEN | `0cc24ecd9ca9e161f23419e99bcf8ebdef0015c3` | 1507 | 0 | Add standalone owned-community deletion handlers |
| #8646 | MERGED | `5f9ee3927359f4e7cb392b187315d81a78c7887a` | 204 | 0 | mobile: find DMs opened ahead of the list everywhere |
| #8647 | OPEN | `3e363f64742f39a91f869277ad5b3a8a1cd2910c` | 183 | 0 | fix(mobile): wait for app activation before browser auth |
| #8648 | OPEN | `8a7967147317415b919b77dcc1f429ba0f56c4b6` | 777 | 1 | feat(repos): trust repository maintainers for issue and pull-request work |
| #8649 | MERGED | `90009381cc9df4911fcf5d57997a90c3f2a087f7` | 4164 | 0 | feat(mobile): unify Messages navigation with Solo and Team filters |
| #8650 | OPEN | `b572e70be43758b6e7e9a500ff685e3a0b514043` | 879 | 0 | feat(mobile): choose remote agent models and gate agents on Builderlab sign-in |
| #8651 | OPEN | `2085d5b7ea2fd985c4c2e5a2d5c6ed25e24f1fa4` | 399 | 0 | db: warm the relay read pool toward its ceiling at boot |
| #8652 | OPEN | `045030c4d76ba9005207104e222e592173caef77` | 2102 | 0 | fix(desktop): resume reconnect replay from the last live point |
| #8653 | OPEN | `b0c494f12eaa934f1e40dd80c0f5b8217da261d4` | 1917 | 0 | fix(buzz-acp): resume reconnect replay from the last live point and spread 1012 reconnects |
| #8654 | MERGED | `ad11110b49f4e3074e736eb21f943059970037d2` | 35582 | 25 | perf(mobile): sign events with native libsecp256k1 on iOS and Android |
| #8655 | OPEN | `d291f12b8c15a834af75059add4e019603d1f5ef` | 81 | 0 | perf(mobile): derive public keys with native libsecp256k1 |
| #8656 | OPEN | `1dbf3ebda5a6e90d441b4554af033e44b4958180` | 35680 | 25 | perf(mobile): compute NIP-44 ECDH with native libsecp256k1 |
| #8657 | OPEN | `e57e3ad86e1a072c99da77078faa3458b932deb6` | 179 | 0 | perf(mobile): verify signatures with native libsecp256k1 |
| #8658 | OPEN | `b70b41c3bed402450f268af3db2fdbdf2733bf8f` | 870 | 4 | BUZZ-413: Fence stream and forum message writes |
| #8659 | MERGED | `c4a1afe9eb99488cf8178ab8bb3628fda6eb60f3` | 818 | 0 | fix(mobile): resume reconnect replay from the last live point and spread reconnects |
| #8660 | OPEN | `b8e172672525d7eb4fbb2834bf4caa23686ed926` | 395 | 0 | fix(desktop): always flash a linked message in the channel timeline |
| #8661 | OPEN | `3ddbecd548a8112a633e574e55d7d19c1bdf71d9` | 140 | 0 | fix(desktop): dismiss channel suggestions when an edit is cleared |
| #8662 | OPEN | `7b6292cc182225f04878a7d185ec95896550850d` | 187 | 1 | relay: open the search pool lazily so a dead reader can't block boot |
| #8663 | OPEN | `b29a3531f720992d0423ed0f9924a9ebc8d55d63` | 162 | 0 | db: answer match-nothing event reads without taking a connection |
| #8664 | MERGED | `78b0a986b53bd70d4a7897daa1f3f0947cb27f17` | 11 | 0 | fix(mobile): rebuild buzz_secp256k1 when vendored headers change |
| #8665 | OPEN | `b77ad12a50839219011f7d331c69582153fea90d` | 2035 | 0 | feat(mobile): hold the default agent to send voice notes |
| #8666 | OPEN | `d72351886051d026161be99fe28221a0b4613a04` | 527 | 1 | perf(relay): route author- and #p-scoped global subscriptions by selector |
| #8667 | CLOSED | `2ce0b735d56f8bce5ddea27432d6196800e2da7a` | 278 | 0 | perf(mobile): skip decrypting read-state events already applied |
| #8668 | CLOSED | `8947f4dc4a83d096f0363be324e8ff6607cc64cc` | 77 | 0 | perf(mobile): keep mention and channel patterns out of message rows that cannot match |
| #8669 | OPEN | `7203e5ae30235b1bd346ad497389f9eb6ef96ded` | 449 | 0 | perf(mobile): decode relay query responses off the UI isolate |
| #8670 | OPEN | `92742c6849850837a2f43eeef5f7d0c17ba68c9c` | 544 | 1 | perf(relay): cut connect-burst CPU in log filtering and open-channel lookup |
| #8671 | MERGED | `6d5b06e8590989dcd1d76101c6df355a095a8fa6` | 157 | 0 | fix(push-gateway): log which App Attest certificate check failed |
| #8672 | OPEN | `37b7b6cd2fbcaee5f9f210903a12b7a885319e51` | 336 | 0 | fix(mobile): keep read state across reconnects and resume |
| #8673 | OPEN | `5c7cb8ddf0172e78d941beee11fd8a0a703dd051` | 5355 | 8 | fix(push): use opaque grants and protect gateway capacity |
| #8675 | OPEN | `6661d594ae4f719f11012de0eabfcb5954fd13f6` | 909 | 0 | perf(mobile): render inbox and search previews as plain text |
| #8676 | OPEN | `dae720ed982f0360fba95e3dc5038eb32f626edd` | 220 | 0 | fix(db): keep lease releases durable and deflake PostgreSQL lane tests |
| #8677 | OPEN | `402045df43f9a740c526b87acd03548bd3da8d7e` | 69 | 0 | test: dedupe collect_until_eose by event id and uncap two shell tests |
| #8678 | OPEN | `7ab028c6f5a6848cb4ae5fcfa0ecf4f59a5a1fcc` | 86 | 0 | test(mobile): keep late callbacks and fixed sleeps from failing tests |
| #8679 | OPEN | `8f162ceb9f0ee539afaae1c94084e686d959f4aa` | 98 | 0 | ci: cache the Tauri apt .debs and fit a cold Windows Rust run in its cap |
| #8680 | OPEN | `66e4ca3b0da7379c888e67cbac9f7c621aa093b9` | 726 | 0 | fix(desktop): fix the product races behind four E2E flakes |
| #8681 | OPEN | `c6f493f2336b6d7647c7f344f480bd146c3eefa7` | 384 | 0 | test(desktop): gate flaky E2E specs on the state they assume |
| #8682 | OPEN | `f977e7e19b253ed01c108398af2eb9d158382429` | 174 | 0 | test(desktop): settle composer edits and press hover-only row actions by keyboard |
| #8683 | OPEN | `7496624b9a0d9363ab539f82042d105aa102038b` | 11 | 0 | test(desktop): measure inline video controls against their player |
| #8685 | OPEN | `d2d5ef78df374c889ffb91a1a81439cbf459883b` | 27 | 0 | fix(mobile): remove Bestie selection and agent deletion controls |
| #8686 | OPEN | `44167eda43979e9074ed23e70a84be0b7a56079c` | 81 | 0 | fix(desktop): pick the typed mention when Enter beats the list render |
| #8687 | OPEN | `32b00c938d8d63d9fecefcd0741649047e47c681` | 2808 | 0 | Unify mobile onboarding and community entry screens |
| #8688 | OPEN | `15e7b7bb34ee26ce4b2b96da31a64a555f710614` | 549 | 0 | fix(buzz-acp): back off on an error CLOSED instead of re-REQing at once |

## 初篩判讀與限制

- 43 筆 PR 的 diff 均成功讀取；66 個模式命中集中於 8 筆 PR。沒有命中 `eval(`、`new Function(`、掛載全域 `require` 或零寬／雙向控制字元。
- #8654、#8656 的長編碼是 BIP-340 公開測試向量；C 標頭的長空白是行尾註解對齊。本報告不複製向量內容。
- 其他長行集中於文件、Justfile 測試篩選式、Postgres SQL 字串與 App Attest 測試資料；這只是模式初篩，不代表語義正確或可安全採用。
- 上表 head 是列舉時的快照；`gh pr diff` 隨後取當時 PR diff，未再次核對 head 是否變動。因此不將掃描結果宣稱為綁定不可變 head 的正式審查，也不據此推進 PR 水位。
- commit 比較固定於 `39b8b2b6a6d065b3da981e096b1a3881f1c63fd4`。GitHub compare 的檔案摘要最多 300 筆且部分 patch 不完整，不能用它宣稱完整 diff 已審查。

## Issue 軸

- [#8674](https://github.com/block/buzz/issues/8674)，open：macOS 匯入 agent snapshot 時，長而不可換行的指令令 Import／Cancel 按鈕超出視窗。已讀重現步驟；本輪未重現或修產品碼。
- [#8684](https://github.com/block/buzz/issues/8684)，open：私人 stream 中只有 agent 擁有者的 mention 能喚醒本機 agent，設定入口消失。已讀重現步驟；根因與舊設定是否遷移尚未證實。

## 既有裁決與 fork 修補核對

- [#8624](https://github.com/block/buzz/pull/8624) 已 CLOSED，`mergedAt=null`，head `af329e96fa522e2b7bfb4549223f51d36a91883b`。既有等待該 PR 合併的安全更新條件未成立，不能當成已修補。
- [#8643](https://github.com/block/buzz/pull/8643) 仍 OPEN，head `b37af7b5b8d4e939a7cf2153a8a893106b21fd36`，未帶入 Hermes 修改。
- 相對舊水位，本機產品／依賴差異仍是 FORK.md 明列的 `Cargo.lock`、Tauri 鎖檔、pnpm 鎖檔、`deny.toml` 與 buzz-dev-mcp 兩個測試檔；workflow 差異另含 fork 自有掃描與發布防護。
- 本機 `_ci-rust.yml` 的非 block owner Windows 90 分鐘條件仍在。既有發布 job／build-push owner guard 與 fork patch 清單均由 `tests/fork` 實際檢查通過。
- 新 commit #8613 修改 `_ci-rust.yml` 並新增 flake workflow；#8671 與 fork 明列的 App Attest certificate 修補同檔；#8644 修改根鎖檔。這些需要正式採用審查，不能由零衝突或初篩推定安全。

## 驗證與結論

- 本機 HEAD：`3bfb2b541844cbe698f04f72eb3731581da2c7bd`，detached HEAD；本輪只改文件。
- `pwsh -NoProfile -File tools/dev_check.ps1`：exit 0；結尾 `29 passed in 1.93s`、`OK`。這是 FORK.md 指定的完整維護工具 gate，涵蓋發布防護與修補清單。
- `. ./bin/activate-hermit`：Windows Git Bash bootstrap 失敗，輸出 `HERMIT_STATE_DIR_RAW: unbound variable`；不可宣稱 pinned 環境已啟用。未修改環境或 hook。
- GitHub 既有成功的 CI 僅涵蓋其原始 commit，不是本輪採用結果的 CI 證據。這次禁止 commit、push、PR，未觸發任何遠端流程。
- 尚未完成 commit 逐筆審查、不可變 PR head 的 diff 核對與採用後受影響 CI，故本項標為未完成；三個水位維持原值，ROADMAP.md 保留原列。
- 沒有修 bug 或改產品／工具執行行為，先紅後綠回歸測試不適用。未修改上游 CHANGELOG.md；repo 無 REVIEW.md，審查狀態回註於本文件與 DECISIONS.md。

## 後續

2026-10-30 已接續逐筆裁決，見 [正式裁決](UPSTREAM_REVIEW_2026-10-30.md)。本文件保留為當時初篩快照；其「未完成／未推進水位」描述只對當時成立，不覆蓋後續結果。
