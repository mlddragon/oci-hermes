# First Deployment Runbook

This runbook takes a deployer from a clean checkout to a reviewed OCI plan, then
through gated provisioning and runtime setup. Stop before any step that would
use someone else's cloud, DNS, backup, Matrix, model, or OpenAI account.

## Preconditions

- OCI CLI is installed and authenticated to the deployer's OCI account.
- OpenTofu is installed as `tofu`; Terraform may be used only as a compatible fallback.
- A dedicated Hermes SSH key exists outside the repo.
- A deployer-owned DuckDNS hostname and token are available.
- Restic passphrase is stored outside OCI and outside this repo.
- Matrix recovery secrets will be stored in a password manager and offline copy.

## Review-Only Path

1. Run `scripts/hermesctl doctor`.
2. Run `scripts/hermesctl init`.
3. Run `scripts/hermesctl secrets-check`.
4. Run `scripts/hermesctl render`.
5. Confirm `git status --short` does not show `.hermes/` files.
6. Run `scripts/hermesctl plan`.
7. Review the plan for Always Free-safe resources only.
8. Stop for human review before `apply`.

## Provisioning Path

1. Run `scripts/hermesctl apply`.
2. Type `APPLY OCI HERMES` only after reviewing the plan.
3. Export the assigned host locally as `HERMES_HOST`.
4. Run `scripts/hermesctl bootstrap-host --host "$HERMES_HOST"`.
5. Type `BOOTSTRAP HERMES HOST` only after confirming the host target.
6. Run `scripts/hermesctl deploy-runtime --host "$HERMES_HOST"`.
7. Type `DEPLOY HERMES RUNTIME` only after reviewing rendered files.
8. Enter secrets only when prompted; do not paste them into git-tracked files.

## Post-Provisioning

1. Configure DuckDNS to the assigned OCI public IP.
2. Confirm HTTPS reaches the Matrix client endpoint.
3. Run the Matrix E2EE runbook.
4. Run the model setup runbook.
5. Run the backup and restore-test runbook.
6. Run `scripts/hermesctl verify --host "$HERMES_HOST"`.

## Stop Conditions

- OCI plan includes paid shapes, paid load balancers, managed databases, or reserved public IPv4.
- SSH is open wider than the approved CIDR.
- Any real secret appears in `git status`, `git diff`, CLI output, logs, or docs.
- Backend ports are publicly reachable.
- Matrix E2EE recovery has not been tested.
- Restic restore test has not passed.
