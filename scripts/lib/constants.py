from pathlib import Path

DEFAULT_REGION = "us-chicago-1"
DEFAULT_COMPARTMENT = "hermes-free"
DEFAULT_SHAPE = "VM.Standard.A1.Flex"
DEFAULT_OCPUS = 4
DEFAULT_MEMORY_GB = 24
DEFAULT_BOOT_VOLUME_GB = 150
DEFAULT_SSH_PUBLIC_KEY = "~/.ssh/hermes_oci_ed25519.pub"
DEFAULT_MATRIX_SERVER = "continuwuity"
DEFAULT_MATRIX_IMAGE = "ghcr.io/girlbossceo/conduwuit:latest"
DEFAULT_MODEL = "hf.co/NousResearch/Hermes-3-Llama-3.1-8B-GGUF:Q4_K_M"

MATRIX_USERS = ["admin", "primary", "secondary", "hermes", "ops"]
MATRIX_ROOMS = [
    "Primary AI",
    "Secondary AI",
    "Shared AI",
    "Ops/Admin",
    "Recovery/Test",
]

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DIR = REPO_ROOT / ".hermes"
CONFIG_FILE = LOCAL_DIR / "config.json"
RENDER_DIR = LOCAL_DIR / "rendered"
