from pathlib import Path

from .runner import run


def ssh_command(host: str, remote_command: str, key_path: str | None = None, user: str = "ubuntu") -> list[str]:
    command = ["ssh"]
    if key_path:
        command.extend(["-i", str(Path(key_path).expanduser())])
    command.extend([f"{user}@{host}", remote_command])
    return command


def scp_command(source: Path, host: str, destination: str, key_path: str | None = None, user: str = "ubuntu") -> list[str]:
    command = ["scp"]
    if key_path:
        command.extend(["-i", str(Path(key_path).expanduser())])
    command.extend([str(source), f"{user}@{host}:{destination}"])
    return command


def run_ssh(host: str, remote_command: str, key_path: str | None = None, user: str = "ubuntu") -> None:
    run(ssh_command(host, remote_command, key_path, user))
