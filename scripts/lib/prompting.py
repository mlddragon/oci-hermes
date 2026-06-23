import getpass
from collections.abc import Callable


def ask(prompt: str, default: str = "", input_fn: Callable[[str], str] = input) -> str:
    suffix = f" [{default}]" if default else ""
    value = input_fn(f"{prompt}{suffix}: ").strip()
    return value or default


def ask_bool(prompt: str, default: bool = False, input_fn: Callable[[str], str] = input) -> bool:
    default_text = "y" if default else "n"
    value = ask(f"{prompt} (y/n)", default_text, input_fn).lower()
    return value in {"y", "yes", "true", "1"}


def ask_secret(prompt: str) -> str:
    return getpass.getpass(f"{prompt}: ")


def require_phrase(expected: str, prompt: str = "Type confirmation phrase") -> None:
    value = input(f"{prompt} ({expected}): ").strip()
    if value != expected:
        raise SystemExit("Confirmation phrase did not match; no action taken.")
