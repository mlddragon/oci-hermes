# OCI Infrastructure

Terraform-compatible OCI infrastructure will live here.

Rules for this directory:

- Keep HCL deployer-owned and placeholder-based.
- Do not commit Terraform state, plans, `.terraform/`, `.tfvars`, or account-specific OCIDs.
- Keep all resources Always Free-safe unless a reviewed design explicitly changes the target.
- Document any resource that can create cost.
