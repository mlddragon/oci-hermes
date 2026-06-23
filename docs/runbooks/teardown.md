# Teardown Runbook

Teardown is intentionally manual in v1. Do not destroy resources until backups
and recovery material have been reviewed.

## Steps

1. Run `scripts/hermesctl teardown-plan`.
2. Run a final Restic backup.
3. Run a local encrypted export if needed.
4. Confirm Matrix recovery keys, Restic passphrase, and required notes are stored off-VM.
5. Run `tofu plan -destroy` from `infra/oci/` using the ignored local tfvars.
6. Review every resource that would be destroyed.
7. Destroy only after independent human confirmation.

## Stop Conditions

- No recent successful backup exists.
- Restic restore test has not passed.
- You are not sure which OCI account or compartment is targeted.
- Terraform/OpenTofu state does not match the expected deployment.
