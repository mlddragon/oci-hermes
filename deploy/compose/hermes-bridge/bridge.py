import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


AUDIT_DIR = Path("/var/log/hermes-audit")


def audit(event: str, detail: str) -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "detail": detail,
    }
    with (AUDIT_DIR / "bridge-events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def main() -> int:
    if os.environ.get("HERMES_BRIDGE_E2EE_CONFIRMED") != "true":
        message = (
            "Hermes Matrix bridge refused to start: no reviewed E2EE-capable "
            "Matrix SDK implementation is enabled. This prevents accidental "
            "plaintext bot deployment."
        )
        audit("bridge_blocked", message)
        print(message, file=sys.stderr)
        return 78

    message = (
        "Hermes bridge E2EE implementation is not included in this scaffold. "
        "Add a reviewed Matrix SDK bridge before enabling this service."
    )
    audit("bridge_not_implemented", message)
    print(message, file=sys.stderr)
    return 78


if __name__ == "__main__":
    raise SystemExit(main())
