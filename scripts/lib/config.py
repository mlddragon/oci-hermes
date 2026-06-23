import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .constants import (
    CONFIG_FILE,
    DEFAULT_BOOT_VOLUME_GB,
    DEFAULT_COMPARTMENT,
    DEFAULT_MATRIX_IMAGE,
    DEFAULT_MATRIX_SERVER,
    DEFAULT_MEMORY_GB,
    DEFAULT_MODEL,
    DEFAULT_OCPUS,
    DEFAULT_REGION,
    DEFAULT_SHAPE,
    DEFAULT_SSH_PUBLIC_KEY,
    MATRIX_ROOMS,
    MATRIX_USERS,
)
from .validation import (
    ConfigError,
    reject_secret_material,
    validate_compartment,
    validate_duckdns_hostname,
    validate_matrix_users,
    validate_public_key_path,
    validate_region,
    validate_ssh_cidr,
)


@dataclass
class HermesConfig:
    region: str = DEFAULT_REGION
    compartment: str = DEFAULT_COMPARTMENT
    ssh_public_key_path: str = DEFAULT_SSH_PUBLIC_KEY
    ssh_allowed_cidr: str = "203.0.113.10/32"
    allow_world_ssh: bool = False
    duckdns_hostname: str = "private-neutral-name.duckdns.org"
    availability_domain: str = ""
    shape: str = DEFAULT_SHAPE
    ocpus: int = DEFAULT_OCPUS
    memory_gb: int = DEFAULT_MEMORY_GB
    boot_volume_gb: int = DEFAULT_BOOT_VOLUME_GB
    matrix_server: str = DEFAULT_MATRIX_SERVER
    matrix_image: str = DEFAULT_MATRIX_IMAGE
    matrix_users: list[str] = field(default_factory=lambda: list(MATRIX_USERS))
    matrix_rooms: list[str] = field(default_factory=lambda: list(MATRIX_ROOMS))
    model: str = DEFAULT_MODEL
    openai_enabled: bool = False
    ntfy_enabled: bool = False

    def validate(self) -> None:
        self.region = validate_region(self.region)
        self.compartment = validate_compartment(self.compartment)
        self.ssh_public_key_path = validate_public_key_path(self.ssh_public_key_path)
        self.ssh_allowed_cidr = validate_ssh_cidr(self.ssh_allowed_cidr, self.allow_world_ssh)
        self.duckdns_hostname = validate_duckdns_hostname(self.duckdns_hostname)
        validate_matrix_users(self.matrix_users)
        if self.matrix_rooms != MATRIX_ROOMS:
            raise ConfigError("Matrix rooms must remain the approved generic room set.")
        if self.shape != DEFAULT_SHAPE:
            raise ConfigError("v1 only supports VM.Standard.A1.Flex.")
        if self.ocpus != DEFAULT_OCPUS or self.memory_gb != DEFAULT_MEMORY_GB:
            raise ConfigError("v1 Always Free target is 4 OCPU and 24 GB RAM.")
        if self.boot_volume_gb < 50 or self.boot_volume_gb > 200:
            raise ConfigError("Boot volume must be between 50 and 200 GB for v1.")
        reject_secret_material(asdict(self))


def config_from_dict(values: dict[str, object]) -> HermesConfig:
    allowed = {field.name for field in HermesConfig.__dataclass_fields__.values()}
    unknown = sorted(set(values) - allowed)
    if unknown:
        raise ConfigError(f"Unknown config keys: {', '.join(unknown)}")
    config = HermesConfig(**values)
    config.validate()
    return config


def load_config(path: Path = CONFIG_FILE) -> HermesConfig:
    if not path.exists():
        raise ConfigError(f"Missing local config: {path}. Run scripts/hermesctl init first.")
    with path.open("r", encoding="utf-8") as handle:
        values = json.load(handle)
    return config_from_dict(values)


def save_config(config: HermesConfig, path: Path = CONFIG_FILE) -> None:
    config.validate()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(asdict(config), handle, indent=2, sort_keys=True)
        handle.write("\n")
    os.chmod(path, 0o600)


def config_exists(path: Path = CONFIG_FILE) -> bool:
    return path.exists()
