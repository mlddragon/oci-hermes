#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import sys
from dataclasses import asdict
from pathlib import Path

from lib.config import HermesConfig, config_exists, load_config, save_config
from lib.constants import CONFIG_FILE, LOCAL_DIR, RENDER_DIR, REPO_ROOT
from lib.oci_checks import oci_auth_summary, public_key_exists, tool_status
from lib.prompting import ask, ask_bool, ask_secret, require_phrase
from lib.redaction import redact_mapping, redact_text
from lib.runner import run
from lib.templates import render_all
from lib.validation import ConfigError


def print_json(data: object) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def tofu_binary() -> str:
    return shutil.which("tofu") or shutil.which("terraform") or "tofu"


def load_or_exit() -> HermesConfig:
    try:
        return load_config()
    except ConfigError as exc:
        raise SystemExit(str(exc)) from exc


def cmd_doctor(_: argparse.Namespace) -> None:
    tools = tool_status(["python3", "oci", "tofu", "terraform", "ssh", "scp", "jq", "ssh-keygen"])
    config_state = {"exists": config_exists(), "path": str(CONFIG_FILE)}
    summary: dict[str, object] = {
        "repo_root": str(REPO_ROOT),
        "local_dir": str(LOCAL_DIR),
        "tools": tools,
        "config": config_state,
    }
    if config_exists():
        config = load_or_exit()
        summary["config_preview"] = redact_mapping(asdict(config))
        summary["ssh_public_key_exists"] = public_key_exists(config.ssh_public_key_path)
    summary["oci"] = oci_auth_summary()
    print_json(summary)
    missing = [name for name, path in tools.items() if name in {"oci", "ssh", "scp"} and not path]
    if not tools.get("tofu") and not tools.get("terraform"):
        missing.append("tofu or terraform")
    if missing:
        raise SystemExit(f"Missing required local tools: {', '.join(missing)}")


def cmd_init(args: argparse.Namespace) -> None:
    if args.non_interactive:
        config = HermesConfig()
    else:
        current = load_config() if config_exists() else HermesConfig()
        config = HermesConfig(
            region=ask("OCI region", current.region),
            compartment=ask("OCI compartment name or OCID", current.compartment),
            ssh_public_key_path=ask("Dedicated Hermes SSH public key path", current.ssh_public_key_path),
            ssh_allowed_cidr=ask("SSH allowed CIDR", current.ssh_allowed_cidr),
            allow_world_ssh=ask_bool("Allow broad SSH CIDR", current.allow_world_ssh),
            duckdns_hostname=ask("DuckDNS hostname", current.duckdns_hostname),
            availability_domain=ask("Availability domain, blank for Terraform data source default", current.availability_domain),
            openai_enabled=ask_bool("Enable OpenAI routing scaffold", current.openai_enabled),
            ntfy_enabled=ask_bool("Enable ntfy fallback scaffold", current.ntfy_enabled),
        )
    save_config(config)
    print(f"Wrote non-secret config to {CONFIG_FILE}")


def cmd_secrets_check(_: argparse.Namespace) -> None:
    required = [
        "DuckDNS token",
        "Matrix admin, primary, secondary, hermes, and ops passwords",
        "Hermes Matrix bot password for the bridge secret file",
        "Matrix recovery keys/passphrases stored off-VM",
        "Restic passphrase",
    ]
    optional = ["OpenAI API key for approval-gated routing", "ntfy topic for nonsensitive fallback alerts"]
    print("Required secrets to keep outside git:")
    for item in required:
        print(f"- {item}")
    print("Optional secrets:")
    for item in optional:
        print(f"- {item}")
    print("hermesctl prompts for runtime secrets just in time and does not persist them locally by default.")


def cmd_render(_: argparse.Namespace) -> None:
    config = load_or_exit()
    rendered = render_all(config)
    print("Rendered local artifacts:")
    for path in rendered:
        print(f"- {path}")
    print("These files live under .hermes/ and must remain untracked.")


def require_rendered_tfvars() -> Path:
    tfvars = RENDER_DIR / "terraform.tfvars.json"
    if not tfvars.exists():
        raise SystemExit("Missing rendered Terraform variables. Run scripts/hermesctl render first.")
    return tfvars


def cmd_plan(_: argparse.Namespace) -> None:
    tfvars = require_rendered_tfvars()
    tofu = tofu_binary()
    infra_dir = REPO_ROOT / "infra/oci"
    run([tofu, "fmt", "-check"], cwd=infra_dir)
    run([tofu, "init"], cwd=infra_dir)
    run([tofu, "validate"], cwd=infra_dir)
    run([tofu, "plan", f"-var-file={tfvars}"], cwd=infra_dir)


def cmd_apply(_: argparse.Namespace) -> None:
    tfvars = require_rendered_tfvars()
    require_phrase("APPLY OCI HERMES", "Cloud resources will be created or changed")
    run([tofu_binary(), "apply", f"-var-file={tfvars}"], cwd=REPO_ROOT / "infra/oci")


def require_remote_host(args: argparse.Namespace) -> str:
    host = args.host or os.environ.get("HERMES_HOST")
    if not host:
        raise SystemExit("Provide --host or HERMES_HOST. Do not commit hostnames or IPs.")
    return host


def cmd_bootstrap_host(args: argparse.Namespace) -> None:
    host = require_remote_host(args)
    bootstrap = RENDER_DIR / "bootstrap-host.sh"
    if not bootstrap.exists():
        raise SystemExit("Missing rendered bootstrap script. Run scripts/hermesctl render first.")
    print(f"Target host: {redact_text(host)}")
    require_phrase("BOOTSTRAP HERMES HOST", "Host packages, firewall, and service directories will be changed")
    run(["scp", str(bootstrap), f"ubuntu@{host}:/tmp/hermes-bootstrap-host.sh"])
    run(["ssh", f"ubuntu@{host}", "sudo bash /tmp/hermes-bootstrap-host.sh"])


def install_secret_file(host: str, name: str, content: str) -> None:
    if not content:
        return
    remote = f"sudo install -d -m 700 /opt/hermes-ai/secrets && sudo tee /opt/hermes-ai/secrets/{name} >/dev/null && sudo chmod 600 /opt/hermes-ai/secrets/{name}"
    run(["ssh", f"ubuntu@{host}", remote], check=True, input_text=content)


def cmd_deploy_runtime(args: argparse.Namespace) -> None:
    host = require_remote_host(args)
    require_phrase("DEPLOY HERMES RUNTIME", "Runtime files and root-owned service secrets will be installed")
    config = load_or_exit()
    duckdns_token = os.environ.get("HERMES_DUCKDNS_TOKEN") or ask_secret("DuckDNS token")
    restic_repository = os.environ.get("HERMES_RESTIC_REPOSITORY") or ask("Restic repository URL, for example oci:bucket:path")
    restic_passphrase = os.environ.get("HERMES_RESTIC_PASSPHRASE") or ask_secret("Restic passphrase")
    matrix_hermes_password = os.environ.get("HERMES_MATRIX_PASSWORD") or ask_secret("Hermes Matrix bot password")
    openai_key = ""
    if config.openai_enabled:
        openai_key = os.environ.get("OPENAI_API_KEY") or ask_secret("OpenAI API key")
    for source in [RENDER_DIR / "caddy/Caddyfile", RENDER_DIR / "compose/hermes.env"]:
        if not source.exists():
            raise SystemExit(f"Missing rendered file: {source}. Run scripts/hermesctl render first.")
    run(["ssh", f"ubuntu@{host}", "sudo rm -rf /tmp/hermes-bridge-src && sudo install -d -m 755 /opt/hermes-ai/deploy/caddy /opt/hermes-ai/deploy/compose /opt/hermes-ai/deploy/compose/hermes-bridge"])
    run(["scp", str(RENDER_DIR / "caddy/Caddyfile"), f"ubuntu@{host}:/tmp/hermes-Caddyfile"])
    run(["scp", str(RENDER_DIR / "compose/hermes.env"), f"ubuntu@{host}:/tmp/hermes.env"])
    run(["scp", str(REPO_ROOT / "deploy/compose/docker-compose.yml"), f"ubuntu@{host}:/tmp/hermes-docker-compose.yml"])
    run(["scp", str(REPO_ROOT / "deploy/compose/hermes-bridge/Dockerfile"), f"ubuntu@{host}:/tmp/hermes-bridge-Dockerfile"])
    run(["scp", str(REPO_ROOT / "deploy/compose/hermes-bridge/Cargo.toml"), f"ubuntu@{host}:/tmp/hermes-bridge-Cargo.toml"])
    run(["scp", str(REPO_ROOT / "deploy/compose/hermes-bridge/Cargo.lock"), f"ubuntu@{host}:/tmp/hermes-bridge-Cargo.lock"])
    run(["scp", "-r", str(REPO_ROOT / "deploy/compose/hermes-bridge/src"), f"ubuntu@{host}:/tmp/hermes-bridge-src"])
    run(["scp", str(REPO_ROOT / "deploy/systemd/hermes-compose.service"), f"ubuntu@{host}:/tmp/hermes-compose.service"])
    run(["scp", str(REPO_ROOT / "deploy/systemd/hermes-backup.service"), f"ubuntu@{host}:/tmp/hermes-backup.service"])
    run(["scp", str(REPO_ROOT / "deploy/systemd/hermes-backup.timer"), f"ubuntu@{host}:/tmp/hermes-backup.timer"])
    run(["scp", str(REPO_ROOT / "deploy/systemd/hermes-restore-test.service"), f"ubuntu@{host}:/tmp/hermes-restore-test.service"])
    run(["scp", str(REPO_ROOT / "deploy/systemd/hermes-duckdns.service"), f"ubuntu@{host}:/tmp/hermes-duckdns.service"])
    run(["scp", str(REPO_ROOT / "deploy/systemd/hermes-duckdns.timer"), f"ubuntu@{host}:/tmp/hermes-duckdns.timer"])
    run(["ssh", f"ubuntu@{host}", "sudo install -m 644 /tmp/hermes-Caddyfile /opt/hermes-ai/deploy/caddy/Caddyfile && sudo install -m 644 /tmp/hermes-Caddyfile /etc/caddy/Caddyfile && sudo install -m 600 /tmp/hermes.env /opt/hermes-ai/deploy/compose/hermes.env"])
    run(["ssh", f"ubuntu@{host}", "sudo install -m 644 /tmp/hermes-docker-compose.yml /opt/hermes-ai/deploy/compose/docker-compose.yml && sudo install -m 644 /tmp/hermes-bridge-Dockerfile /opt/hermes-ai/deploy/compose/hermes-bridge/Dockerfile && sudo install -m 644 /tmp/hermes-bridge-Cargo.toml /opt/hermes-ai/deploy/compose/hermes-bridge/Cargo.toml && sudo install -m 644 /tmp/hermes-bridge-Cargo.lock /opt/hermes-ai/deploy/compose/hermes-bridge/Cargo.lock && sudo rm -rf /opt/hermes-ai/deploy/compose/hermes-bridge/src && sudo cp -R /tmp/hermes-bridge-src /opt/hermes-ai/deploy/compose/hermes-bridge/src && sudo chown -R root:root /opt/hermes-ai/deploy/compose/hermes-bridge/src && sudo find /opt/hermes-ai/deploy/compose/hermes-bridge/src -type d -exec chmod 755 {} + && sudo find /opt/hermes-ai/deploy/compose/hermes-bridge/src -type f -exec chmod 644 {} +"])
    run(["ssh", f"ubuntu@{host}", "sudo install -m 644 /tmp/hermes-compose.service /etc/systemd/system/hermes-compose.service && sudo install -m 644 /tmp/hermes-backup.service /etc/systemd/system/hermes-backup.service && sudo install -m 644 /tmp/hermes-backup.timer /etc/systemd/system/hermes-backup.timer && sudo install -m 644 /tmp/hermes-restore-test.service /etc/systemd/system/hermes-restore-test.service && sudo install -m 644 /tmp/hermes-duckdns.service /etc/systemd/system/hermes-duckdns.service && sudo install -m 644 /tmp/hermes-duckdns.timer /etc/systemd/system/hermes-duckdns.timer && sudo systemctl daemon-reload && sudo systemctl reload caddy"])
    install_secret_file(host, "duckdns.env", f"DUCKDNS_DOMAIN={config.duckdns_hostname.removesuffix('.duckdns.org')}\nDUCKDNS_TOKEN={duckdns_token}\n")
    install_secret_file(host, "restic.env", f"RESTIC_REPOSITORY={restic_repository}\nRESTIC_PASSWORD={restic_passphrase}\n")
    install_secret_file(host, "matrix-hermes-password", f"{matrix_hermes_password}\n")
    if openai_key:
        install_secret_file(host, "openai.env", f"OPENAI_API_KEY={openai_key}\n")
    print("Runtime files copied. Start services with the runbook after reviewing rendered Compose files.")


def cmd_setup_matrix(_: argparse.Namespace) -> None:
    print("Matrix setup is intentionally human-confirmed in v1.")
    print("Create users: admin, primary, secondary, hermes, ops.")
    print("Close registration, enable E2EE, verify primary/secondary recovery, then verify the Hermes bot device.")
    print("Use docs/runbooks/matrix-e2ee.md for the exact checklist.")


def cmd_pull_model(args: argparse.Namespace) -> None:
    host = require_remote_host(args)
    require_phrase("I ACCEPT HERMES MODEL TERMS", "Model license terms must be accepted before download")
    model = load_or_exit().model
    run(["ssh", f"ubuntu@{host}", f"sudo docker exec hermes-ollama ollama pull {model}"])


def cmd_verify(args: argparse.Namespace) -> None:
    host = require_remote_host(args)
    config = load_or_exit()
    checks = [
        ["ssh", f"ubuntu@{host}", "systemctl is-active caddy || true"],
        ["ssh", f"ubuntu@{host}", "sudo ufw status verbose || true"],
        ["ssh", f"ubuntu@{host}", "sudo test -f /opt/hermes-ai/secrets/matrix-hermes-password && sudo stat -c '%U %a %n' /opt/hermes-ai/secrets/matrix-hermes-password || true"],
        ["ssh", f"ubuntu@{host}", "cd /opt/hermes-ai/deploy/compose && sudo docker compose --env-file hermes.env --profile bridge config >/dev/null && echo compose-config-ok || true"],
        ["ssh", f"ubuntu@{host}", "sudo docker ps --format '{{.Names}} {{.Ports}}' || true"],
        ["ssh", f"ubuntu@{host}", "sudo docker ps --filter name=hermes-bridge --format '{{.Names}} {{.Status}}' || true"],
        ["ssh", f"ubuntu@{host}", "sudo test -f /opt/hermes-ai/data/audit/bridge-events.jsonl && echo bridge-audit-log-present || true"],
        ["curl", "-fsS", f"https://{config.duckdns_hostname}/_matrix/client/versions"],
    ]
    for check in checks:
        run(check, check=False)


def cmd_backup_test(args: argparse.Namespace) -> None:
    host = require_remote_host(args)
    require_phrase("RUN RESTIC BACKUP TEST", "A backup and restore-test workflow will run on the host")
    run(["ssh", f"ubuntu@{host}", "sudo systemctl start hermes-backup.service && sudo systemctl start hermes-restore-test.service"])


def cmd_status(args: argparse.Namespace) -> None:
    status: dict[str, object] = {"config_exists": config_exists(), "render_dir": str(RENDER_DIR)}
    if config_exists():
        status["config"] = redact_mapping(asdict(load_or_exit()))
    if args.host or os.environ.get("HERMES_HOST"):
        host = require_remote_host(args)
        result = run(["ssh", f"ubuntu@{host}", "hostname && uptime"], check=False)
        status["host_check_exit"] = result.returncode
    print_json(status)


def cmd_teardown_plan(_: argparse.Namespace) -> None:
    print("Teardown checklist:")
    print("1. Run and verify a final Restic backup.")
    print("2. Export any required local encrypted recovery bundle.")
    print("3. Confirm Matrix recovery keys and Restic passphrase are stored off-VM.")
    print("4. Run `tofu plan -destroy` manually and review every resource.")
    print("5. Only after review, run a separate destroy command outside hermesctl.")
    print("hermesctl does not implement automatic destroy in v1.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deploy and operate OCI Hermes safely.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor").set_defaults(func=cmd_doctor)
    init = sub.add_parser("init")
    init.add_argument("--non-interactive", action="store_true")
    init.set_defaults(func=cmd_init)
    sub.add_parser("secrets-check").set_defaults(func=cmd_secrets_check)
    sub.add_parser("render").set_defaults(func=cmd_render)
    sub.add_parser("plan").set_defaults(func=cmd_plan)
    sub.add_parser("apply").set_defaults(func=cmd_apply)

    for name, func in {
        "bootstrap-host": cmd_bootstrap_host,
        "deploy-runtime": cmd_deploy_runtime,
        "pull-model": cmd_pull_model,
        "verify": cmd_verify,
        "backup-test": cmd_backup_test,
        "status": cmd_status,
    }.items():
        command = sub.add_parser(name)
        command.add_argument("--host", help="Deployment host DNS name or IP. Prefer HERMES_HOST for local use.")
        command.set_defaults(func=func)

    sub.add_parser("setup-matrix").set_defaults(func=cmd_setup_matrix)
    sub.add_parser("teardown-plan").set_defaults(func=cmd_teardown_plan)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
