"""Contract tests for the fork-owned maintenance tools (not the Buzz product)."""

from __future__ import annotations

import json
import re
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
    oldest = 9000 - upstream.TICKET_LIMIT + 1
    baseline["reviewed_pr_through"] = oldest  # page reaches the watermark: complete
    assert upstream.collect_new_tickets(baseline, "pr") is not None
    baseline["reviewed_pr_through"] = oldest - 1  # one number unlisted below the page
    assert upstream.collect_new_tickets(baseline, "pr") is None


def test_cursor_rule_pins_prs_to_this_fork() -> None:
    text = (REPO_ROOT / ".cursor" / "rules" / "no-upstream-pr.mdc").read_text("utf-8")
    assert "alwaysApply: true" in text
    assert "SanHsien/buzz" in text


OWNER_GUARD = "github.repository_owner == 'block'"
PUBLISH_WORKFLOWS = ("docker.yml", "sprig.yml", "sprig-image.yml")
# Jobs that must build on every owner but may only *push* for `block`; their guard lives on the
# push-capable steps (checked below) instead of on the job.
STEP_GUARDED_JOBS = {
    ("docker.yml", "build"),
    ("docker.yml", "push-gateway-build"),
    ("sprig-image.yml", "build"),
}


def _can_write(job: dict) -> bool:
    perms = job.get("permissions") or {}
    return isinstance(perms, dict) and "write" in {perms.get("contents"), perms.get("packages")}


def test_every_publishing_job_outside_the_block_owner_is_skipped() -> None:
    """A tag push (`sprig-v*`) or a dispatch on the fork must not publish what the rolling path
    already refuses to: DECISIONS.md says Sprig publishing stays with the upstream owner."""
    unguarded = []
    for name in PUBLISH_WORKFLOWS:
        for job_id, job in _workflow(name)["jobs"].items():
            if not _can_write(job) or (name, job_id) in STEP_GUARDED_JOBS:
                continue
            if OWNER_GUARD not in str(job.get("if", "")):
                unguarded.append(f"{name}:{job_id}")
    assert not unguarded, f"publishing jobs without the owner guard: {unguarded}"


def test_push_capable_build_steps_carry_the_owner_guard() -> None:
    missing = []
    for name, job_id in sorted(STEP_GUARDED_JOBS):
        for step in _workflow(name)["jobs"][job_id]["steps"]:
            if not str(step.get("uses", "")).startswith("docker/build-push-action"):
                continue
            outputs = str((step.get("with") or {}).get("outputs", ""))
            push = re.search(r"push=\$\{\{.*?\}\}", outputs)
            if push is None or OWNER_GUARD not in push.group(0):
                missing.append(f"{name}:{job_id}:{step.get('name')}")
    assert not missing, f"build-push steps that can push outside block: {missing}"


def test_a_sha_pin_without_a_version_comment_has_no_floor() -> None:
    """The leading hex digits of a SHA are not a version: `34e11487...` read as floor 34."""
    sha_only = "      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5\n"
    [row] = fresh.parse_workflow_actions(sha_only, "x.yml")
    assert row["minimum"] == ""
    # A real version still produces a floor, from the comment or from a floating tag.
    [commented] = fresh.parse_workflow_actions(sha_only.rstrip() + " # v4.3.1\n", "x.yml")
    assert commented["minimum"] == "4.3.1"
    [floating] = fresh.parse_workflow_actions("      - uses: actions/checkout@v6\n", "x.yml")
    assert floating["minimum"] == "6"


def test_no_workflow_pin_in_the_tree_gets_a_floor_from_its_sha() -> None:
    for row in fresh.load_workflow_actions():
        ref = row["requirement"].split("@", 1)[1]
        if re.fullmatch(r"[0-9a-f]{12}", ref):  # label of an uncommented SHA pin
            assert row["minimum"] == "", row


def _hanging_run(*_args, **kwargs):
    """A subprocess.run stand-in for a stalled network: it only returns if given a deadline."""
    import subprocess

    if kwargs.get("timeout") is None:
        raise AssertionError("subprocess.run without a timeout would block until the job is killed")
    raise subprocess.TimeoutExpired(_args[0], kwargs["timeout"])


def test_a_stalled_git_call_is_reported_as_a_failed_check(monkeypatch, tmp_path: Path) -> None:
    import pytest

    monkeypatch.setattr(upstream.subprocess, "run", _hanging_run)
    with pytest.raises(upstream.UpstreamCheckError, match="timed out"):
        upstream.run_git(["fetch", "--quiet"], tmp_path)


def test_a_stalled_gh_call_reads_as_not_checked_not_as_nothing_to_review(monkeypatch) -> None:
    monkeypatch.setattr(upstream.subprocess, "run", _hanging_run)
    baseline = {"repo": "https://github.com/block/buzz.git", "reviewed_pr_through": 1}
    assert upstream.collect_new_tickets(baseline, "pr") is None


def test_a_missing_git_executable_is_reported_as_a_failed_check(monkeypatch, tmp_path: Path) -> None:
    import pytest

    def no_git(*_a, **_k):
        raise FileNotFoundError("git")

    monkeypatch.setattr(upstream.subprocess, "run", no_git)
    with pytest.raises(upstream.UpstreamCheckError, match="git"):
        upstream.run_git(["fetch"], tmp_path)


def test_gh_failure_is_none_never_an_empty_list(monkeypatch) -> None:
    """Pins the contract the report relies on: every way `gh` can fail is `None`."""
    import subprocess

    baseline = {"repo": "https://github.com/block/buzz.git", "reviewed_pr_through": 1}

    def failing(returncode: int, stdout: str):
        return lambda *_a, **_k: subprocess.CompletedProcess([], returncode, stdout, "boom")

    def missing(*_a, **_k):
        raise FileNotFoundError("gh")

    for fake in (failing(1, "[]"), failing(0, "not json"), missing):
        monkeypatch.setattr(upstream.subprocess, "run", fake)
        assert upstream.collect_new_tickets(baseline, "pr") is None
    monkeypatch.setattr(upstream.subprocess, "run", failing(0, "[]"))
    assert upstream.collect_new_tickets(baseline, "pr") == []
