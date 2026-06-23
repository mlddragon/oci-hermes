from pathlib import Path

from .config import HermesConfig
from .constants import RENDER_DIR, REPO_ROOT
from .oci_checks import resolve_compartment_ocid


def render_text(template: str, values: dict[str, object]) -> str:
    output = template
    for key, value in values.items():
        output = output.replace("{{" + key + "}}", str(value))
    if "{{" in output or "}}" in output:
        raise ValueError("Rendered template still contains unresolved placeholders.")
    return output


def template_values(config: HermesConfig, compartment_ocid: str | None = None) -> dict[str, object]:
    resolved_compartment = compartment_ocid or resolve_compartment_ocid(config.compartment)
    return {
        "REGION": config.region,
        "COMPARTMENT": resolved_compartment,
        "SSH_PUBLIC_KEY_PATH": config.ssh_public_key_path,
        "SSH_ALLOWED_CIDR": config.ssh_allowed_cidr,
        "DUCKDNS_HOSTNAME": config.duckdns_hostname,
        "AVAILABILITY_DOMAIN": config.availability_domain,
        "SHAPE": config.shape,
        "OCPUS": config.ocpus,
        "MEMORY_GB": config.memory_gb,
        "BOOT_VOLUME_GB": config.boot_volume_gb,
        "MATRIX_SERVER": config.matrix_server,
        "MATRIX_IMAGE": config.matrix_image,
        "MODEL": config.model,
        "OPENAI_ENABLED": str(config.openai_enabled).lower(),
        "NTFY_ENABLED": str(config.ntfy_enabled).lower(),
    }


def render_file(source: Path, destination: Path, values: dict[str, object], mode: int | None = None) -> None:
    text = source.read_text(encoding="utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_text(text, values), encoding="utf-8")
    if mode is not None:
        destination.chmod(mode)


def render_all(config: HermesConfig, output_dir: Path = RENDER_DIR) -> list[Path]:
    values = template_values(config)
    rendered: list[Path] = []
    specs = [
        (REPO_ROOT / "infra/oci/templates/terraform.tfvars.json.tmpl", output_dir / "terraform.tfvars.json", None),
        (REPO_ROOT / "deploy/caddy/templates/Caddyfile.tmpl", output_dir / "caddy/Caddyfile", None),
        (REPO_ROOT / "deploy/compose/config/hermes.env.tmpl", output_dir / "compose/hermes.env", 0o600),
        (REPO_ROOT / "deploy/systemd/templates/bootstrap-host.sh.tmpl", output_dir / "bootstrap-host.sh", 0o700),
    ]
    for source, destination, mode in specs:
        render_file(source, destination, values, mode)
        rendered.append(destination)
    return rendered
