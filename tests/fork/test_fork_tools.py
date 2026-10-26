"""Contract tests for the fork-owned maintenance tools (not the Buzz product)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import check_dependency_freshness as fresh  # noqa: E402
import check_upstream_updates as upstream  # noqa: E402

WORKFLOWS = REPO_ROOT / ".github" / "workflows"


def _workflow(name: str) -> dict:
    return yaml.safe_load((WORKFLOWS / name).read_text(encoding="utf-8"))


def test_baseline_points_at_block_buzz_with_all_three_watermarks() -> None:
    baseline = upstream.load_baseline()
    assert baseline["repo"] == "https://github.com/block/buzz.git"
    assert len(baseline["reviewed_through"]) == 40
    assert isinstance(baseline["reviewed_pr_through"], int)
    assert isinstance(baseline["reviewed_issue_through"], int)


def test_upstream_check_workflow_gives_gh_a_token_and_fails_closed() -> None:
    text = (WORKFLOWS / "upstream-check.yml").read_text(encoding="utf-8")
    assert "GH_TOKEN: ${{ github.token }}" in text
    assert "--strict" in text
    assert "fetch-depth: 0" in text


def test_cargo_loader_reads_workspace_dependencies(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "Cargo.toml").write_text(
        '[workspace]\nmembers = []\n[workspace.dependencies]\n'
        'tokio = { version = "1", features = ["rt"] }\nserde = "1"\n'
        'local = { path = "crates/local" }\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(fresh, "CARGO_MANIFESTS", ("Cargo.toml",))
    names = {p["name"] for p in fresh.load_cargo(tmp_path)}
    assert names == {"tokio", "serde"}


def test_every_declared_manifest_is_read_from_the_real_tree() -> None:
    cargo = fresh.load_cargo()
    npm = fresh.load_npm()
    assert any(p["name"] == "tokio" for p in cargo)
    assert any(p["source"].startswith("crates/") for p in cargo)
    assert npm
    for name in fresh.CARGO_MANIFESTS + fresh.NPM_MANIFESTS:
        assert (REPO_ROOT / name).is_file(), name


def test_dependabot_covers_every_ecosystem_the_freshness_check_reads() -> None:
    config = yaml.safe_load((REPO_ROOT / ".github" / "dependabot.yml").read_text("utf-8"))
    ecosystems = {u["package-ecosystem"] for u in config["updates"]}
    assert {"github-actions", "cargo", "npm"} <= ecosystems
    assert set(fresh.ECOSYSTEMS) <= ecosystems


def test_dependabot_directories_exist() -> None:
    config = yaml.safe_load((REPO_ROOT / ".github" / "dependabot.yml").read_text("utf-8"))
    for update in config["updates"]:
        assert (REPO_ROOT / update["directory"].lstrip("/")).is_dir(), update["directory"]


def test_codeql_matrix_matches_languages_the_repo_has() -> None:
    languages = set(_workflow("codeql.yml")["jobs"]["analyze"]["strategy"]["matrix"]["language"])
    assert languages == {"javascript-typescript", "rust", "actions", "python"}
    assert any(REPO_ROOT.glob("crates/*/src/**/*.rs"))
    assert any((REPO_ROOT / "desktop").glob("src/**/*.ts*"))


def test_every_deferral_is_complete_enough_for_the_loader_to_keep_it() -> None:
    data = json.loads((REPO_ROOT / ".github" / "dependency-deferrals.json").read_text("utf-8"))
    assert isinstance(data["deferrals"], dict) and data["deferrals"]
    for name, entry in data["deferrals"].items():
        assert fresh.release_key(str(entry.get("deferredLatest", ""))) is not None, name
        assert str(entry.get("reason", "")).strip(), name
    assert len(fresh.load_deferrals()) == len(data["deferrals"])


def test_cargo_manifests_include_every_member_of_both_workspaces() -> None:
    import tomllib

    for root in ("", "desktop/src-tauri/"):
        data = tomllib.loads((REPO_ROOT / f"{root}Cargo.toml").read_text("utf-8"))
        for member in data["workspace"]["members"]:
            assert f"{root}{member}/Cargo.toml" in fresh.CARGO_MANIFESTS, f"{root}{member}"


def test_a_full_ticket_page_above_the_watermark_is_not_checked(monkeypatch) -> None:
    """`gh` truncates silently; advancing the watermark past unlisted items skips them."""
    import subprocess

    page = [{"number": 9000 - i, "title": "t"} for i in range(upstream.TICKET_LIMIT)]

    def fake_run(*_a, **_k):
        return subprocess.CompletedProcess([], 0, stdout=json.dumps(page), stderr="")

    monkeypatch.setattr(upstream.subprocess, "run", fake_run)
    baseline = {"repo": "https://github.com/block/buzz.git", "reviewed_pr_through": 100}
    assert upstream.collect_new_tickets(baseline, "pr") is None
    baseline["reviewed_pr_through"] = 8500  # page reaches back past the watermark: complete
    assert upstream.collect_new_tickets(baseline, "pr") is not None


def test_cursor_rule_pins_prs_to_this_fork() -> None:
    text = (REPO_ROOT / ".cursor" / "rules" / "no-upstream-pr.mdc").read_text("utf-8")
    assert "alwaysApply: true" in text
    assert "SanHsien/buzz" in text
