# Caddy

Caddy templates for public HTTPS Matrix client access will live here.

Rules for this directory:

- Proxy only reviewed public endpoints.
- Keep federation disabled for v1 unless a reviewed design changes that.
- Do not commit real hostnames unless they are neutral examples.
- Render deployer-owned values with `scripts/hermesctl render`; generated files belong under `.hermes/`.
