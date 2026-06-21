# Provider Boundaries

OCI Hermes must remain account-neutral.

## Required Boundary

Each deployer provides and controls their own:

- Cloud provider tenancy, account, subscription, or project.
- DNS account and hostname.
- Backup storage.
- Model-provider account and API keys when external inference is enabled.
- Matrix homeserver data, user accounts, recovery keys, and bot session store.
- Terraform state and state encryption material.

## Repository Rules

- Do not hard-code maintainer or contributor provider identifiers.
- Do not commit state, secrets, generated keys, account-specific hostnames, private endpoints, or service data.
- Do not assume access to a shared backend, shared storage bucket, shared DNS token, shared OpenAI project, or shared Matrix homeserver.
- Do not include screenshots or logs that expose private provider metadata.

## Template Rules

Templates should use clear placeholders such as:

- `REPLACE_WITH_YOUR_OCI_TENANCY_OCID`
- `REPLACE_WITH_YOUR_DUCKDNS_HOSTNAME`
- `REPLACE_WITH_YOUR_RESTIC_REPOSITORY`
- `REPLACE_WITH_YOUR_OPENAI_PROJECT_KEY_PATH`

The deployer must replace placeholders locally and keep those local values out of git.
