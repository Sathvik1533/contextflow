"""Terminal Context Capture — Read shell history and detect errors.

This module captures terminal context by:
1. Reading shell history file (~/.zsh_history or ~/.bash_history)
2. Extracting recent commands (last 20)
3. Detecting error patterns (Error:, Traceback, etc.)
4. Getting current working directory

Why read history file?
- Simple and reliable
- Works on all systems
- No terminal integration needed

Limitations:
- Only captures commands, not full output
- Errors only visible if in command itself
- Week 3 will add live terminal hooking
"""

import os
import re
from pathlib import Path
from typing import Any


def capture_terminal_context() -> dict[str, Any]:
    """Capture terminal context from shell history.
    
    This function:
    1. Detects shell type (zsh or bash)
    2. Reads history file
    3. Extracts last 20 commands
    4. Detects error patterns
    5. Gets current directory
    
    Returns:
        dict with keys:
        - recent_commands: List[str] (last 20 commands)
        - errors_detected: List[str] (commands with error keywords)
        - current_directory: str (cwd)
        - shell_type: str (zsh or bash)
    
    Raises:
        None (returns empty dict on failure, logs warning)
    """
    result = {
        "recent_commands": [],
        "errors_detected": [],
        "current_directory": os.getcwd(),
        "shell_type": "unknown",
    }
    
    # Detect shell type and history file
    shell_type, history_file = _detect_shell_and_history()
    result["shell_type"] = shell_type
    
    if not history_file:
        return result

    # Read history file
    try:
        commands = _read_history_file(history_file, shell_type)
        result["recent_commands"] = commands[-20:]  # Last 20 commands

        # Detect errors in commands
        result["errors_detected"] = _detect_errors(commands[-50:])  # Check last 50

    except Exception:
        pass
    
    return result


def _detect_shell_and_history() -> tuple[str, Path | None]:
    """Detect shell type and locate history file.
    
    Returns:
        (shell_type, history_file_path)
        shell_type: "zsh", "bash", or "unknown"
        history_file_path: Path object or None
    """
    home = Path.home()
    
    # Check for zsh history
    zsh_history = home / ".zsh_history"
    if zsh_history.exists():
        return ("zsh", zsh_history)
    
    # Check for bash history
    bash_history = home / ".bash_history"
    if bash_history.exists():
        return ("bash", bash_history)
    
    # Check HISTFILE environment variable
    histfile = os.getenv("HISTFILE")
    if histfile:
        histfile_path = Path(histfile)
        if histfile_path.exists():
            return ("custom", histfile_path)
    
    return ("unknown", None)


def _read_history_file(history_file: Path, shell_type: str) -> list[str]:
    """Read and parse shell history file.
    
    Args:
        history_file: Path to history file
        shell_type: "zsh", "bash", or "custom"
    
    Returns:
        List of command strings
    
    Notes:
        - zsh history format: `: timestamp:0;command`
        - bash history format: `command` (one per line)
        - Handles large files by reading last 1000 lines only
    """
    # Check file size
    file_size = history_file.stat().st_size
    if file_size > 1_000_000:  # 1MB
        # Read last 1000 lines (approximate)
        with open(history_file, "rb") as f:
            f.seek(max(0, file_size - 100_000))  # Seek to ~100KB from end
            lines = f.read().decode("utf-8", errors="ignore").splitlines()
            lines = lines[-1000:]  # Last 1000 lines
    else:
        # Read entire file
        with open(history_file, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    
    # Parse based on shell type
    commands = []
    
    if shell_type == "zsh":
        # zsh format: `: 1234567890:0;command`
        for line in lines:
            line = line.strip()
            if line.startswith(":"):
                # Extract command after `;`
                parts = line.split(";", 1)
                if len(parts) == 2:
                    commands.append(parts[1].strip())
            else:
                # Fallback: treat as plain command
                commands.append(line)
    
    else:  # bash or custom
        # bash format: one command per line
        commands = [line.strip() for line in lines if line.strip()]
    
    return commands


def _detect_errors(commands: list[str]) -> list[str]:
    """Detect commands that likely resulted in errors.
    
    Args:
        commands: List of recent commands
    
    Returns:
        List of commands with error keywords
    
    Error patterns:
        - Commands with "error" keyword (case-insensitive)
        - Commands that failed (exit code in zsh history)
        - Common error commands (e.g., "command not found")
    
    Limitations:
        - Only detects errors in command text itself
        - Cannot detect errors in command output (need live terminal hook)
        - Week 3 will add full output capture
    """
    error_patterns = [
        r"error",
        r"failed",
        r"exception",
        r"traceback",
        r"not found",
        r"permission denied",
        r"cannot",
        r"unable to",
    ]
    
    errors = []
    
    for cmd in commands:
        cmd_lower = cmd.lower()
        for pattern in error_patterns:
            if re.search(pattern, cmd_lower):
                errors.append(cmd)
                break  # Only add once per command
    
    return errors


# Example usage (for testing)
if __name__ == "__main__":
    context = capture_terminal_context()
    print("\n=== TERMINAL CONTEXT ===")
    print(f"Shell: {context['shell_type']}")
    print(f"Directory: {context['current_directory']}")
    print(f"\nRecent commands ({len(context['recent_commands'])}):")
    for cmd in context['recent_commands'][-10:]:
        print(f"  {cmd}")
    print(f"\nErrors detected ({len(context['errors_detected'])}):")
    for err in context['errors_detected']:
        print(f"  ❌ {err}")
