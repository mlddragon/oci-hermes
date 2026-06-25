#!/usr/bin/env python3
import re
import subprocess
import sys
from pathlib import Path

FORBIDDEN_TRACKED_FILE = re.compile(
    r"(^|/)(terraform\.tfstate(\..*)?|\.terraform/|\.terraform\.lock\.hcl|"
    r"\.env(\..*)?|\.hermes/|\.worktrees/|[^/]+\.tfplan|[^/]+\.tfvars(\.json)?)$"
)
FORBIDDEN_TRACKED_DIR = re.compile(
    r"(^|/)(secrets|private|data|models|backups|matrix-data|bot-session|bot-store)/"
)

REQUIRED_PLANNING_FILES = (
    Path("docs/superpowers/specs/2026-06-21-hermes-ai-oci-matrix-design.md"),
    Path("docs/superpowers/plans/2026-06-21-hermes-ai-oci-matrix-execution.md"),
)


def tracked_paths() -> list[str]:
    return subprocess.check_output(["git", "ls-files"], text=True).splitlines()


def is_forbidden_tracked_path(path: str) -> bool:
    return bool(FORBIDDEN_TRACKED_FILE.search(path) or FORBIDDEN_TRACKED_DIR.search(path))


def forbidden_tracked_paths(paths: list[str]) -> list[str]:
    return [path for path in paths if is_forbidden_tracked_path(path)]


def main() -> int:
    matches = forbidden_tracked_paths(tracked_paths())
    if matches:
        print("Forbidden local, secret, state, or runtime artifact is tracked.", file=sys.stderr)
        for path in matches:
            print(path, file=sys.stderr)
        return 1

    missing = [str(path) for path in REQUIRED_PLANNING_FILES if not path.is_file()]
    if missing:
        print("Missing required planning files:", file=sys.stderr)
        for path in missing:
            print(path, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
