# AGENTS.md

## Project Scope

OCI Hermes hydrates private Hermes AI environments on cloud platforms. The first supported target is OCI Always Free hosting for Hermes with a local LLM runtime and private Matrix access.

This repo is public and account-neutral. Contributors and automated agents must not add maintainer-owned provider identifiers, live endpoints, secrets, Terraform state, personal Matrix data, backup material, model credentials, or anything that ties a deployment to someone else's account.

## Expected Project Shape

- `infra/oci/`: Terraform-compatible OCI infrastructure.
- `deploy/compose/`: Docker Compose service definitions.
- `deploy/caddy/`: Caddy templates for HTTPS and reverse proxying.
- `deploy/systemd/`: Host service and timer units.
- `scripts/`: Operational helpers for DNS, backup, health, update, and restore workflows.
- `docs/runbooks/`: Human-run operational procedures.
- `docs/superpowers/`: Design specs and implementation plans.

## Agent Rules

- Treat this as infrastructure/security-sensitive work.
- Do not invent provider account IDs, OCIDs, bucket names, DNS tokens, hostnames, API keys, Matrix recovery secrets, backup passphrases, or state backends.
- Do not commit Terraform state, `.terraform/`, `.env`, key material, generated private keys, Matrix tokens, model-provider tokens, local model caches, or backup artifacts.
- Keep examples deployer-owned and placeholder-based.
- Prefer explicit allowlists and deny-by-default network, identity, and runtime behavior.
- Keep Ollama, llama.cpp, Hermes agent APIs, Docker internals, and non-Matrix backend services private unless a reviewed design explicitly changes that.
- When changing deployment behavior, update the matching runbook and include manual verification steps.
- When changing security posture, document the threat model impact in the pull request.
- Use existing project layout before introducing new directories.

## Deployment Boundary

Anyone deploying from this repo must provision into their own provider accounts. The repository must not assume access to the maintainer's accounts or any other contributor's accounts.

## Current Implementation Stage

The repository currently contains design and execution planning materials plus scaffold configuration. Infrastructure, deployment, and operational scripts should be added incrementally behind reviewed pull requests.
