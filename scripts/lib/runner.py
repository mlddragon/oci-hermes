import subprocess
from pathlib import Path

from .redaction import redact_text


class CommandError(RuntimeError):
    pass


def run(
    command: list[str],
    cwd: Path | None = None,
    check: bool = True,
    input_text: str | None = None,
    quiet: bool = False,
) -> subprocess.CompletedProcess[str]:
    display = " ".join(command)
    print(f"+ {redact_text(display)}")
    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        input=input_text,
    )
    if result.stdout and not quiet:
        print(redact_text(result.stdout), end="")
    if result.stderr and not quiet:
        print(redact_text(result.stderr), end="")
    if check and result.returncode != 0:
        raise CommandError(f"Command failed with exit {result.returncode}: {redact_text(display)}")
    return result
