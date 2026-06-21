# Hermes AI OCI Matrix Design Spec

## Goal

Build a subscription-free, secure Hermes AI installation on OCI Always Free that provides chat continuity across macOS, iPad, iPhone, and web through a private Matrix server. The system uses local inference by default, optional OpenAI API calls only with explicit approval, encrypted memory/artifact storage, backups, monitoring, and clear recovery runbooks.

## Non-Goals

- No paid cloud shapes, GPUs, paid load balancers, paid managed databases, HCP Terraform, or recurring paid DNS/domain dependencies in v1.
- No public federation with the Matrix network in v1.
- No public exposure of Ollama, llama.cpp, Hermes Agent APIs, Docker internals, or non-Matrix backend services.
- No Open WebUI in v1. Matrix is the only user-facing chat surface.
- No full autonomous agent behavior in v1. Advanced autonomy is deferred until the foundation is proven.

## Architecture

One OCI Always Free `VM.Standard.A1.Flex` instance runs the stack on Ubuntu 24.04 LTS ARM64. The target size is 4 OCPU, 24 GB RAM, and a 150 GB boot volume, subject to final Always Free eligibility and capacity checks.

Matrix is the public HTTPS client-access layer. Caddy terminates TLS on ports 80/443, proxies Matrix client traffic, and keeps federation disabled. Hermes, Ollama, model services, bot bridge services, and task-execution containers stay private on localhost or private Docker networks.

The user-facing flow is:

1. Element clients connect to the private Matrix homeserver over public HTTPS.
2. The primary user, secondary user, and Hermes interact in encrypted Matrix rooms.
3. Hermes participates as a verified E2EE-capable Matrix bot device.
4. Hermes sends local model requests to Ollama by default.
5. Hermes recommends OpenAI only when useful and requires per-request approval before any API call.
6. Hermes stores only summaries, facts, decisions, and artifacts in encrypted OCI storage, not raw transcript archives.

## OCI And Cost Controls

The account stays on OCI Free Tier/Always Free for v1. Pay-As-You-Go is not enabled unless explicitly revisited after concrete capacity or retention blockers.

The home region must be a US region. Always Free A1 capacity takes priority over latency. If A1 capacity is unavailable, use patient retry/backoff within OCI limits and terms; do not select paid shapes.

Terraform Community Edition is used first for career familiarity, with plain Terraform-compatible HCL that should remain OpenTofu-compatible. Terraform state stays local, encrypted at rest, excluded from git, and backed up encrypted. HCP Terraform is not used.

## DNS And Public Access

The Matrix homeserver uses a neutral DuckDNS name. Preference order:

1. `example-private-1.duckdns.org`
2. `example-private-2.duckdns.org`
3. `example-private-3.duckdns.org`

If those are taken, choose a neutral fallback by using a short random neutral label. Avoid names that reveal services, such as `matrix`, `hermes`, `ai`, `chat`, `server`, or `cloud`.

Use a reserved OCI public IPv4 only if final provisioning confirms it is Always Free-safe. Configure a DuckDNS update script either way so the chosen hostname tracks the current OCI public IP.

## Matrix Design

Use a lightweight compiled Matrix homeserver rather than Synapse. Continuwuity is the default. Immediately before implementation, compare current Continuwuity and Tuwunel releases for ARM64 support, E2EE behavior, registration disablement, federation disablement, media limits, admin/account tooling, backup/restore docs, and known Element/Element X issues. Synapse is only a compatibility fallback if both lightweight servers block required v1 behavior.

Matrix registration is closed after initial account creation. Federation is disabled, and no federation ingress such as port 8448 is exposed.

Initial accounts:

- `admin`: Matrix administration and recovery.
- `primary`: the primary user daily account.
- `secondary`: the secondary user daily account.
- `hermes`: Hermes bot account, display name `Hermes`.
- `ops`: operational alert notifier.

Hermes and ops do not receive Matrix server/admin privileges. Ops does not receive AI or task-execution privileges.

Initial encrypted rooms:

- Primary AI: `primary` + `hermes`
- Secondary AI: `secondary` + `hermes`
- Shared AI: `primary` + `secondary` + `hermes`
- Ops/Admin: `primary` + `admin` + `ops`; the secondary user is excluded for v1 unless changed later
- Recovery/Test: temporary room for E2EE, client, bot, and notification verification

Element-family clients are used across macOS, iPad, iPhone, and web. E2EE, cross-signing, secure key backup, and recovery must be configured and tested for primary and secondary users before production use.

## Hermes Bot And Routing

Hermes joins only rooms where AI participation is desired. The bot runs as an E2EE-capable Matrix client device and must be manually verified from a primary Element client before it is trusted with encrypted-room context. Unexpected new Hermes bot devices or key-store/session resets trigger alerts.

The Matrix bridge is minimal custom code built on an existing E2EE-capable Matrix SDK. Final SDK selection happens during implementation after checking current support and maintenance. The bridge must not implement Matrix encryption directly.

Bot attention rules:

- Watch all messages and infer responses in direct one-human/one-bot rooms.
- Use pause/resume commands.
- Default to mention-only or paused behavior in multi-human rooms unless explicitly changed.

Local inference uses Ollama in v1, with llama.cpp as fallback. The primary local model is Hermes 3 Llama 3.1 8B GGUF `Q4_K_M`. Benchmark local CPU-only latency and tokens/second on OCI A1 before adding any smaller fast local model.

OpenAI is optional and approval-gated. Use one dedicated OpenAI API project/key, not multiple personal ChatGPT subscription accounts. Set the initial monthly budget target to $5, or the lowest practical current project/billing limit if exact $5 enforcement is unavailable. Warn at about 50%, 80%, and 95%.

Routing classes:

- `local-ok`
- `openai-recommended`
- `openai-required`

OpenAI calls require explicit per-request approval in v1. The primary user may approve in Primary AI. The secondary user may approve in Secondary AI. Either approved human user may approve in Shared AI after secondary-user onboarding. Secondary-user onboarding must cover Element login, device verification, recovery key handling, what Hermes can see, what OpenAI approval sends off-box, shared API budget implications, and one successful E2EE recovery/key verification test.

OpenAI approvals use explicit single-use approval IDs. They expire after 15 minutes and are bound to room, approver, operation, and data boundary.

Side-effecting action approvals use explicit single-use approval IDs. They expire after 5 minutes and are bound to room, approver, operation, and data boundary.

## Authority And Sandboxing

Hermes uses a deny-by-default authority model.

Allowed without approval:

- read/chat/summarize/plan behavior
- local reasoning that does not mutate state or call external services

Requires explicit approval:

- file writes
- package installs
- service restarts
- firewall, IAM, or network changes
- cloud API mutations
- outbound messages outside the approved Matrix interaction
- backup deletion
- model/runtime changes
- any external side effect not already allowlisted

Hermes task execution uses Docker sandboxing in v1:

- no `--privileged`
- no `/var/run/docker.sock`
- no host networking
- no broad host mounts such as `/`, `/opt`, `/home`, or Matrix/Hermes service data
- only a dedicated task workspace mount
- CPU, memory, process, and disk limits
- no OCI credentials, Matrix server secrets, backup keys, or root SSH keys by default

Direct host execution requires explicit review and approval. A future microVM/Firecracker-style isolation upgrade path should be documented for higher-risk autonomous workflows.

## Storage And Secrets

Use explicit bind-mounted service data directories under `/opt/hermes-ai/data/`. Do not use anonymous Docker volumes. Document ownership, permissions, and backup inclusion/exclusion for every data path.

Hermes memory and artifacts live in an encrypted mounted directory, manually unlocked after reboot in v1. App-level memory database encryption is deferred unless later risk review requires it. The design remains open to external-secret auto-unlock later if a free and acceptable option is found.

Hermes long-term memory stores only:

- summaries
- durable facts
- decisions
- generated artifacts

Hermes does not store raw transcript chunks as long-term memory.

Runtime secrets live in root-owned per-service files on the VM. Human/master recovery secrets stay off-VM in a password manager plus one offline emergency copy. Do not put master recovery secrets in OCI, Terraform repos, Matrix rooms, or Terraform state.

Secrets requiring off-VM storage include:

- Matrix recovery keys/passphrases
- Restic passphrase
- encrypted Hermes memory unlock material
- OCI API private key metadata and recovery notes
- DuckDNS token
- OpenAI API key metadata and budget/revocation notes

## Networking And Host Hardening

Public ingress:

- SSH 22 only from the primary user's current public IP.
- HTTPS 443 to Caddy for Matrix client access.
- HTTP 80 only if Caddy needs ACME HTTP-01 challenge.

No public ingress:

- Matrix federation such as 8448
- Ollama or llama.cpp
- Hermes Agent raw API
- Docker internal ports
- non-Matrix backend services

Use OCI network rules at the cloud edge plus UFW on Ubuntu. UFW denies inbound by default and mirrors approved OCI ingress. Docker port publishing must be reviewed so internal services are not published to public interfaces.

Use key-only SSH, disable password login, avoid world-open SSH, install fail2ban, enable automatic Ubuntu security updates, and do not add the normal admin user to the Docker group. Use `sudo docker` and `sudo docker compose`.

## Backups And Recovery

Use Restic encrypted backups to OCI Object Storage Always Free plus periodic local export. Store the Restic passphrase outside OCI. Backups run nightly with explicit lock-state reporting.

Backup reports include:

- Matrix/service data included
- Hermes memory/artifact store unlocked and included, or locked and intentionally skipped/covered only as encrypted blobs depending on final storage design
- backup success/failure
- latest restore-test status

Create monthly encrypted local exports outside OCI. Also run manual encrypted local exports after major setup milestones, risky updates, recovery changes, or secret rotations.

At least one restore test must succeed before production use.

## Updates, Monitoring, And Alerts

Updates have two phases:

- Bootstrap: app/container/model updates are manual until backup restore is confirmed.
- Steady state: security/critical updates as soon as practical after pre-update backup and health gate; non-critical fixes weekly; feature/minor app updates monthly.

Model changes require manual approval because model behavior changes are product/trust changes.

Primary alerts go to a dedicated encrypted Matrix admin room after Matrix is stable. Local logs are the source of record. ntfy public free topic is the fallback alert channel for Matrix-down cases. ntfy alert content must be non-sensitive: timestamp, host/service, severity, and generic failure reason only. Do not include secrets, room names, message contents, tokens, or detailed logs.

V1 health checks cover:

- Matrix HTTPS and client login path
- Caddy TLS certificate validity and renewal status
- disk usage and inode pressure
- memory and swap pressure
- latest backup status and latest restore-test status
- Hermes bot sync/session health
- unexpected bot-device events
- local Ollama/Hermes model response
- OpenAI budget usage and warning thresholds
- SSH anomalies and fail2ban status
- update job status and pending security updates

Health checks use service probes or Recovery/Test room and do not log raw Matrix message content.

Audit logs are metadata-only and retained for 90 days. They include approvals, denied actions, OpenAI call metadata, update jobs, backup results, SSH anomalies, bot/device events, timestamps, actors, rooms, and operation IDs. Normal logs exclude raw Matrix message content. Content capture requires explicit temporary debug mode for a specific incident.

## Media Policy

Matrix media uploads are allowed for practical cross-device continuity. Initial per-file upload limit is 25 MB. Configure cleanup/retention rules for stale media/cache where supported. Explicitly saved Hermes artifacts are separate from casual chat attachments.

## Project Layout

Use one structured project repo:

- `infra/oci/`: Terraform-compatible HCL
- `deploy/compose/`: Docker Compose service definitions
- `deploy/caddy/`: Caddy config templates
- `deploy/systemd/`: host service/timer templates
- `scripts/`: health, backup, update, DNS, and operational helpers
- `docs/runbooks/`: setup, recovery, update, backup, and incident runbooks
- `docs/superpowers/`: planning/spec artifacts

Commit templates/examples, not secrets, state, tokens, or generated private material. `.gitignore` must exclude Terraform state, `.terraform/`, `.env`, API keys, Matrix tokens, Restic secrets, generated private keys, and local override files.

## Runbooks

Maintain concise daily operator runbooks plus detailed recovery runbooks.

Daily runbooks cover:

- status checks
- service restart
- manual backup
- local export
- update review
- memory unlock
- OpenAI budget check
- alert review

Recovery runbooks cover:

- full restore
- lost Matrix device
- Matrix key recovery
- DuckDNS/DNS failure
- Caddy/TLS failure
- failed update rollback
- OCI capacity issue
- OCI cost alert
- compromised bot device
- secret rotation

Runbooks reference secret locations but do not include raw secrets.

## Critical Review Gates

1. OCI signup, home region selection, MFA setup, and payment verification.
2. Confirm tenancy limits and that every selected OCI resource is Always Free eligible before provisioning.
3. SSH key, API key, compartment, and IAM policy review before Codex uses credentials.
4. Firewall and public exposure review before opening ports beyond SSH/HTTPS.
5. First model download and service startup review because it consumes disk and memory.
6. Backup and restore test before treating the install as persistent.

## V1 Success Criteria

- Matrix public HTTPS client access works through Caddy with federation disabled and registration closed.
- Element clients work on macOS, iPad, iPhone, and web.
- E2EE, cross-signing, and recovery/key backup are verified for primary and secondary users.
- Matrix rooms are created for Primary AI, Secondary AI, Shared AI, Ops/Admin, and Recovery/Test.
- Hermes joins approved encrypted rooms as a verified E2EE-capable bot.
- Hermes can perform basic chat through Matrix using the local Hermes 3 8B Q4_K_M model.
- OpenAI routing can recommend cloud use and requires explicit per-request approval before any API call.
- OpenAI spend limit target and warning thresholds are configured.
- Restic encrypted backups run nightly with lock-state reporting.
- At least one restore test succeeds before production use.
- Matrix admin-room alerts and ntfy fallback alerts work.
- Health checks cover core services, disk, memory/swap, certificates, backups, updates, SSH anomalies, bot-device events, and OpenAI budget thresholds.
- Advanced sandboxed autonomy is not required for v1 success beyond the deny-by-default framework and approval model.

## Open Issues For Execution-Time Verification

- Verify current OCI Always Free treatment of reserved public IPv4 before reserving one.
- Verify current OCI A1 capacity in US regions before selecting home region.
- Verify current Continuwuity vs Tuwunel release health, ARM64 support, and Element/Element X compatibility.
- Verify current OpenAI API project budget controls and minimum enforceable spend limits.
- Verify final E2EE-capable Matrix SDK choice for the Hermes bridge.
- Verify current DuckDNS hostname availability after login.
