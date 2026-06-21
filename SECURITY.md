# Security Policy

## Supported Scope

Security reports are welcome for repository content, infrastructure templates, deployment scripts, runbooks, and operational assumptions.

Live deployments are outside the control of this repository. Each deployer is responsible for their own cloud accounts, DNS, secrets, backups, Matrix homeserver data, and model-provider accounts.

## Sensitive Material

Do not open public issues or pull requests containing:

- Cloud provider credentials or account identifiers.
- API keys, SSH private keys, Matrix recovery keys, backup passphrases, or model-provider tokens.
- Terraform state or plan output containing sensitive values.
- Private Matrix messages, homeserver data, bot session stores, or backup contents.
- Maintainer-owned deployment endpoints or account details.

If sensitive material is accidentally committed, revoke or rotate it first, then remove it from the repository history through the appropriate GitHub process.

## Design Defaults

- Deployer-owned provider accounts only.
- Local inference by default.
- Explicit approval for external model calls.
- No public exposure for non-Matrix backend services.
- Deny-by-default authority for side effects.
- Metadata-only operational and audit logs.

## Reporting

For now, open a GitHub security advisory if available, or contact the repository owner through GitHub. Do not include secrets in the initial report.
