# Hermes AI OCI Matrix Execution Checklist

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this checklist task-by-task. Stop at the review gates before proceeding.

**Goal:** Build the approved Hermes AI + private Matrix continuity system on OCI Always Free.

**Source Spec:** `docs/superpowers/specs/2026-06-21-hermes-ai-oci-matrix-design.md`

---

## Gate 1: Account Bootstrap

- [ ] Create OCI Free Tier account.
- [ ] Choose a US home region, prioritizing Always Free A1 capacity over latency.
- [ ] Enable MFA.
- [ ] Create daily admin identity separate from root/bootstrap identity.
- [ ] Create compartment `hermes-free`.
- [ ] Configure OCI budget/usage alert at the minimum useful threshold.
- [ ] Confirm account remains Free Tier/Always Free.
- [ ] Do not upgrade to Pay-As-You-Go.
- [ ] Stop for user review.

## Local Workstation Setup

- [ ] Generate or confirm SSH keypair.
- [ ] Install OCI CLI.
- [ ] Configure OCI CLI/API key after user approval.
- [ ] Install Terraform Community Edition.
- [ ] Create repo layout:
  - `infra/oci/`
  - `deploy/compose/`
  - `deploy/caddy/`
  - `deploy/systemd/`
  - `scripts/`
  - `docs/runbooks/`
  - `docs/superpowers/`
- [ ] Add `.gitignore` for Terraform state, `.terraform/`, `.env`, API keys, Matrix tokens, Restic secrets, generated private keys, and local overrides.
- [ ] Store human/master secrets in password manager plus offline emergency copy.

## DNS Setup

- [ ] Log in to DuckDNS.
- [ ] Choose a deployer-owned DuckDNS hostname such as `REPLACE_WITH_YOUR_DUCKDNS_HOSTNAME`.
- [ ] Use a short random neutral label that does not reveal services such as `matrix`, `hermes`, `ai`, `chat`, `server`, or `cloud`.
- [ ] Store DuckDNS token in password manager.
- [ ] Later store DuckDNS runtime token only in root-owned VM secret file.

## Gate 2: Terraform Plan

- [ ] Write Terraform-compatible HCL for:
  - VCN
  - public subnet
  - internet gateway
  - NSG/security rules
  - A1 Flex VM
  - 150 GB boot volume
  - SSH key attachment
  - optional reserved public IPv4 only if confirmed Always Free-safe
- [ ] Use local encrypted Terraform state only.
- [ ] Run Terraform plan.
- [ ] Verify every planned OCI resource is Always Free-safe.
- [ ] Verify ingress:
  - SSH from the primary user's current IP only
  - HTTP/HTTPS for Caddy only
  - no 8448 federation
  - no backend ports
- [ ] Stop for user review before apply.

## Provision OCI

- [ ] Apply reviewed Terraform.
- [ ] If A1 capacity is unavailable, use patient retry/backoff; do not select paid shape.
- [ ] Confirm public IP.
- [ ] Configure DuckDNS update script.
- [ ] Confirm hostname resolves to OCI public IP.

## Host Hardening

- [ ] SSH in with key.
- [ ] Update Ubuntu 24.04 LTS ARM64.
- [ ] Disable password SSH login.
- [ ] Confirm root SSH posture is safe.
- [ ] Install and configure UFW.
- [ ] Mirror approved OCI ingress rules in UFW.
- [ ] Install fail2ban.
- [ ] Enable unattended Ubuntu security updates.
- [ ] Set timezone to `America/Chicago`.
- [ ] Reboot and confirm SSH still works.

## Runtime Layout

- [ ] Install Docker Engine and Docker Compose plugin.
- [ ] Do not add admin user to Docker group; use `sudo`.
- [ ] Install Caddy as host service.
- [ ] Create `/opt/hermes-ai`.
- [ ] Create explicit bind-mounted data directories under `/opt/hermes-ai/data/`.
- [ ] Create `/opt/hermes-ai/models`.
- [ ] Create `/opt/hermes-ai/backups`.
- [ ] Document ownership, permissions, and backup inclusion/exclusion.
- [ ] Confirm no anonymous Docker volumes are used.

## Matrix Homeserver

- [ ] Compare current Continuwuity and Tuwunel releases for required v1 behavior.
- [ ] Use Continuwuity unless Tuwunel clearly wins or Continuwuity blocks v1.
- [ ] Use Synapse only if both lightweight servers block required behavior.
- [ ] Deploy Matrix via Docker Compose with explicit bind mounts.
- [ ] Disable federation.
- [ ] Disable public registration after initial account creation.
- [ ] Set 25 MB media upload limit.
- [ ] Configure media cleanup/retention where supported.
- [ ] Create accounts:
  - `admin`
  - `primary`
  - `secondary`
  - `hermes`
  - `ops`
- [ ] Ensure `hermes` and `ops` have no admin privileges.

## HTTPS And Exposure

- [ ] Configure Caddy for the DuckDNS hostname.
- [ ] Proxy only Matrix client traffic to the homeserver.
- [ ] Obtain trusted TLS certificate.
- [ ] Keep 8448 closed.
- [ ] Confirm Ollama, Hermes Agent, Docker internals, and non-Matrix backend services are not externally reachable.
- [ ] Run external port check.

## Element And E2EE

- [ ] Install Element-family clients on macOS, iPad, iPhone, and web.
- [ ] Log in primary and secondary users.
- [ ] Enable E2EE, cross-signing, and secure key backup.
- [ ] Store recovery keys/passphrases outside OCI.
- [ ] Test encrypted history recovery from a fresh client login for primary and secondary users.
- [ ] Create rooms:
  - Primary AI
  - Secondary AI
  - Shared AI
  - Ops/Admin
  - Recovery/Test

## Local Model

- [ ] Install Ollama on ARM64.
- [ ] Pull `NousResearch/Hermes-3-Llama-3.1-8B-GGUF:Q4_K_M`.
- [ ] Bind model service to localhost/private network only.
- [ ] Run terminal inference test.
- [ ] Benchmark representative prompts.
- [ ] Measure memory/swap pressure.
- [ ] Stop for user review if disk, memory, or performance is unacceptable.

## OpenAI Provider

- [ ] Create one dedicated OpenAI API project/key for Hermes.
- [ ] Set initial budget target to $5/month or lowest practical current limit.
- [ ] Configure warnings at about 50%, 80%, and 95%.
- [ ] Store API key only in root-owned service secret file.
- [ ] Keep API key out of Hermes task sandbox.
- [ ] Implement metadata-only OpenAI call logging.

## Hermes Agent And Matrix Bridge

- [ ] Install Hermes Agent.
- [ ] Run `hermes --version`.
- [ ] Run `hermes doctor`.
- [ ] Configure Hermes to use local model endpoint.
- [ ] Select E2EE-capable Matrix SDK for bridge.
- [ ] Implement minimal bridge:
  - Matrix login/sync/decrypt/send
  - persistent bot session/key store
  - room policy
  - approval handling
  - local/OpenAI routing
  - pause/resume
  - metadata-only audit logging
- [ ] Verify `@hermes` device from primary Element client.
- [ ] Alert on unexpected new bot device or session reset.
- [ ] Do not read Matrix homeserver database for plaintext.

## Hermes Memory And Authority

- [ ] Create encrypted mounted directory for Hermes memory/artifacts.
- [ ] Require manual unlock after reboot in v1.
- [ ] Store summaries, facts, decisions, and artifacts only.
- [ ] Do not persist raw transcript chunks as long-term memory.
- [ ] Implement deny-by-default authority model.
- [ ] Implement OpenAI approval IDs:
  - single-use
  - expire after 15 minutes
  - bound to room, approver, operation, data boundary
- [ ] Implement side-effect approval IDs:
  - single-use
  - expire after 5 minutes
  - bound to room, approver, operation, data boundary
- [ ] Log approvals and denied actions for 90 days, metadata only.

## Task Sandbox

- [ ] Configure Docker task sandbox separate from service Compose stack.
- [ ] No privileged mode.
- [ ] No Docker socket mount.
- [ ] No host networking.
- [ ] Mount only dedicated task workspace.
- [ ] Apply CPU, memory, process, and disk limits.
- [ ] Do not inject OCI, Matrix, backup, root SSH, or broad service secrets.
- [ ] Document future microVM upgrade path.

## Backups

- [ ] Configure Restic repository in OCI Object Storage Always Free.
- [ ] Store Restic passphrase outside OCI.
- [ ] Schedule nightly backups.
- [ ] Include lock-state reporting.
- [ ] Schedule monthly encrypted local export outside OCI.
- [ ] Run manual local export after major milestones/risky changes.
- [ ] Run restore test.
- [ ] Stop for user review before production use.

## Monitoring And Alerts

- [ ] Configure Ops/Admin Matrix alert room.
- [ ] Configure `@ops` notifier.
- [ ] Configure ntfy public free topic fallback with non-sensitive alert content only.
- [ ] Implement health checks for:
  - Matrix HTTPS/login
  - Caddy TLS
  - disk/inodes
  - memory/swap
  - backup/restore status
  - Hermes bot sync/session
  - unexpected bot devices
  - local model response
  - OpenAI budget
  - SSH anomalies/fail2ban
  - update status
- [ ] Retain metadata-only operational/security logs for 90 days.
- [ ] Exclude raw Matrix message content from normal logs.

## Updates

- [ ] Bootstrap phase: app/container/model updates are manual until restore is proven.
- [ ] Steady state after restore proof:
  - security/critical updates as soon as practical after backup/health gate
  - non-critical fixes weekly
  - feature/minor app updates monthly
  - model changes manual approval only
- [ ] Each update job checks pre-update backup, recent restore-test status, health checks, and reports results.

## Runbooks

- [ ] Write concise daily runbooks:
  - status check
  - service restart
  - manual backup
  - local export
  - update review
  - memory unlock
  - OpenAI budget check
  - alert review
- [ ] Write detailed recovery runbooks:
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
- [ ] Reference secret locations only; do not include raw secrets.

## V1 Acceptance

- [ ] Matrix public HTTPS works.
- [ ] Federation disabled and registration closed.
- [ ] Element clients work on macOS, iPad, iPhone, and web.
- [ ] Primary and secondary user E2EE recovery verified.
- [ ] Hermes bot verified and working in approved encrypted rooms.
- [ ] Local Hermes 8B chat works through Matrix.
- [ ] OpenAI approval-gated routing works.
- [ ] Backups, restore test, alerts, and health checks work.
- [ ] No non-Matrix backend ports are public.
- [ ] Advanced autonomy remains deferred beyond deny-by-default framework and approved sandbox.
