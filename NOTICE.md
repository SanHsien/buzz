# NOTICE

This repository is a maintained fork of [buzz](https://github.com/block/buzz).

- Original Author: [Block, Inc.](https://github.com/block)
- Upstream Repository: https://github.com/block/buzz
- License: Apache License 2.0 (see LICENSE)

Modifications and fork maintenance infrastructure by SanHsien:
- Upstream synchronization ledger and automation (`tools/check_upstream_updates.py`, `tools/upstream_baseline.json`)
- Declared-dependency freshness check (`tools/check_dependency_freshness.py`)
- Dependabot and CodeQL configuration (`.github/dependabot.yml`, `.github/workflows/codeql.yml`)
- Fork documentation (`FORK.md`, `docs/fork/`)

The fork adds no product features. Its edits to upstream-owned files (CI workflow gates, lockfile
dependency updates, `deny.toml` ignores, a test-only lock in `buzz-dev-mcp`) are listed in
`FORK.md`.
