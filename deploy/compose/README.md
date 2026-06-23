# Compose Deployment

Docker Compose definitions for the private Hermes, Matrix, and local model runtime will live here.

Rules for this directory:

- Use explicit bind mounts, not anonymous volumes.
- Do not publish Ollama, llama.cpp, Hermes agent APIs, Docker internals, or backend services to public interfaces.
- Keep runtime secrets in deployer-owned root-only files outside git.
- Keep the `hermes-bridge` profile disabled until Matrix accounts, encrypted rooms, trusted inviters, and Element bot-device verification are complete.
- Keep `ai_private` internal; the bridge may talk to Ollama, but Ollama must not be public.
