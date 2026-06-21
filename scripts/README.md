# Scripts

Operational helper scripts will live here.

Scripts should be safe by default:

- No embedded secrets.
- No deployer-specific account IDs.
- Clear dry-run behavior for cloud mutations where practical.
- Explicit failure handling for backup, restore, update, and DNS workflows.
