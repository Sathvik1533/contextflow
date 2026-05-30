"""Git Context Capture — Signal 3 for ContextFlow's capture_node.

TASK-016: Enriches every capture with the developer's current git state.

WHY THIS EXISTS:
  ContextFlow's Guide agent was giving generic advice because it didn't know
  what the developer was actually building. Two developers can have the same
  error on screen — but one is on branch 'feature/auth' and the other is on
  'hotfix/payment'. The advice should be completely different.

  Git context makes Guide's advice surgical instead of generic.

WHAT IT CAPTURES:
  - Current branch name     → "You're on feature/memory-agent"
  - Last 3 commit messages  → "You recently added ChromaDB — check that first"
  - Uncommitted file list   → "memory.py is modified — the error is likely there"

FALLBACK:
  Not a git repo? Not a problem. Returns {is_git_repo: False} silently.
  The pipeline never crashes. Git context is enrichment, not a requirement.

DESIGN PATTERN: Context Aggregation
  capture_node collects multiple signals (screen + terminal + git) before
  any LLM sees them. More context = more precise advice.
"""

import subprocess
from pathlib import Path
from typing import Any

from src.utils.logger import get_logger

logger = get_logger(__name__)


def capture_git_context(cwd: str | None = None) -> dict[str, Any]:
    """Capture current git repository state.

    Runs three git commands silently via subprocess and returns structured data.
    Falls back gracefully if not in a git repo or git is not installed.

    Args:
        cwd: Directory to run git commands in. Defaults to current directory.
             capture_node passes terminal_context["current_directory"] here.

    Returns:
        dict with keys:
            is_git_repo: bool — False means all other fields are empty
            branch: str — current branch name (e.g. "feature/memory-agent")
            last_commits: list[str] — last 3 commits, one-line format
            uncommitted_files: list[str] — modified/untracked files
            repo_root: str — absolute path to repo root (empty if not git repo)

    Data Flow:
        capture_node() calls this function
            → subprocess runs git commands in cwd
            → results parsed into dict
            → dict stored as terminal_context["git"]
            → guide_node reads terminal_context["git"]
            → injected into Guide prompt
    """
    working_dir = cwd or str(Path.cwd())

    empty = {
        "is_git_repo": False,
        "branch": "",
        "last_commits": [],
        "uncommitted_files": [],
        "repo_root": "",
    }

    try:
        # Check if this directory is inside a git repo at all
        # git rev-parse --git-dir returns ".git" if yes, error if no
        check = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if check.returncode != 0:
            return empty

        # Get current branch name
        branch = _run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"], working_dir)

        # Get last 3 commits — one line each (hash + message)
        log_output = _run_git(["git", "log", "--oneline", "-3"], working_dir)
        last_commits = [line.strip() for line in log_output.splitlines() if line.strip()]

        # Get uncommitted file list — M=modified, ??=untracked, A=added
        status_output = _run_git(["git", "status", "--short"], working_dir)
        uncommitted_files = [
            line.strip() for line in status_output.splitlines() if line.strip()
        ]

        # Get repo root path
        repo_root = _run_git(["git", "rev-parse", "--show-toplevel"], working_dir)

        logger.debug(
            "Git context captured | branch=%s | commits=%d | uncommitted=%d",
            branch, len(last_commits), len(uncommitted_files),
        )

        return {
            "is_git_repo": True,
            "branch": branch.strip(),
            "last_commits": last_commits[:3],
            "uncommitted_files": uncommitted_files[:10],  # cap at 10
            "repo_root": repo_root.strip(),
        }

    except FileNotFoundError:
        # git is not installed on this machine
        logger.debug("Git not found — skipping git context")
        return empty
    except Exception:
        # Any other failure — log and continue, never crash the pipeline
        logger.exception("capture_git_context failed — returning empty")
        return empty


def _run_git(cmd: list[str], cwd: str) -> str:
    """Run a single git command and return stdout as a string.

    Args:
        cmd: The git command as a list (e.g. ["git", "log", "--oneline", "-3"])
        cwd: Directory to run the command in

    Returns:
        stdout output as a string, empty string if command fails
    """
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode == 0:
        return result.stdout
    return ""


def format_git_for_guide(git_context: dict[str, Any]) -> str:
    """Format git_context dict into a string for injection into Guide prompt.

    Called inside guide.py's context string builder.
    Returns empty string if not a git repo — Guide prompt stays clean.

    Args:
        git_context: The dict returned by capture_git_context()

    Returns:
        Formatted string block, or "" if not a git repo
    """
    if not git_context.get("is_git_repo"):
        return ""

    parts = ["\nGIT CONTEXT:"]

    branch = git_context.get("branch", "")
    if branch:
        parts.append(f"Branch: {branch}")

    commits = git_context.get("last_commits", [])
    if commits:
        parts.append("Last commits:")
        for commit in commits:
            parts.append(f"  - {commit}")

    uncommitted = git_context.get("uncommitted_files", [])
    if uncommitted:
        parts.append(f"Uncommitted changes: {', '.join(uncommitted[:5])}")

    return "\n".join(parts)
