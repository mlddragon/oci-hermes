# systemd

Host service and timer unit templates will live here.

Rules for this directory:

- Prefer explicit environment file paths outside git.
- Use least-privilege service users where practical.
- Document restart, backup, and health-check behavior in runbooks.
- Review every unit before installing it on a live host.
