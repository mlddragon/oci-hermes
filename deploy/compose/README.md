# Compose Deployment

Docker Compose definitions for the private Hermes, Matrix, and local model runtime will live here.

Rules for this directory:

- Use explicit bind mounts, not anonymous volumes.
- Do not publish Ollama, llama.cpp, Hermes agent APIs, Docker internals, or backend services to public interfaces.
- Keep runtime secrets in deployer-owned root-only files outside git.
