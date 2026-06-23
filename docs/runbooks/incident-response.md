# Incident Response Runbook

Keep incident notes metadata-only. Do not paste Matrix message contents, secrets,
recovery keys, tokens, or private keys into tickets or chat.

## Common Incidents

- Unexpected Hermes bot device.
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

## Stop Conditions

- A secret is suspected exposed.
- Matrix bot session store is reset unexpectedly.
- OCI billing shows unexpected spend.
- Backend service is publicly reachable.
