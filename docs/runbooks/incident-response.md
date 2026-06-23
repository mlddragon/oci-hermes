# Incident Response Runbook

Keep incident notes metadata-only. Do not paste Matrix message contents, secrets,
recovery keys, tokens, or private keys into tickets or chat.

## Common Incidents

- Unexpected Hermes bot device.
- Hermes crypto store reset or session mismatch.
- Hermes reply in an unencrypted room.
- Matrix E2EE recovery failure.
- DuckDNS or TLS failure.
- OCI cost alert.
- Backup failure.
- Failed update.
- SSH anomaly or fail2ban activity.

## First Actions

1. Preserve local logs on the VM.
2. Rotate the smallest affected secret first.
3. Disable risky services before debugging if exposure is suspected.
4. Confirm OCI ingress and UFW still match the expected rules.
5. Run `scripts/hermesctl status --host "$HERMES_HOST"`.
6. Escalate to full restore only after backup integrity is confirmed.

## Hermes Bridge Incidents

1. Stop the bridge profile: `cd /opt/hermes-ai/deploy/compose && sudo docker compose --env-file hermes.env --profile bridge stop hermes-bridge`.
2. Review `/opt/hermes-ai/data/audit/bridge-events.jsonl` for metadata-only event patterns.
3. If an unexpected bot device appears, rotate the `hermes` Matrix password and remove the device from Element before restarting.
4. If the crypto store reset unexpectedly, preserve `/opt/hermes-ai/data/bot-store` for investigation and restore from the latest known-good backup.
5. If the bridge answered in an unencrypted room, keep it stopped and treat it as a security bug.

## Stop Conditions

- A secret is suspected exposed.
- Matrix bot session store is reset unexpectedly.
- Hermes answers in an unencrypted room.
- OCI billing shows unexpected spend.
- Backend service is publicly reachable.
