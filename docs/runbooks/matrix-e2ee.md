# Matrix And E2EE Runbook

Use generic accounts only: `admin`, `primary`, `secondary`, `hermes`, and `ops`.

## Account Setup

1. Create `admin` for homeserver administration and recovery.
2. Create `primary` and `secondary` for daily human use.
3. Create `hermes` for the bot account.
4. Create `ops` for operational alerts.
5. Confirm `hermes` and `ops` do not have server admin privileges.
6. Close public registration.
7. Confirm federation is disabled.

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
5. Verify the `hermes` bot device from the primary client only after a reviewed E2EE bridge exists.
6. Treat unexpected bot devices or session resets as incidents.

## Current Bridge Boundary

The checked-in bridge container refuses to start by default. This is intentional
until a reviewed E2EE-capable Matrix SDK implementation is added. Do not replace
it with a plaintext bot for encrypted rooms.
