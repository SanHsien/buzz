# 上游同步

- 上游：`block/buzz`（`main`）。水位在 `tools/upstream_baseline.json`（commit／PR／issue 三個）。
- 每週 `upstream-check.yml` 列出水位之後的新 commit／PR／issue（`--state all`）；有新東西就紅燈，審完才推進水位。
- 產品碼與上游相同時，審查結論＝「是否要把這些 commit 帶進來」。帶進來用 `git fetch upstream` 後 cherry-pick 或手動移植（2026-11-17 起本線歷史已壓縮成單一根提交，與上游沒有共同歷史，不能 fast-forward 或 merge，見 `DECISIONS.md` 同日條目）；**移植做法不是硬套 diff**，先確認缺陷在本 fork 存在。
- 上游 PR 取目前的 head 審查；diff 出現行內長串空白後的程式、超長單行、`eval`／`new Function(`、往 `global` 掛 `require`、長 base64／hex 就拒收並記進 `DECISIONS.md`。
- 上游 workflow 在 fork 上也會跑（見 `DECISIONS.md` 的 fork CI 條目）。帶進新 commit 前先確認不會把它們弄紅。
- 不對上游開 PR、不 push、不留言。
