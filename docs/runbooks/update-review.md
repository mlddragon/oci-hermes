# Update Review Runbook

During bootstrap, app, container, model, and host feature updates are manual.
Security updates may run through unattended Ubuntu upgrades after host bootstrap.

## Review Steps

1. Run a backup before nontrivial updates.
2. Confirm the latest restore test status.
3. Review release notes for Matrix, Caddy, Ollama, and Hermes bridge components.
4. Confirm no update changes public exposure or registration/federation posture.
5. Apply one category of update at a time.
6. Run `scripts/hermesctl verify --host "$HERMES_HOST"` after each update.

## Stop Conditions

- Restore test is stale or failed.
- Update requires paid OCI resources.
- Update changes model behavior without explicit review.
- Update adds a public backend port.
