import io
import subprocess
import sys
from pathlib import Path

from .redaction import redact_text


class CommandError(RuntimeError):
    pass


_TRACE_BACK_MARKER = "Traceback (most recent call last):"
_DEBUG_LINE_PREFIXES = ("DEBUG:", "[DEBUG]")
_verbose = False


def set_verbose(enabled: bool) -> None:
    global _verbose
    _verbose = enabled


def _effective_verbose(verbose: bool | None) -> bool:
    return _verbose if verbose is None else verbose


def _is_debug_only_line(line: str) -> bool:
    stripped = line.lstrip()
    return any(stripped.startswith(prefix) for prefix in _DEBUG_LINE_PREFIXES)


def _traceback_emit_state(line: str, in_traceback: bool, verbose: bool) -> tuple[bool, bool]:
    if _TRACE_BACK_MARKER in line:
        return verbose, True
    if in_traceback:
        if verbose:
            return True, True
        if line and not line.startswith((" ", "\t")):
            return True, False
        return False, True
    if not verbose and _is_debug_only_line(line):
        return False, False
    return True, False


def _emit_streamed_line(line: str, *, in_traceback: bool, verbose: bool) -> bool:
    emit, in_traceback = _traceback_emit_state(line, in_traceback, verbose)
    if emit:
        print(redact_text(line), end="", file=sys.stdout)
    return in_traceback


def _run_streamed(
    command: list[str],
    cwd: Path | None,
    *,
    verbose: bool,
    capture: bool,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    proc = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        stdin=None,
        env=env,
    )
    captured: list[str] = []
    in_traceback = False
    assert proc.stdout is not None
    for line in proc.stdout:
        if capture:
            captured.append(line)
        in_traceback = _emit_streamed_line(line, in_traceback=in_traceback, verbose=verbose)
    returncode = proc.wait()
    output = "".join(captured)
    return subprocess.CompletedProcess(command, returncode, output, "")


def _filter_captured_output(text: str, verbose: bool) -> str:
    if verbose or not text:
        return text
    out = io.StringIO()
    in_traceback = False
    for line in text.splitlines(keepends=True):
        emit, in_traceback = _traceback_emit_state(line, in_traceback, verbose)
        if emit:
            out.write(line)
    return out.getvalue()


def run(
    command: list[str],
    cwd: Path | None = None,
    check: bool = True,
    input_text: str | None = None,
    quiet: bool = False,
    stream: bool = False,
    stream_capture: bool = False,
    verbose: bool | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    show_verbose = _effective_verbose(verbose)
    display = " ".join(command)
    print(f"+ {redact_text(display)}")
    if stream:
        result = _run_streamed(command, cwd, verbose=show_verbose, capture=stream_capture, env=env)
        if check and result.returncode != 0:
            raise CommandError(f"Command failed with exit {result.returncode}: {redact_text(display)}")
        return result

    result = subprocess.run(
        command,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        input=input_text,
        env=env,
    )
    stdout = _filter_captured_output(result.stdout or "", show_verbose)
    stderr = _filter_captured_output(result.stderr or "", show_verbose)
    if stdout and not quiet:
        print(redact_text(stdout), end="")
    if stderr and not quiet:
        print(redact_text(stderr), end="", file=sys.stderr)
    if check and result.returncode != 0:
        raise CommandError(f"Command failed with exit {result.returncode}: {redact_text(display)}")
    return subprocess.CompletedProcess(result.args, result.returncode, stdout, stderr)
