# 2026-10-30 上游差異裁決

> 前半保留上一輪固定快照的完整裁決；最新水位與本次驗收以末節「接續增量」為準。

## 範圍與方法

接續 [2026-10-29 初篩](UPSTREAM_REVIEW_2026-10-29.md)，固定 commit 範圍 `24a370606044c0c7be787cc2fd98ec0bfe1d606b..39b8b2b6a6d065b3da981e096b1a3881f1c63fd4`（17 筆）；PR #8644–#8688（43 筆）；issue #8642–#8688（只有 #8674、#8684，已從 state=all 清單核對）。

本輪只是採用裁決：adopt＝本輪實際帶入；skip＝本輪不帶入且有明確原因；defer＝不帶入，條件成立後再審。沒有 adopt，不修改產品、依賴、workflow 或 advisory ignore，也沒有「採用後產品 CI 已通過」的聲明。延後項目的唯一工作清單仍在 ROADMAP.md；下表是本次裁決紀錄。

已讀 VISION.md、VISION_REMOTE_AGENTS.md、VISION_MODERATION.md、TESTING.md 與 docs/database.md。保持共用事件記錄、社群隔離及應用端持有行為的方向；不自行修改產品行為。

```text
固定 commit / PR base...head -> diff 雜湊與檔案清單 -> 逐筆 skip / defer
維護工具 gate 通過 -> 更新已審查水位；產品同步仍未完成
```

## 不可變版本與掃描界限

每個 commit 由 `gh api repos/block/buzz/commits/<完整 SHA> -H "Accept: application/vnd.github.diff"` 取得；PR 先讀 `pulls/<number>`，再以 metadata 的完整 `base.sha...head.sha` 取得 diff，不再用會漂移的 `gh pr diff`。43 筆的 diff 檔案數全部等於同次 metadata 的 changed_files；每份 diff 的 SHA-256、bytes、檔案清單、base／head、updated_at、掃描數與裁決見 [機器證據](UPSTREAM_REVIEW_2026-10-30.json)。API 取回成功、檔案數一致只證明本輪輸入可核對，不代表語義正確。

初篩後 head 改變：#8650、#8651、#8653、#8656、#8657、#8662、#8666、#8669、#8675、#8687、#8688。本輪使用下表的新 head；之後的 head 不在本輪結論內。PR 的 base 也固定在 JSON，避免 base 前進讓三點比較改變。

新增行掃描未命中 eval、new Function、全域 require 或零寬／雙向控制字元。#8654 及其合併 commit 的 19 筆長編碼、3 筆行內長空白分別位於 BIP-340 公開向量與 vendored C 註解；依 UPSTREAM.md 的字面拒收規則，本輪仍判 skip，不將可解釋誤寫成獲准採用。其餘上述四組模式沒有命中；掃描不是完整安全審計。

另依 DECISIONS.md 已有的 400 字元門檻檢查超長新增行：commit `78b5dae1f608`（NOSTR.md）、`646ef8abf9bc`（Helm README）、`0a362eef150a` 與 `d6196a16c1ee`（Justfile），以及 PR #8648、#8658、#8662、#8666、#8670、#8673 命中，本輪均 skip。#8654 亦有 3 筆超長向量行，維持 skip。檔案、長度與片段記在 JSON；未因它們是說明文字、SQL 或篩選式就自行豁免拒收規則。補查時重新取得固定 SHA 的 diff，60 份 SHA-256 全部與第一次相符。

查詢時上游 main 已前進至 `f6d31d13e433da3c70158cc24f1107b2b2ca1143`。本輪 commit 審查仍停在固定快照 `39b8b2b`；PR 目前已合併的項目若不在這 17 筆內，不因此視為 commit 軸已審。

## Commit 軸：17 筆（0 adopt、6 skip、11 defer）

| Commit | 內容 | 裁決與理由 |
| --- | --- | --- |
| `3ed07e5c758fe14c3712e6e8309dfe90942f1d81` | fix(deps): bump pulldown-cmark to 0.13.5 for RUSTSEC-2026-0414 (#8644) | **skip**：安全修補已具備：本機 pulldown-cmark 0.13.5 與 checksum 相同；不帶入同筆無關的 data-encoding-macro-internal syn 2→1 鎖檔變動。 |
| `78b5dae1f608a33850137b5be5a1909390035cce` | fix(relay): store a kind:9000 and its membership writes in one transaction (#8606) | **skip**：本輪拒收：新增行超過既有 400 字元門檻，命中 UPSTREAM.md 的超長單行規則（位置見 long_line_samples）；未自行豁免文件、SQL 或測試篩選式。重新考慮需符合政策的修訂或維護者明確決定。其餘採用風險：kind:9000 事件與成員寫入改為同一交易，方向符合一次操作一次儲存；需 Postgres 的失敗、重送、全拒絕流程及 relay gate，目前不移植。 |
| `646ef8abf9bc5ac3e698826b38811033537a4806` | Stop requiring the 0032 roster trigger at relay startup (#8611) | **skip**：本輪拒收：新增行超過既有 400 字元門檻，命中 UPSTREAM.md 的超長單行規則（位置見 long_line_samples）；未自行豁免文件、SQL 或測試篩選式。重新考慮需符合政策的修訂或維護者明確決定。其餘採用風險：移除 0032 roster trigger 啟動要求但未刪 trigger；需確認部署順序與應用端 fence，再跑 migration-mode／relay 測試，不把它誤當 trigger 已可刪除。 |
| `9e18d17a36d338b8a8e006d51ce5f971865d37c5` | fix(mobile): open new DMs without waiting for a full channel reload (#8638) | **defer**：DM 改為定向讀取並背景更新列表；需行動端新建、重開隱藏 DM 及讀取失敗重試流程，未做原生驗收。 |
| `2c28e07133d306ced204ca17f97c4cb93c916f72` | BUZZ-413: Add user deletion fence storage (#8632) | **defer**：新增 user_deletion_fences、0074 migration 與 desired-state／seed；需雙模式 schema、一致的 purge 例外及刪除後拒絕寫入測試，不能只套單一 migration。 |
| `b310fea05b2ed2c2d04cc0da4ad16f38108b6a3c` | mobile: find DMs opened ahead of the list everywhere (#8646) | **defer**：提前開啟的 DM 需同時進入搜尋、mention 與 thread 等入口；依賴 #8638，與前項一起驗收，不拆開移植。 |
| `0a362eef150ab16453993d442a8037baad766797` | perf(db,relay): bound thread participant scans and coalesce live summaries (#8635) | **skip**：本輪拒收：新增行超過既有 400 字元門檻，命中 UPSTREAM.md 的超長單行規則（位置見 long_line_samples）；未自行豁免文件、SQL 或測試篩選式。重新考慮需符合政策的修訂或維護者明確決定。其餘採用風險：限制 thread participant 查詢並合併即時摘要刷新；需 Postgres 查詢界限、併發刷新與取消清理測試，未驗收不採用。 |
| `d6196a16c1eec7268e1fc5124ca89ee3d03d6d3e` | fix(relay): revoke invitations and restrict claims (#8237) | **skip**：本輪拒收：新增行超過既有 400 字元門檻，命中 UPSTREAM.md 的超長單行規則（位置見 long_line_samples）；未自行豁免文件、SQL 或測試篩選式。重新考慮需符合政策的修訂或維護者明確決定。其餘採用風險：邀請撤銷與 claim 限制橫跨 relay／db／desktop／web；需撤銷、受限使用者、owner 比對及部分失敗重試整合測試，不拆散授權邊界。 |
| `4ff02bf03b73b6e07ac45beca833652e0272478a` | perf(mobile): sign events with native libsecp256k1 on iOS and Android (#8654) | **skip**：本輪拒收：新增行含 19 筆長編碼與 3 筆行內長空白，命中 UPSTREAM.md 的拒收條件；雖可辨認為 BIP-340 向量及 vendored C 註解，未自行豁免。重新考慮需符合政策的修訂或維護者明確決定，另需原生 ABI／簽章跨實作驗收。 |
| `bad9d26142eaa9df8027b51a3b1bea0ca984309a` | fix(mobile): push every message in your own Solo chats (#8615) | **defer**：Solo 每則訊息推送涉及加密與 push lease；需自聊、一般 DM、靜音與 root isolation 的行動端流程，不以維護工具測試代替。 |
| `974495fd4a5d77310efd9de45a6f4339e881446a` | fix(mobile): resume reconnect replay from the last live point and spread reconnects (#8659) | **defer**：reconnect 回放游標與錯開重連；需歷史／即時重疊、斷線重試及游標持續性流程，避免漏訊息。 |
| `713b864e2f6cc70889c41a1bcf5c7207547c104a` | fix(push-gateway): log which App Attest certificate check failed (#8671) | **defer**：App Attest 分類錯誤改善診斷，與 fork 已帶入的 certificate 修補同檔；需保留 p256 0.14 與憑證拒絕語義，跑 gateway 相容測試後才採用。 |
| `82b27813766b6ae38602769a1166024cdc191260` | fix(mobile): rebuild buzz_secp256k1 when vendored headers change (#8664) | **defer**：vendored header 變更加入原生庫重建輸入；依賴本輪拒收的 #8654，不能單獨加入目前沒有的 package 路徑。 |
| `eda26b9423328a06960bb0d5fd4c1af54600c419` | ci: repeat changed tests ten times on pull requests (#8613) | **defer**：flake lane 十次重跑、cache shared-key 與新增 workflow；雖 _ci-rust.yml 改動不碰 Windows 逾時行，仍需保留 90 分鐘 fork patch、發布 guard 並驗證 selector／成本上限，不直接啟用。 |
| `6e332f46c7f0b046c37355a1aca8f8189e6718c5` | chore(desktop): point `just staging` at the new Block staging relay (#8623) | **defer**：只改 Block staging 的 Justfile URL；fork 未要求使用該內部環境，不連線測試，待完整同步時核對是否仍需這個入口。 |
| `7c165c371845792b6752c642c6351a16b025268c` | Smooth profile avatar editor transitions (#8640) | **defer**：avatar editor 動畫與原生透明度；需 iOS 外觀切換、取消與空預覽流程，未做原生驗收。 |
| `39b8b2b6a6d065b3da981e096b1a3881f1c63fd4` | feat(mobile): unify Messages navigation with Solo and Team filters (#8649) | **defer**：Messages／Solo／Team 導航含 Kotlin／Swift／Flutter 與 default-agent 加密設定；需兩平台原生流程與持續儲存失敗重試，不以單一 Flutter 測試當整體驗收。 |

## PR 軸：43 筆（0 adopt、10 skip、33 defer）

| PR | 狀態 | 審查 head | 裁決與理由 |
| --- | --- | --- | --- |
| [#8644](https://github.com/block/buzz/pull/8644) | MERGED | `2593bf12f174f5a2f628a0baa47ea54b24a9ccb7` | **skip**：安全修補已具備：本機 pulldown-cmark 0.13.5 與 checksum 相同；不帶入同筆無關的 data-encoding-macro-internal syn 2→1 鎖檔變動。 |
| [#8645](https://github.com/block/buzz/pull/8645) | MERGED | `0cc24ecd9ca9e161f23419e99bcf8ebdef0015c3` | **defer**：owned-community 刪除處理需和 durable deletion／admission 一起驗收。 查詢時已合併但不在本次固定的 17 個 commit 內；留給後續 commit 增量審查。 |
| [#8646](https://github.com/block/buzz/pull/8646) | MERGED | `5f9ee3927359f4e7cb392b187315d81a78c7887a` | **defer**：對應固定範圍 commit b310fea05b2e；提前開啟的 DM 需同時進入搜尋、mention 與 thread 等入口；依賴 #8638，與前項一起驗收，不拆開移植。 |
| [#8647](https://github.com/block/buzz/pull/8647) | MERGED | `3e363f64742f39a91f869277ad5b3a8a1cd2910c` | **defer**：browser auth 等待 app activation，需行動裝置回跳驗收。 查詢時已合併但不在本次固定的 17 個 commit 內；留給後續 commit 增量審查。 |
| [#8648](https://github.com/block/buzz/pull/8648) | OPEN | `8a7967147317415b919b77dcc1f429ba0f56c4b6` | **skip**：本輪拒收：新增行超過既有 400 字元門檻，命中 UPSTREAM.md 的超長單行規則（位置見 long_line_samples）；未自行豁免文件、SQL 或測試篩選式。重新考慮需符合政策的修訂或維護者明確決定。其餘採用風險：repository maintainer 信任涉及 issue／PR 授權，需測越權邊界。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8649](https://github.com/block/buzz/pull/8649) | MERGED | `90009381cc9df4911fcf5d57997a90c3f2a087f7` | **defer**：對應固定範圍 commit 39b8b2b6a6d0；Messages／Solo／Team 導航含 Kotlin／Swift／Flutter 與 default-agent 加密設定；需兩平台原生流程與持續儲存失敗重試，不以單一 Flutter 測試當整體驗收。 |
| [#8650](https://github.com/block/buzz/pull/8650) | MERGED | `2dc1c52bbe80b33b0ee94d632c57ecdfed18f4b6` | **defer**：遠端模型與 Builderlab 登入門檻需 provider／登入流程驗收。 查詢時已合併但不在本次固定的 17 個 commit 內；留給後續 commit 增量審查。 |
| [#8651](https://github.com/block/buzz/pull/8651) | OPEN | `c405273df112bd9b640660316a7a711680af7000` | **defer**：read-pool 開機預熱需連線上限及不可用 reader 測試。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8652](https://github.com/block/buzz/pull/8652) | MERGED | `045030c4d76ba9005207104e222e592173caef77` | **defer**：桌面 reconnect 游標需斷線／即時重疊回歸。 查詢時已合併但不在本次固定的 17 個 commit 內；留給後續 commit 增量審查。 |
| [#8653](https://github.com/block/buzz/pull/8653) | MERGED | `ba5d0530bb7db41ca45d8c69dc1b08864d1b722e` | **defer**：ACP reconnect 與 1012 錯開重試需 harness 實測。 查詢時已合併但不在本次固定的 17 個 commit 內；留給後續 commit 增量審查。 |
| [#8654](https://github.com/block/buzz/pull/8654) | MERGED | `ad11110b49f4e3074e736eb21f943059970037d2` | **skip**：本輪拒收：新增行含 19 筆長編碼與 3 筆行內長空白，命中 UPSTREAM.md 的拒收條件；雖可辨認為 BIP-340 向量及 vendored C 註解，未自行豁免。重新考慮需符合政策的修訂或維護者明確決定，另需原生 ABI／簽章跨實作驗收。 |
| [#8655](https://github.com/block/buzz/pull/8655) | MERGED | `d291f12b8c15a834af75059add4e019603d1f5ef` | **defer**：native derive-public-key 依賴 #8654 原生 package，不獨立引進。 查詢時已合併但不在本次固定的 17 個 commit 內；留給後續 commit 增量審查。 |
| [#8656](https://github.com/block/buzz/pull/8656) | MERGED | `da1190e2c978646d8cac06f2f38ae58dab4c97a1` | **defer**：目前 head 已縮成 2 檔 ECDH 修改，仍依賴 #8654 原生 package；不能沿用舊 head 的向量掃描結論。 查詢時已合併但不在本次固定的 17 個 commit 內；留給後續 commit 增量審查。 |
| [#8657](https://github.com/block/buzz/pull/8657) | OPEN | `f90823cd1208ac688fca706ce063e1f090c009c7` | **defer**：native verify-signature 依賴 #8654，需跨實作向量與 ABI 驗收。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8658](https://github.com/block/buzz/pull/8658) | OPEN | `b70b41c3bed402450f268af3db2fdbdf2733bf8f` | **skip**：本輪拒收：新增行超過既有 400 字元門檻，命中 UPSTREAM.md 的超長單行規則（位置見 long_line_samples）；未自行豁免文件、SQL 或測試篩選式。重新考慮需符合政策的修訂或維護者明確決定。其餘採用風險：stream／forum write fence 需 relay／Postgres 的刪除併發測試。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8659](https://github.com/block/buzz/pull/8659) | MERGED | `c4a1afe9eb99488cf8178ab8bb3628fda6eb60f3` | **defer**：對應固定範圍 commit 974495fd4a5d；reconnect 回放游標與錯開重連；需歷史／即時重疊、斷線重試及游標持續性流程，避免漏訊息。 |
| [#8660](https://github.com/block/buzz/pull/8660) | MERGED | `b8e172672525d7eb4fbb2834bf4caa23686ed926` | **defer**：linked-message flash 需桌面定位與重複跳轉流程。 查詢時已合併但不在本次固定的 17 個 commit 內；留給後續 commit 增量審查。 |
| [#8661](https://github.com/block/buzz/pull/8661) | OPEN | `3ddbecd548a8112a633e574e55d7d19c1bdf71d9` | **defer**：編輯清空後 suggestions 狀態需鍵盤與滑鼠流程。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8662](https://github.com/block/buzz/pull/8662) | OPEN | `9270a5bcf9566d03aa93dc7c570808ce2374c3e9` | **skip**：本輪拒收：新增行超過既有 400 字元門檻，命中 UPSTREAM.md 的超長單行規則（位置見 long_line_samples）；未自行豁免文件、SQL 或測試篩選式。重新考慮需符合政策的修訂或維護者明確決定。其餘採用風險：lazy search-pool 啟動需 reader 死亡／恢復測試。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8663](https://github.com/block/buzz/pull/8663) | MERGED | `b29a3531f720992d0423ed0f9924a9ebc8d55d63` | **defer**：match-nothing 查詢需證明不取連線且保留篩選語義。 查詢時已合併但不在本次固定的 17 個 commit 內；留給後續 commit 增量審查。 |
| [#8664](https://github.com/block/buzz/pull/8664) | MERGED | `78b0a986b53bd70d4a7897daa1f3f0947cb27f17` | **defer**：對應固定範圍 commit 82b27813766b；vendored header 變更加入原生庫重建輸入；依賴本輪拒收的 #8654，不能單獨加入目前沒有的 package 路徑。 |
| [#8665](https://github.com/block/buzz/pull/8665) | OPEN | `b77ad12a50839219011f7d331c69582153fea90d` | **defer**：長按語音涉及權限、錄製取消與 default-agent 設定。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8666](https://github.com/block/buzz/pull/8666) | OPEN | `fe88174b16875bff6849ba3c90921b4749fecc4b` | **skip**：本輪拒收：新增行超過既有 400 字元門檻，命中 UPSTREAM.md 的超長單行規則（位置見 long_line_samples）；未自行豁免文件、SQL 或測試篩選式。重新考慮需符合政策的修訂或維護者明確決定。其餘採用風險：author／#p subscription selector 需權限隔離及路由正確性測試。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8667](https://github.com/block/buzz/pull/8667) | CLOSED | `2ce0b735d56f8bce5ddea27432d6196800e2da7a` | **skip**：已關閉未合併，不採用被放棄的 head；如重開或有替代 PR，依新 head 重審。 |
| [#8668](https://github.com/block/buzz/pull/8668) | CLOSED | `8947f4dc4a83d096f0363be324e8ff6607cc64cc` | **skip**：已關閉未合併，不採用被放棄的 head；如重開或有替代 PR，依新 head 重審。 |
| [#8669](https://github.com/block/buzz/pull/8669) | MERGED | `0fc6c094309f3b56f101a5ea65890b7a493043f3` | **defer**：isolate decode 需行動端順序、錯誤與大回應測試。 查詢時已合併但不在本次固定的 17 個 commit 內；留給後續 commit 增量審查。 |
| [#8670](https://github.com/block/buzz/pull/8670) | OPEN | `92742c6849850837a2f43eeef5f7d0c17ba68c9c` | **skip**：本輪拒收：新增行超過既有 400 字元門檻，命中 UPSTREAM.md 的超長單行規則（位置見 long_line_samples）；未自行豁免文件、SQL 或測試篩選式。重新考慮需符合政策的修訂或維護者明確決定。其餘採用風險：connect-burst 優化需 CPU／連線及 open-channel 授權測試。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8671](https://github.com/block/buzz/pull/8671) | MERGED | `6d5b06e8590989dcd1d76101c6df355a095a8fa6` | **defer**：對應固定範圍 commit 713b864e2f6c；App Attest 分類錯誤改善診斷，與 fork 已帶入的 certificate 修補同檔；需保留 p256 0.14 與憑證拒絕語義，跑 gateway 相容測試後才採用。 |
| [#8672](https://github.com/block/buzz/pull/8672) | MERGED | `37b7b6cd2fbcaee5f9f210903a12b7a885319e51` | **defer**：read-state 跨 reconnect／resume 需持續儲存與重放測試。 查詢時已合併但不在本次固定的 17 個 commit 內；留給後續 commit 增量審查。 |
| [#8673](https://github.com/block/buzz/pull/8673) | OPEN | `5c7cb8ddf0172e78d941beee11fd8a0a703dd051` | **skip**：本輪拒收：新增行超過既有 400 字元門檻，命中 UPSTREAM.md 的超長單行規則（位置見 long_line_samples）；未自行豁免文件、SQL 或測試篩選式。重新考慮需符合政策的修訂或維護者明確決定。其餘採用風險：opaque push grants 與 gateway 容量保護跨信任邊界，需端到端測試。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8675](https://github.com/block/buzz/pull/8675) | OPEN | `8c721ba3a99b73a3e5966771c9b41c2a61687c77` | **defer**：純文字 inbox／search preview 需對照 mention、特殊內容及搜尋流程。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8676](https://github.com/block/buzz/pull/8676) | OPEN | `dae720ed982f0360fba95e3dc5038eb32f626edd` | **defer**：lease release 持續重試需 Postgres 部分失敗與重啟測試。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8677](https://github.com/block/buzz/pull/8677) | OPEN | `402045df43f9a740c526b87acd03548bd3da8d7e` | **defer**：collect_until_eose 去重與 shell timeout 修改需實際 relay／shell gate。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8678](https://github.com/block/buzz/pull/8678) | OPEN | `7ab028c6f5a6848cb4ae5fcfa0ecf4f59a5a1fcc` | **defer**：late callback／sleep 調整需證明仍能揭露產品失敗。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8679](https://github.com/block/buzz/pull/8679) | OPEN | `8f162ceb9f0ee539afaae1c94084e686d959f4aa` | **defer**：Tauri apt cache 與 Windows 冷編譯上限，碰 fork 逾時修補同檔；需保留 90 分鐘與 fork CI 驗證。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8680](https://github.com/block/buzz/pull/8680) | OPEN | `66e4ca3b0da7379c888e67cbac9f7c621aa093b9` | **defer**：四項 desktop race 需對應真實 E2E 流程驗收。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8681](https://github.com/block/buzz/pull/8681) | OPEN | `c6f493f2336b6d7647c7f344f480bd146c3eefa7` | **defer**：E2E 前置條件需確定不遮蔽產品 race。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8682](https://github.com/block/buzz/pull/8682) | OPEN | `f977e7e19b253ed01c108398af2eb9d158382429` | **defer**：composer settle／鍵盤觸發 row action 需驗證非主要輸入方式。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8683](https://github.com/block/buzz/pull/8683) | OPEN | `7496624b9a0d9363ab539f82042d105aa102038b` | **defer**：video controls 量測基準需 player 尺寸及實際 overlay 驗收。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8685](https://github.com/block/buzz/pull/8685) | OPEN | `d2d5ef78df374c889ffb91a1a81439cbf459883b` | **defer**：移除 Bestie／agent deletion 控制項需確認仍有復原入口。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8686](https://github.com/block/buzz/pull/8686) | OPEN | `44167eda43979e9074ed23e70a84be0b7a56079c` | **defer**：Enter 早於 mention 清單渲染需同名、鍵盤與貼上回歸。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |
| [#8687](https://github.com/block/buzz/pull/8687) | MERGED | `0917da309bc49448e5467c2de9b333be032b3c0a` | **defer**：onboarding／community entry 涉及帳號與社群切換，需原生流程驗收。 查詢時已合併但不在本次固定的 17 個 commit 內；留給後續 commit 增量審查。 |
| [#8688](https://github.com/block/buzz/pull/8688) | OPEN | `b7341d9e5aecc1ae247a800906a8691514d40019` | **defer**：error CLOSED backoff 需證明有上限、不丟事件且能恢復。 未合併，不獨立帶入；合併或 head 再變更時重新審查。 |

## Issue 軸：2 筆

- **#8674 — defer**：macOS 0.5.28 匯入 snapshot 時，長指令把 Import／Cancel 擠出視窗。本機 `desktop/src/features/agents/ui/AgentSnapshotImportDialog.tsx` 仍有 `break-words` 的 instructions／manifest `<pre>`；這是可對照的疑似路徑，不是已重現的根因。desktop/src 相對舊水位無 fork 差異。等待上游修正 commit，或維護者回報本 fork 原生桌面可重現後再做先紅後綠回歸；不在本輪猜修 CSS。
- **#8684 — defer**：private stream 中其他成員的 mention 不喚醒 agent，舊 respond-to 設定入口消失。本機 `desktop/src-tauri/src/commands/agents.rs` 仍驗證 respond-to allowlist，不能由 issue 文字推定 kind:30177 遷移就是根因；desktop/src 與 desktop/src-tauri/src 相對舊水位均無 fork 差異。等待可定位的上游修正或本 fork 原生重現，再驗證 owner、allowlist、其他成員及社群隔離；不擅自放寬授權。

issue 沒有 Git head：本輪以 number、updated_at、body SHA-256 固定已讀內容（見 JSON）；兩筆 state=open、comments=0，沒有可追加的留言證據。

## Fork 修補與發布防護

- `git diff 24a370606044c0c7be787cc2fd98ec0bfe1d606b HEAD --name-only -- crates desktop mobile web .github/workflows deny.toml Cargo.lock pnpm-lock.yaml`：產品／依賴分歧只有 Cargo.lock、兩個 buzz-dev-mcp 測試檔、deny.toml、Tauri 鎖檔、pnpm 鎖檔；workflow 另含 FORK.md 所列發布 guard、Windows 逾時修補及 fork 自有檢查。desktop／mobile 產品碼未自行分岔。
- #8644 的 pulldown-cmark 0.13.5 與 checksum 已存在；它同時把 data-encoding-macro-internal 的 syn 2.0.117 改成 1.0.109，本機仍保留 syn 2.0.117，不為重複安全修補倒退此項。
- #8671 修改 App Attest certificate.rs，與 FORK.md 已列 p256 修補同檔；#8613 改 _ci-rust.yml 的 cache 並新增 flake workflow，#8679 也觸碰 CI 設定。延後採用，不以不同 hunk 推定整合一定安全。
- 本輪未改任何發布 workflow；完整維護工具 gate 覆蓋非 block 發布 job、build-push guard、fork patch 清單。Windows 非 block owner 90 分鐘條件另以現有檔案核對。沒有建立 release、推送映像或向上游寫入。

## #8624 與路線圖

唯讀重新確認 #8624：state=closed、merged=false、head=`af329e96fa522e2b7bfb4549223f51d36a91883b`、updated_at=`2026-10-29T09:06:37Z`。它不能再作為「等這個 PR 合併」的預期來源。ROADMAP.md 改為等替代修補合併，或 @tailwindcss/typography 放寬 selector 版本且可用相容鎖檔更新解決；安全告警 state=fixed 仍必須另查。未宣稱相關告警已解除。

## 驗證與水位

- 第一輪完整維護工具 gate：`pwsh -NoProfile -File tools/dev_check.ps1`，exit 0；結尾 `29 passed in 1.23s`、`OK`。通過後才將 commit／PR／issue 水位推進到 `39b8b2b6a6d065b3da981e096b1a3881f1c63fd4`／8688／8684（2026-10-30）。
- 水位更新後完整維護工具 gate：`pwsh -NoProfile -File tools/dev_check.ps1`，exit 0；結尾 `29 passed in 0.57s`、`OK`。
- `git diff --check`：exit 0、無輸出。`python -` 一次性驗收檢查：exit 0；結尾 `PASS: 17 commits form fixed chain; 43 immutable PR diffs; 2 issues; decisions and 3 watermarks consistent; local links/wording/whitespace valid; index unchanged.` 檢查涵蓋固定 commit 連續鏈、完整 PR 編號集合、diff SHA 格式、拒收分類、水位、文件本機連結、禁用稱呼、行尾空白及未暫存。
- 文件自審：minimalism 9/10、elegance 9/10、correctness 9/10；無文件正確性阻擋項。此評分不代表 skip／defer 的產品碼已獲採用審查通過。
- `. ./bin/activate-hermit` 在 Windows Git Bash 仍輸出 `HERMIT_STATE_DIR_RAW: unbound variable`；外層 exit 0 是 bootstrap 未正確傳遞失敗，不是環境啟用證據。未改 bootstrap、PATH 或 hook。文件／水位變更依 FORK.md 跑完整維護工具 gate，不以未啟用的 pinned 工具鏈宣稱產品 gate 成功。

本輪只更新 fork 維護文件與審查水位，沒有產品或工具行為修正，先紅後綠不適用。不改上游 CHANGELOG.md；repo 無 REVIEW.md，審查回註在本文件與 DECISIONS.md。文件變更不需要啟動 app；沒有宣稱維護者已測試或 PR 已符合 ready 條件。

## 接續增量：審至目前上游最新

2026-10-30 固定 `39b8b2b6a6d065b3da981e096b1a3881f1c63fd4..6d719c680a85c98153324809988be37425fba73e`；新增 15 個 commit（全部 defer）、PR #8689–#8699 共 11 筆（2 skip、9 defer）。完整 base／head、diff SHA-256、檔案清單、掃描結果、逐筆理由與重審條件見 [增量機器證據](UPSTREAM_REVIEW_2026-10-30_INCREMENT.json)。原 17 個 commit、43 筆 PR、2 筆 issue 的裁決與 JSON 保留，不以新快照覆寫。

### Commit 軸

| 完整 SHA | 內容 | 裁決與理由 |
| --- | --- | --- |
| `a7e65c91da4937c6f825681c3f124b83380635a4` | feat(mobile): choose remote agent models and gate agents on Builderlab sign-in (#8650) | **defer**：模型／effort 選擇取自服務目錄，Builderlab 登入控制建立入口；需驗證跨社群、登出中建立、失敗重試與 hosted defines 的原生流程。 |
| `770ab7ff82d704d96870d6043346d3fca181eb8d` | perf(mobile): decode relay query responses off the UI isolate (#8669) | **defer**：成功回應改由 isolate 解壓與解析，保留前後 generation 檢查；需驗證 gzip、錯誤、退役與大回應，且錯誤解壓上限另見 #8689，不能只採成功路徑就宣稱資源已受限。 |
| `8161a7cad02f32261a7bae00b33109b76743b0cb` | perf(mobile): derive public keys with native libsecp256k1 (#8655) | **defer**：公鑰推導改走原生 libsecp256k1，依賴前批 #8654 套件；前批拒收未解除，且需 iOS／Android 跨實作向量與 ABI 驗收。 |
| `0d19ca69d3001520baa676172d6b7b250359bf18` | fix(mobile): wait for app activation before browser auth (#8647) | **defer**：iOS browser auth 等待 app activation，涉及 scene lifecycle、取消與多次回呼；需實機登入回跳及原生 bridge 測試。 |
| `5ea5ae1727fc6701a6b06595f0f920ec4f079b52` | fix(desktop): always flash a linked message in the channel timeline (#8660) | **defer**：linked-message flash 改動虛擬列表與 anchored scroll；需桌面深連結、已載入／需載入目標、鍵盤與重複跳轉流程。 |
| `8abcf2ea2a416c5cfceba797cb14487c3612b190` | fix(mobile): keep read state across reconnects and resume (#8672) | **defer**：read-state 跨 reconnect／resume 保留，需驗證持久化失敗、重連競態及社群切換不回寫舊狀態。 |
| `e922dc08ffd08f21d20fa0900f5f109eb0a22c98` | Unify mobile onboarding and community entry screens (#8687) | **defer**：統一 onboarding／community entry，涉及原生姓名輸入、帳號、配對與社群切換；需 hosted／self-hosted、取消與返回原生流程驗收。 |
| `8caf8351c124a2a39f160e342587d427e8c32a51` | Add standalone owned-community deletion handlers (#8645) | **defer**：owned-community 刪除新增 standalone handlers；需連同 durable lease、admission、git 寫入 fence 與階段重試驗證，不拆散刪除邊界。 |
| `aed4be8592bf512f3d345e28d3c76fe6b55e3134` | Add a scenario-driven relay load generator (#8636) | **defer**：新增 scenario-driven buzz-loadgen、seed／run 與鎖檔依賴，取代 wamp_bench；需受控本機 relay 驗證人口／分片、ramp 失敗終止、統計及清理，不在本輪建立負載資料。 |
| `ae689ab54d716d6f6df6bf18c67f12a3a810ecfe` | fix(desktop): resume reconnect replay from the last live point (#8652) | **defer**：reconnect replay 改從最後 live point 恢復，需驗證歷史回放與 live 交接無缺口、錯誤 CLOSED、重連與社群隔離。 |
| `3dbc95c3f668547e501c7d5f306d85ca5dcd055e` | perf(mobile): compute NIP-44 ECDH with native libsecp256k1 (#8656) | **defer**：NIP-44 ECDH 改走原生套件；依賴前批拒收的 #8654，需跨實作向量、錯誤公鑰及原生平台驗收。 |
| `cc28660c6117fb54d176b697b0db1059ed336e1f` | fix(buzz-acp): spread 1012 reconnects and keep replay gaps across a dropped socket (#8653) | **defer**：ACP 1012 重連採隨機延遲並保留 dropped-socket replay gap；需 harness 中斷／恢復及 shutdown 測試，並與 #8688／#8692 部署順序一起確認。 |
| `f6d31d13e433da3c70158cc24f1107b2b2ca1143` | db: answer match-nothing event reads without taking a connection (#8663) | **defer**：match-nothing 讀取在取得連線前回傳空集合；需驗證各 filter 組合與空 kinds 語義、不取連線及歷史端點行為，不能由掃描代替 Postgres gate。 |
| `0cde1fe2f40478d58c34f7a7113ea62759e353ec` | Make mobile Agents a full-page owned-agent directory (#8693) | **defer**：代理目錄改全頁、帳號共用 model catalog，新增 avatar／camera 與 Bestie 同步；需 owned-agent 身分隔離、登出／重試、相機與原生無障礙流程，PR 自述仍未確認最終實機、相機與 live Bestie，不當作 fork 驗收。 |
| `6d719c680a85c98153324809988be37425fba73e` | db: warm the relay read pool toward its ceiling at boot (#8651) | **defer**：開機探測後以每波最多 5 條連線預熱到 reader ceiling，波數受限且失敗不阻擋 readiness；需 Postgres reader 不可達／部分取得、滾動部署總連線上限及與流量重疊時 writer fallback 驗收。 |

### PR 軸

| PR | 狀態 | 完整 head SHA | 裁決與理由 |
| --- | --- | --- | --- |
| [#8689](https://github.com/block/buzz/pull/8689) | CLOSED | `45253c9a35b7fd7d37721594ffad6bd1952106e9` | **skip**：已關閉未合併；錯誤 gzip 解壓移到 isolate 並限 64 KiB，含退役檢查。未自行帶入已關閉來源；若替代修補合併，重驗 gzip bomb、429 及取消。 |
| [#8690](https://github.com/block/buzz/pull/8690) | OPEN | `f7fdd476f6ad8f784e58b2dafad7efcff44eb50a` | **defer**：撤回 #8615 的 Solo 全訊息 push 並移除 lease-size guards；本 fork 未帶入 #8615，不直接套反向修補。等待上游合併並核對實際基底，再驗證 mention-only、DM、租約大小與 NIP-44 邊界。 |
| [#8691](https://github.com/block/buzz/pull/8691) | OPEN | `2fa20c19722e5d1d0471c4166680dcb8a1eaf97e` | **defer**：修 #8650 reload 時 community 為空、設定選單 semantics 及不支援遠端社群的錯誤提示；需與 #8650／#8693 目錄重構一起核對，測試 Add、VoiceOver 與 reload／sign-out。 |
| [#8692](https://github.com/block/buzz/pull/8692) | OPEN | `95a8255a60ce0c8bd492856d3d37819bf5ee2ed8` | **skip**：新增 ARCHITECTURE.md 說明行長 548，超過既有 400 字元拒收門檻；未自行豁免文件。語義上將歷史 DB 失敗從 EOSE 改為 CLOSED，需符合政策的修訂或維護者明確決定，再依其宣告先部署 relay、後 #8688，驗證失敗清理與重播。 |
| [#8693](https://github.com/block/buzz/pull/8693) | MERGED | `246cbbeaaf5c8152d5c6aabc3ccc969f9689b7f5` | **defer**：代理目錄改全頁、帳號共用 model catalog，新增 avatar／camera 與 Bestie 同步；需 owned-agent 身分隔離、登出／重試、相機與原生無障礙流程，PR 自述仍未確認最終實機、相機與 live Bestie，不當作 fork 驗收。 已合併，同一變更的 commit 0cde1fe 已另在 commit 軸裁決，未實際採用。 |
| [#8694](https://github.com/block/buzz/pull/8694) | OPEN | `777107fdbec39c30a4d0b5a62c5e66921207dd20` | **defer**：以 buzz:workflow 與 p-tag owner marker 區分歸屬和 mention，橫跨 core filter、DB event_mentions、push／operator listener 與 mobile；需驗證真正 mention owner 仍通知、歷史／live 一致及舊資料處理，不只改單一用戶端。 |
| [#8695](https://github.com/block/buzz/pull/8695) | OPEN | `8b8a16845e5a7e455712623326128a1ba709a3a4` | **defer**：typing prune 只在值改變時發布，頁面訂閱排除自己且符合 thread scope 的 VisibleTyping；需驗證到期、自己 echo、他人／thread 切換與原生輸入延遲。 |
| [#8696](https://github.com/block/buzz/pull/8696) | OPEN | `d835556200dce52c0b50c6d1c24816c59fd0ca91` | **defer**：0076 以 1s lock_timeout／5s statement_timeout 移除 roster trigger／function，更新 desired-state 與 reconcile；方向符合 docs/database.md，但本 fork 尚未採 #8611，不可提早撤資料庫防護。需先部署應用端替代，再驗證 migration／desired-state、pgschema 重套與現有 relay 相容。 |
| [#8697](https://github.com/block/buzz/pull/8697) | OPEN | `3e495d73e1dbbd7f73271b0fb754236f71bdfca3` | **defer**：只把 prepare_reconnect 註解中的 real clock and RNG 改為 real RNG，與 #8653 後實作對齊；不獨立 cherry-pick 上游仍開放的 PR，合併後隨對應 ACP 同步核對。 |
| [#8698](https://github.com/block/buzz/pull/8698) | OPEN | `ef85d468f7cf2feeea5139050307ace84d40b75f` | **defer**：standalone purge_messages 以 request lease／approved inventory 按 thread 批次刪除，同交易修計數並拒絕未清理附件；未接 dispatcher。需驗證他人回覆／tombstone 保留、租約失效、授權與重試，不能把 handler 當完整使用者刪除流程。 |
| [#8699](https://github.com/block/buzz/pull/8699) | OPEN | `477f9b0689fef5bcf508048251b632146015404e` | **defer**：不只 duration validation：同時升 Node 24.15→24.21、新增 approval decide HTTP endpoint，改授權方法、approval context 與 days／delay 限制；PR 描述仍為空模板。需維護者確認新 HTTP 面符合產品約定，補齊 NIP-98 方法／URL、跨社群／非 approver 拒絕、重送與期限測試後再考慮，不按標題視為小修。 |

### Issue 軸與邊界

以 state=all、created desc 的混合清單讀到低於 #8684，最高編號 #8699；排除 PR 後沒有 #8684 以上的新 issue。因此最新 issue 水位仍為 #8684，不能把 PR 編號灌進 issue 水位。既有 #8674、#8684 的 defer 裁決保留。本次不重新宣稱舊 PR 的 head／state 仍是最新；後續變動另行重新審查。

26 份增量 diff 的 dynamic／control／encoded／inline_space 掃描均為 0；只有 #8692 的 ARCHITECTURE.md 新增行長 548，依規則 skip。掃描沒有替代產品安全審計。新增 commit 未觸碰發布 workflow，未帶入產品碼，FORK.md 的依賴修補與發布 guard 維持原狀。

### 本次驗收

水位更新前完整維護工具 gate exit 0（29 passed in 0.54s、OK）；strict 檢查 exit 1，準確列出待審 15 commit／11 PR。裁決完成後 commit 水位推進到 `6d719c680a85c98153324809988be37425fba73e`、PR #8699，issue 以新清單確認 #8684 已是最新。後續閘門結果記於增量 JSON。

本次只修文件與審查資料，未修產品 bug，先紅後綠回歸測試不適用；strict 的 1→0 是水位驗收，不冒充程式回歸測試。維持 solo 自審，minimalism／elegance／correctness 各 9/10，無本批文件阻擋項。沒有上游 CHANGELOG 或 REVIEW.md 需改，回註在本文件與 DECISIONS.md；文件無英文鏡像。Hermit 啟用仍因 HERMIT_STATE_DIR_RAW 錯誤失敗，未宣稱產品工具鏈或原生驗收通過。
