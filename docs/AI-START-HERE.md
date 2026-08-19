# AI Start Here — Public Repository Boundary

This public repository is self-contained for contributors and automated agents. It does not advertise or locate maintainer-private systems.

## Start in this order

1. Read `AGENTS.md`, `SECURITY.md`, and the task-relevant design, plan, or runbook.
2. Refresh the repository and inspect the live checkout before relying on remembered state.
3. Use only this repository and context explicitly supplied with the task.
4. If a decision requires non-public maintainer input, state the missing decision and ask a maintainer for the minimum information needed.
5. Never seek, infer, disclose, or persist maintainer-private context in public issues, pull requests, commits, logs, fixtures, or examples.

## Repository boundary

| Subject | Authoritative source |
|---|---|
| Technical design, deployment tooling, infrastructure definitions, runbooks, code, security boundary, licensing, and repository history | This repository and its refreshed checkout |
| Live provider accounts, deployment state, secrets, endpoints, and runtime data | Deployer-owned systems outside this repository; do not infer or request access unless the task explicitly authorizes it |
| A non-public maintainer decision needed to proceed | Ask a maintainer for the minimum decision or sanitized context needed |
| Temporary analysis and execution context | The current task or chat; non-authoritative until written back to this repository where appropriate |

The repository provides deploy tooling and runbooks. It does not prove that a live deployment exists or satisfies production, backup, restore, E2EE, or acceptance gates.

## Conflict and write-back rules

1. Follow explicit task instructions within their stated scope.
2. Resolve repository-owned facts from the refreshed repository rather than chat memory.
3. Preserve and report genuine conflicts or missing maintainer decisions instead of guessing.
4. Write repository changes through a branch and pull request with applicable tests, hygiene, secret scans, and runbook updates.
5. Reference public repository paths, issues, pull requests, releases, or commits when recording technical work.
6. Never put private organizational material or deployer-specific data in public git, issues, pull requests, logs, or examples.

## Before reporting completion

- Verify the worktree and branch state.
- Verify the base and remote branch resolve to the intended commits.
- Verify the pull request and relevant checks.
- Report unavailable evidence, unresolved conflicts, and any unproven live-deployment gates.
