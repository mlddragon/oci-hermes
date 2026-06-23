# Matrix And E2EE Runbook

Use generic accounts only: `admin`, `primary`, `secondary`, `hermes`, and `ops`.

## Account Setup

1. Create `admin` for homeserver administration and recovery.
2. Create `primary` and `secondary` for daily human use.
3. Create `hermes` for the bot account.
4. Create `ops` for operational alerts.
5. Confirm `hermes` and `ops` do not have server admin privileges.
6. Store the `hermes` password in your password manager. `scripts/hermesctl deploy-runtime` installs it on the VM as `/opt/hermes-ai/secrets/matrix-hermes-password`.
7. Close public registration.
8. Confirm federation is disabled.

## Trusted Inviter Setup

The rendered bridge environment allows invites only from:

- `@admin:<your Matrix server name>`
- `@primary:<your Matrix server name>`

Keep `HERMES_TRUSTED_INVITER_IDS` narrow. Do not add public rooms, guests, or unverified accounts as trusted inviters.

## Room Setup

Create encrypted rooms:

- `Primary AI`: `primary` and `hermes`
- `Secondary AI`: `secondary` and `hermes`
- `Shared AI`: `primary`, `secondary`, and `hermes`
- `Ops/Admin`: `primary`, `admin`, and `ops`
- `Recovery/Test`: temporary validation room

## E2EE Verification

1. Log in with Element on the primary device.
2. Enable secure key backup and record the recovery key outside OCI.
3. Log in from a fresh second client and verify encrypted history recovery.
4. Repeat for the secondary user.
5. Start the bridge profile only after the `hermes` account exists and encrypted rooms are ready:
   `cd /opt/hermes-ai/deploy/compose && sudo docker compose --env-file hermes.env --profile bridge up -d hermes-bridge`
6. Invite `hermes` to `Recovery/Test` from `primary` or `admin`.
7. Verify the `hermes` bot device in Element before trusting replies.
8. Send `!hermes status` in `Recovery/Test`; expect an encrypted reply.
9. Invite `hermes` to an unencrypted test room; expect no answer and a metadata-only audit denial.
10. Treat unexpected bot devices or session resets as incidents.

## Bridge Behavior

- Direct encrypted rooms with one human plus `hermes` respond by default unless paused.
- Multi-human encrypted rooms respond only to `!hermes` commands or mentions.
- Supported commands are `!hermes status`, `!hermes pause`, `!hermes resume`, and `!hermes help`.
- Unencrypted rooms, untrusted inviters, unknown rooms, Ollama failures, and bot session reset concerns deny safely and write metadata-only audit events.
- OpenAI routing is refused in this slice, even if an operator tries to enable it.

## Troubleshooting

1. Check `sudo docker logs hermes-bridge` for startup errors. Do not paste secrets or message contents into issues.
2. Confirm `/opt/hermes-ai/secrets/matrix-hermes-password` exists and is mode `600`.
3. Confirm `/opt/hermes-ai/data/bot-store` persists across restarts.
4. Confirm `/opt/hermes-ai/data/audit/bridge-events.jsonl` contains metadata only.
5. If the crypto store or bot device changes unexpectedly, stop the bridge and follow the incident runbook.
