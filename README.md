# OCI Hermes

OCI Hermes is a public, account-neutral project for hydrating a private Hermes AI environment on cloud infrastructure.

The v1 target is a private-use Hermes deployment on OCI Always Free: Matrix for the user-facing chat surface, a local LLM runtime by default, optional external model calls only after explicit approval, encrypted operational storage, backups, monitoring, and recovery runbooks.

## Current Status

This repository is in deploy-tooling scaffold phase. The design and execution checklist are checked in under `docs/superpowers/`, and the safe CLI entrypoint is `scripts/hermesctl`:

- [Design spec](docs/superpowers/specs/2026-06-21-hermes-ai-oci-matrix-design.md)
- [Execution checklist](docs/superpowers/plans/2026-06-21-hermes-ai-oci-matrix-execution.md)
- [First deployment runbook](docs/runbooks/first-deployment.md)

Safe local review flow:

```bash
scripts/hermesctl doctor
scripts/hermesctl init
scripts/hermesctl secrets-check
scripts/hermesctl render
scripts/hermesctl plan
```

Commands after `plan` may create or change deployer-owned cloud or host
resources and require typed confirmation.

## Project Goals

- Hydrate reproducible cloud environments for private Hermes AI deployments.
- Keep deployer infrastructure isolated to the deployer's own provider accounts.
- Prefer local inference and private services by default.
- Keep secrets, Terraform state, provider credentials, model tokens, Matrix recovery keys, and backup passphrases out of git.
- Make the repository public and contribution-friendly through forks, branches, and pull requests.
- Preserve the spirit of open collaboration: use it, fork it, deploy it, sell services around it, and keep distributed changes to project files open under the same license.

## Account And Provider Boundary

Every deployer must use their own cloud, DNS, backup, and model provider accounts.

This project must not include or depend on any maintainer-owned provider account, billing profile, API key, Terraform state backend, DNS token, storage bucket, Matrix homeserver data, model cache, or deployed service endpoint. Examples and templates must use placeholders or deployer-owned values only.

## Planned Layout

```text
infra/oci/          Terraform-compatible OCI infrastructure
deploy/compose/     Docker Compose service definitions
deploy/caddy/       Caddy configuration templates
deploy/systemd/     Host service and timer templates
scripts/            Health, backup, update, DNS, and operational helpers
docs/runbooks/      Setup, recovery, update, backup, and incident runbooks
docs/superpowers/   Design specs and execution plans
```

## Contribution Model

This is intended to be a public GitHub repository. Forks, feature branches, and pull requests from authenticated GitHub users are welcome.

Before opening a pull request:

1. Keep provider-specific values out of the repository.
2. Use placeholders for account IDs, hostnames, email addresses, tokens, and keys.
3. Document security impact for infrastructure, identity, network, secrets, backup, or model-routing changes.
4. Update the relevant runbook or design document when operational behavior changes.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## License

Licensed under the Mozilla Public License 2.0. See [LICENSE](LICENSE).

Plain English intent: use this project freely, credit the work by keeping license notices intact, and keep distributed modifications to this repository's files open source. Private deployments, local secrets, account-specific configuration, and separate client work do not belong in this repository.

The project may later split documentation under a documentation-specific license such as CC BY 4.0, while keeping code, templates, and scripts under MPL-2.0.
