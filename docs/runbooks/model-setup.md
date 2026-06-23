# Local Model Setup Runbook

The v1 runtime uses Ollama and a local Hermes 3 Llama 3.1 8B quantized model by
default. The model license and download terms are separate from this repo.

## Steps

1. Confirm the VM has enough free disk and memory.
2. Review the model terms from the model publisher.
3. Run `scripts/hermesctl pull-model --host "$HERMES_HOST"`.
4. Type `I ACCEPT HERMES MODEL TERMS` only after accepting the model terms.
5. Run a local inference check on the VM.
6. Record rough latency, tokens per second, memory pressure, and swap use.

## Stop Conditions

- The model terms are unacceptable.
- The model cannot fit in available disk or memory.
- The runtime binds Ollama to a public interface.
- Performance is too slow for private chat continuity.
