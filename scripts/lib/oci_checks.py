import json
import shutil
from pathlib import Path

from .runner import run


def tool_status(names: list[str]) -> dict[str, str]:
    return {name: shutil.which(name) or "" for name in names}


def oci_auth_summary() -> dict[str, object]:
    if not shutil.which("oci"):
        return {"available": False, "error": "oci CLI not found"}
    result = run(
        ["oci", "iam", "region-subscription", "list", "--output", "json"],
        check=False,
        quiet=True,
    )
    if result.returncode != 0:
        return {"available": True, "authenticated": False}
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"available": True, "authenticated": False, "error": "invalid JSON from OCI CLI"}
    return {"available": True, "authenticated": True, "regions": data.get("data", [])}


def public_key_exists(path: str) -> bool:
    return Path(path).expanduser().exists()


def resolve_compartment_ocid(compartment: str) -> str:
    if compartment.startswith("ocid1.compartment."):
        return compartment
    if not shutil.which("oci"):
        raise RuntimeError("OCI CLI is required to resolve compartment names to OCIDs.")
    result = run(
        [
            "oci",
            "iam",
            "compartment",
            "list",
            "--all",
            "--compartment-id-in-subtree",
            "true",
            "--name",
            compartment,
            "--output",
            "json",
        ],
        check=True,
        quiet=True,
    )
    data = json.loads(result.stdout)
    matches = [item for item in data.get("data", []) if item.get("name") == compartment and item.get("lifecycle-state") == "ACTIVE"]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one ACTIVE compartment named {compartment}, found {len(matches)}.")
    return matches[0]["id"]
