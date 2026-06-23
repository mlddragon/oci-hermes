# Scripts

Operational helper scripts will live here.

Scripts should be safe by default:

- No embedded secrets.
- No deployer-specific account IDs.
- Clear dry-run behavior for cloud mutations where practical.
- Explicit failure handling for backup, restore, update, and DNS workflows.

Use `scripts/hermesctl` as the deployer-facing CLI.

Safe starting sequence:

```bash
scripts/hermesctl doctor
scripts/hermesctl init
scripts/hermesctl secrets-check
scripts/hermesctl render
scripts/hermesctl plan
```

Commands after `plan` may mutate cloud or host state and require typed
confirmation phrases.
