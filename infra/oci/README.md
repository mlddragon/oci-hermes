# OCI Infrastructure

OpenTofu-compatible OCI infrastructure lives here. Use `scripts/hermesctl render`
to generate ignored local variables under `.hermes/rendered/`, then use
`scripts/hermesctl plan` to review the deployment before any apply.

This configuration intentionally does not reserve a public IPv4 address by
default. It provisions one A1 Flex VM with SSH restricted to the configured
CIDR and HTTP/HTTPS for Caddy.

Never commit generated state, plans, `.tfvars`, public IPs, OCIDs, or hostnames.

Rules for this directory:

- Keep HCL deployer-owned and placeholder-based.
- Do not commit Terraform state, plans, `.terraform/`, `.tfvars`, or account-specific OCIDs.
- Keep all resources Always Free-safe unless a reviewed design explicitly changes the target.
- Document any resource that can create cost.
