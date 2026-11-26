# Local Model Setup Runbook

The v1 runtime uses Ollama and a local Qwen3 4B GGUF `Q4_K_M` model by default
(`hf.co/Qwen/Qwen3-4B-GGUF:Q4_K_M`). That size fits Always Free A1 at 2 OCPU and
12 GB RAM with Matrix and Caddy still running. The model license is Apache 2.0
and is separate from this repo.

## Steps

1. Confirm the VM has enough free disk and memory for a ~2.5 GB download plus
   runtime headroom. Leave swap unused if possible.
2. Review the [Qwen3 4B terms](https://huggingface.co/Qwen/Qwen3-4B-GGUF) (Apache 2.0).
3. Run `scripts/hermesctl pull-model --host "$HERMES_HOST"`.
4. Type `I ACCEPT QWEN MODEL TERMS` only after accepting the model terms.
5. Run a local inference check on the VM with a short context (4k–8k).
6. Record rough latency, tokens per second, memory pressure, and swap use.

## Stop Conditions

- The model terms are unacceptable.
- The model cannot fit in available disk or memory.
- The runtime binds Ollama to a public interface.
- Performance is too slow for private chat continuity.
- Resident model plus homeserver memory approaches 12 GB or swap is in use.
