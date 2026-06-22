# Contributing

OCI Hermes is public and accepts contributions through forks, branches, and pull requests from authenticated GitHub users.

## Ground Rules

- Keep deployer-specific values out of git.
- Use placeholders for provider account IDs, OCIDs, regions, bucket names, DNS records, tokens, keys, emails, and hostnames.
- Do not commit secrets, Terraform state, generated private keys, local model caches, Matrix data, backup artifacts, or `.env` files.
- Keep changes scoped. Infrastructure, runtime, security, and operations changes should include docs or runbook updates.
- Prefer provider-neutral language where possible; OCI is the first implementation target, not a requirement for every future design.
- By contributing, you agree that your contribution is licensed under this repository's current license structure. Today, that is MPL-2.0 for the whole repository.

## Pull Requests

1. Fork the repository or create a feature branch.
2. Make a focused change.
3. Run applicable checks.
4. Open a pull request using the template.

For infrastructure or deployment changes, include:

- What resources or services are affected.
- Whether the change can create cost.
- Which ports or identities are exposed.
- Which secrets are required and where they should live outside git.
- Manual verification steps.

## Local Development

This scaffold intentionally avoids live provider credentials. Work against examples, local checks, and disposable deployer-owned test accounts only.

Before contributing infrastructure, deployment, or runtime code, run a local secret scan such as:

```sh
gitleaks detect --source .
```

If `gitleaks` is unavailable, use an equivalent scanner such as TruffleHog before opening a pull request.
