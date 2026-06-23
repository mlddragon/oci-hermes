# Backup And Restore Runbook

Backups use deployer-owned Restic storage. The Restic passphrase must stay
outside OCI and outside this repo.

## Backup Setup

1. Create a deployer-owned OCI Object Storage bucket.
2. Store the Restic repository URL and passphrase outside the repo.
3. Run `scripts/hermesctl deploy-runtime --host "$HERMES_HOST"` to install the root-owned Restic env file.
4. Enable `hermes-backup.timer` only after reviewing `/etc/systemd/system/hermes-backup.service`.
5. Run `sudo systemctl start hermes-backup.service` on the VM.

## Restore Test

1. Run `scripts/hermesctl backup-test --host "$HERMES_HOST"`.
2. Type `RUN RESTIC BACKUP TEST`.
3. Confirm restore output appears under `/opt/hermes-ai/restore-test/latest`.
4. Confirm the restored files include expected service data and deploy files.
5. Remove test restore data after review if no longer needed.

## Stop Conditions

- Restic passphrase is lost or only stored in OCI.
- Restore cannot read the repository.
- Backup includes raw local secrets that should remain off-VM.
- Restore test has not succeeded before production use.
