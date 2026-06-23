import ipaddress
import re
from pathlib import Path

from .constants import MATRIX_USERS

BANNED_DUCKDNS_TERMS = {"matrix", "hermes", "ai", "chat", "server", "cloud"}
REGION_RE = re.compile(r"^[a-z]+-[a-z]+-\d+$")
COMPARTMENT_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{1,62}$")
DUCKDNS_LABEL_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])?$")
SECRET_VALUE_RE = re.compile(r"(-----BEGIN .*PRIVATE KEY-----|sk-[A-Za-z0-9_-]{12,})", re.S)


class ConfigError(ValueError):
    pass


def normalize_duckdns_label(hostname: str) -> str:
    host = hostname.strip().lower()
    if host.endswith(".duckdns.org"):
        host = host[: -len(".duckdns.org")]
    return host


def validate_duckdns_hostname(hostname: str) -> str:
    label = normalize_duckdns_label(hostname)
    if label.startswith("replace_with"):
        raise ConfigError("DuckDNS hostname must be deployer-owned, not a placeholder.")
    if not DUCKDNS_LABEL_RE.match(label):
        raise ConfigError("DuckDNS hostname must be a DNS-safe label under duckdns.org.")
    if any(term in label for term in BANNED_DUCKDNS_TERMS):
        raise ConfigError("DuckDNS hostname must not reveal matrix, hermes, ai, chat, server, or cloud.")
    return f"{label}.duckdns.org"


def validate_region(region: str) -> str:
    value = region.strip()
    if not REGION_RE.match(value):
        raise ConfigError("OCI region must look like us-chicago-1.")
    return value


def validate_compartment(value: str) -> str:
    cleaned = value.strip()
    if cleaned.startswith("ocid1.compartment."):
        return cleaned
    if not COMPARTMENT_NAME_RE.match(cleaned):
        raise ConfigError("Compartment must be an OCI compartment OCID or a simple compartment name.")
    return cleaned


def validate_ssh_cidr(cidr: str, allow_world_ssh: bool = False) -> str:
    network = ipaddress.ip_network(cidr.strip(), strict=False)
    if network.version != 4:
        raise ConfigError("SSH CIDR must be IPv4 for v1.")
    if network.prefixlen == 0 and not allow_world_ssh:
        raise ConfigError("World-open SSH is blocked unless allow_world_ssh is explicitly true.")
    if network.prefixlen < 24 and not allow_world_ssh:
        raise ConfigError("SSH CIDR must be narrow, preferably the detected current /32.")
    return str(network)


def validate_public_key_path(path: str) -> str:
    expanded = Path(path).expanduser()
    if expanded.name.startswith("id_rsa") or expanded.name == "id_ed25519.pub":
        raise ConfigError("Use a dedicated Hermes OCI SSH key, not a broad default SSH key.")
    return str(expanded)


def validate_matrix_users(users: list[str]) -> list[str]:
    if users != MATRIX_USERS:
        raise ConfigError(f"Matrix users must remain the approved generic set: {', '.join(MATRIX_USERS)}.")
    return users


def reject_secret_material(value: object, path: str = "config") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            lowered = key.lower()
            if any(term in lowered for term in ("token", "secret", "password", "passphrase", "api_key", "apikey")):
                raise ConfigError(f"{path}.{key} looks like a secret field and must not be persisted.")
            reject_secret_material(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            reject_secret_material(item, f"{path}[{index}]")
    elif isinstance(value, str) and SECRET_VALUE_RE.search(value):
        raise ConfigError(f"{path} contains secret-like material and must not be persisted.")
