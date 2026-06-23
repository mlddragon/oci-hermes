import re
from collections.abc import Mapping

SECRET_KEY_RE = re.compile(r"(token|secret|password|passphrase|api[_-]?key|private[_-]?key)", re.I)
OCID_RE = re.compile(r"ocid1\.[A-Za-z0-9._-]+")
PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.S,
)
IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
OPENAI_KEY_RE = re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b")
DUCKDNS_TOKEN_RE = re.compile(r"\b[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b", re.I)


def redact_text(value: str) -> str:
    text = str(value)
    text = PRIVATE_KEY_RE.sub("[REDACTED_PRIVATE_KEY]", text)
    text = OPENAI_KEY_RE.sub("[REDACTED_OPENAI_KEY]", text)
    text = OCID_RE.sub("[REDACTED_OCID]", text)
    text = DUCKDNS_TOKEN_RE.sub("[REDACTED_TOKEN]", text)
    text = IPV4_RE.sub("[REDACTED_IP]", text)
    return text


def redact_mapping(mapping: Mapping[str, object]) -> dict[str, object]:
    redacted: dict[str, object] = {}
    for key, value in mapping.items():
        if SECRET_KEY_RE.search(key):
            redacted[key] = "[REDACTED]"
        elif isinstance(value, Mapping):
            redacted[key] = redact_mapping(value)
        elif isinstance(value, list):
            redacted[key] = [redact_text(item) for item in value]
        else:
            redacted[key] = redact_text(value)
    return redacted
