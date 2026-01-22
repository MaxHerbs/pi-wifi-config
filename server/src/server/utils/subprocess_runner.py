import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CommandResult:
    success: bool
    stdout: str
    stderr: str
    return_code: int


def run_command(
    args: List[str],
    timeout: int = 30,
    check: bool = False,
    input_text: Optional[str] = None,
) -> CommandResult:
    """
    Run a command safely with proper argument handling.

    Args:
        args: List of command arguments (no shell expansion)
        timeout: Timeout in seconds
        check: If True, raise exception on non-zero return code
        input_text: Optional input to pass to stdin

    Returns:
        CommandResult with success status, stdout, stderr, and return code
    """
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            input=input_text,
        )
        success = result.returncode == 0

        if check and not success:
            raise subprocess.CalledProcessError(
                result.returncode, args, result.stdout, result.stderr
            )

        return CommandResult(
            success=success,
            stdout=result.stdout,
            stderr=result.stderr,
            return_code=result.returncode,
        )
    except subprocess.TimeoutExpired:
        return CommandResult(
            success=False,
            stdout="",
            stderr=f"Command timed out after {timeout} seconds",
            return_code=-1,
        )
    except FileNotFoundError:
        return CommandResult(
            success=False,
            stdout="",
            stderr=f"Command not found: {args[0]}",
            return_code=-1,
        )
    except Exception as e:
        return CommandResult(
            success=False,
            stdout="",
            stderr=str(e),
            return_code=-1,
        )


def run_sudo_command(
    args: List[str],
    timeout: int = 30,
    input_text: Optional[str] = None,
) -> CommandResult:
    """
    Run a command with sudo.

    Args:
        args: List of command arguments (sudo will be prepended)
        timeout: Timeout in seconds
        input_text: Optional input to pass to stdin

    Returns:
        CommandResult with success status, stdout, stderr, and return code
    """
    return run_command(["sudo"] + args, timeout=timeout, input_text=input_text)
