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


def _narrow_stdout(monkeypatch):
    """A stdout whose codec cannot encode the Chinese and emoji the reports contain."""
    import io

    wrapper = io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict")
    monkeypatch.setattr(sys, "stdout", wrapper)
    return wrapper


def test_freshness_check_survives_a_stdout_that_cannot_encode_the_report(
    monkeypatch, tmp_path: Path
) -> None:
    row = {
        "name": "pkg", "source": "package.json", "requirement": "pkg@1", "latest": "2.0.0",
        "hold": "keep 不升級 \U0001f680", "outdated": True, "check_failed": False,
        "no_floor": False, "deferred_reason": "", "minimum": "1", "kind": "npm",
    }
    monkeypatch.setattr(fresh, "collect_sections", lambda *_a: {"npm": [row]})
    report = tmp_path / "report.md"
    monkeypatch.setattr(sys, "argv", ["x", "--output", str(report)])
    _narrow_stdout(monkeypatch)
    assert fresh.main() == 0
    assert "\U0001f680" in report.read_text(encoding="utf-8")


def _row_for(name: str, minimum: str, latest: str, deferrals: dict) -> dict:
    package = {
        "name": name, "minimum": minimum, "requirement": f"{name}@{minimum}",
        "source": "x", "hold": "", "kind": "npm",
    }
    return fresh.collect_status([package], lambda _n: latest, deferrals)[0]


def test_a_deferral_expires_once_the_registry_passes_the_reviewed_release() -> None:
    """The documented rule is "passes that release", whatever precision it was written at:
    a deferral recorded as `1.13` must not survive `1.13.4`."""
    deferrals = {"pkg": ("1.13", "not this month")}
    assert _row_for("pkg", "1.1", "1.13", deferrals)["deferred_reason"] == "not this month"
    expired = _row_for("pkg", "1.1", "1.13.4", deferrals)
    assert expired["deferred_reason"] == ""
    assert fresh.needs_review(expired)


def test_a_deferral_whose_release_cannot_be_read_is_ignored_not_permanent(tmp_path: Path) -> None:
    path = tmp_path / "deferrals.json"
    path.write_text(
        json.dumps(
            {
                "deferrals": {
                    "good": {"deferredLatest": "1.2.3", "reason": "r"},
                    "forever": {"deferredLatest": "latest", "reason": "r"},
                }
            }
        ),
        encoding="utf-8",
    )
    assert set(fresh.load_deferrals(path)) == {"good"}


def test_cargo_member_globs_are_expanded_not_silently_dropped(tmp_path: Path) -> None:
    """`members = ["crates/*"]` names no file; read literally it contributes zero manifests and
    the report stays green over crates it never looked at."""
    (tmp_path / "Cargo.toml").write_text(
        '[workspace]\nmembers = ["crates/*", "tools/one"]\nexclude = ["crates/skipped"]\n',
        encoding="utf-8",
    )
    for member in ("crates/a", "crates/b", "crates/skipped", "tools/one"):
        (tmp_path / member).mkdir(parents=True)
        (tmp_path / member / "Cargo.toml").write_text("[package]\nname='x'\n", encoding="utf-8")
    (tmp_path / "crates" / "not-a-crate").mkdir()
    assert fresh._cargo_manifests(tmp_path) == (
        "Cargo.toml",
        "crates/a/Cargo.toml",
        "crates/b/Cargo.toml",
        "tools/one/Cargo.toml",
    )


def test_a_truncated_registry_response_is_a_failed_lookup_not_a_crash(monkeypatch) -> None:
    """`response.read()` raises http.client.IncompleteRead (not an OSError) on a cut-off body;
    it must become one CHECK FAILED row instead of aborting the whole report."""
    import http.client
    import io

    class Truncated(io.BytesIO):
        def read(self, *_a):
            raise http.client.IncompleteRead(b"{", 100)

    monkeypatch.setattr(fresh.urllib.request, "urlopen", lambda *_a, **_k: Truncated())
    assert fresh._get_json("https://registry.npmjs.org/x/latest") is None


FORK_PATCH_MARKER = "fork patch (SanHsien/buzz)"
FORK_OWNED_DOCS = {"test_fork_tools.py", "FORK.md", "DECISIONS.md"}


def _files_with_fork_patch_marker() -> list[str]:
    import subprocess

    result = subprocess.run(
        ["git", "grep", "-lzF", FORK_PATCH_MARKER, "--", "."],
        cwd=REPO_ROOT, capture_output=True, check=False,
    )
    names = result.stdout.decode("utf-8").split("\0")
    return sorted(n for n in names if n and Path(n).name not in FORK_OWNED_DOCS)


def test_every_file_carrying_a_fork_patch_marker_is_listed_in_fork_md() -> None:
    """FORK.md's difference table is the only place a maintainer learns which upstream-owned
    files the fork has edited; a patch that is not in it is invisible at the next sync."""
    fork_md = (REPO_ROOT / "FORK.md").read_text(encoding="utf-8")
    patched = _files_with_fork_patch_marker()
    assert patched, "marker convention changed; update this test"
    missing = [name for name in patched if name not in fork_md]
    assert not missing, f"fork-patched files absent from FORK.md: {missing}"


def test_deny_toml_marks_the_ignores_the_fork_added() -> None:
    """Upstream owns deny.toml; the marker is what lets a sync tell its ignores from ours."""
    text = (REPO_ROOT / "deny.toml").read_text(encoding="utf-8")
    marker_at = text.index(FORK_PATCH_MARKER)
    assert marker_at < text.index('id = "RUSTSEC-2026-0253"')


def test_crypto_bigint_advisory_is_cleared_by_the_lock_not_by_an_ignore() -> None:
    """RUSTSEC-2026-0387 was first ignored, then fixed by taking upstream's p256 0.14. An ignore
    that comes back would silence the advisory while a vulnerable crypto-bigint sits in the lock;
    the lock is what has to carry the patched release (>= 0.7.6)."""
    assert 'id = "RUSTSEC-2026-0387"' not in (REPO_ROOT / "deny.toml").read_text(encoding="utf-8")
    versions = _locked_versions("Cargo.lock", "crypto-bigint")
    assert versions, "crypto-bigint left the lock; delete this test"
    for version in versions:
        parts = tuple(int(x) for x in version.split(".")[:3])
        assert parts >= (0, 7, 6), f"crypto-bigint {version} is below the patched 0.7.6"


def _locked_versions(lock: str, crate: str) -> list[str]:
    import tomllib

    data = tomllib.loads((REPO_ROOT / lock).read_text(encoding="utf-8"))
    return [p["version"] for p in data["package"] if p["name"] == crate]


# Patched floors for advisories the fork already cleared in the root lock (docs/fork/DECISIONS.md).
# `cargo deny check` reads only the root workspace, so nothing but this test notices when the
# excluded Tauri lock (the desktop app's own dependency set) still carries the vulnerable release.
TAURI_LOCK_PATCHED_FLOORS = {
    "lru": (0, 18, 2),  # RUSTSEC-2026-0253
    "tokio": (1, 54, 1),  # RUSTSEC-2026-0386
    "h2": (0, 4, 16),  # RUSTSEC-2026-0258
    "rtrb": (0, 3, 5),  # RUSTSEC-2026-0274
}


def test_tauri_lock_carries_the_patched_releases_cargo_deny_never_checks() -> None:
    behind = {
        f"{crate} {version}": floor
        for crate, floor in TAURI_LOCK_PATCHED_FLOORS.items()
        for version in _locked_versions("desktop/src-tauri/Cargo.lock", crate)
        if (fresh.release_key(version) or ()) < floor
    }
    assert not behind, f"Tauri Cargo.lock below the patched release: {behind}"


def test_a_floating_tag_with_a_prose_comment_keeps_its_floor() -> None:
    """`@v6 # pinned for X`: the comment is not a version, so the floor comes from the ref."""
    [row] = fresh.parse_workflow_actions(
        "      - uses: actions/checkout@v6 # matches the runner image\n", "x.yml"
    )
    assert row["minimum"] == "6"


def test_cargo_loader_reads_target_specific_dev_dependencies(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "Cargo.toml").write_text(
        '[package]\nname = "x"\nversion = "0.1.0"\n'
        "[target.'cfg(windows)'.dev-dependencies]\nwinsafe = \"0.0.20\"\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(fresh, "CARGO_MANIFESTS", ("Cargo.toml",))
    assert {p["name"] for p in fresh.load_cargo(tmp_path)} == {"winsafe"}


def test_a_cargo_0_0_x_requirement_compares_on_the_patch() -> None:
    """Cargo's caret on 0.0.z allows only that patch, so 0.0.4 must read as newer than 0.0.3."""
    floor = fresh.range_floor("0.0.3", True)
    assert floor == "0.0.3"
    assert fresh.is_newer_version("0.0.4", floor)
    assert fresh.range_floor("^0.2.3", True) == "0.2"
