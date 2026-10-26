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
    assert languages == {"javascript-typescript", "rust", "actions"}
    assert any(REPO_ROOT.glob("crates/*/src/**/*.rs"))
    assert any((REPO_ROOT / "desktop").glob("src/**/*.ts*"))


def test_deferrals_file_is_valid_json_with_a_deferrals_map() -> None:
    data = json.loads((REPO_ROOT / ".github" / "dependency-deferrals.json").read_text("utf-8"))
    assert isinstance(data["deferrals"], dict)


def test_cursor_rule_pins_prs_to_this_fork() -> None:
    text = (REPO_ROOT / ".cursor" / "rules" / "no-upstream-pr.mdc").read_text("utf-8")
    assert "alwaysApply: true" in text
    assert "SanHsien/buzz" in text
