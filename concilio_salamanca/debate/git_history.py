from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


MDE_HISTORY_INDEX = "_index.json"


def get_git_log(path: str = ".", n: int = 20) -> str:
    """Returns the last `n` git log entries as a formatted string.

    Returns empty string if the directory is not a git repo or git fails.
    """
    try:
        result = subprocess.run(
            ["git", "log", f"-{n}", "--oneline", "--decorate", "--no-color"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=path,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return ""


def get_mde_history(path: str = ".") -> Optional[Dict]:
    """Reads the .mde_history/_index.json file if it exists.

    Expected format:
    {
      "project": "project-name",
      "sessions": [
        {
          "id": "session-uuid",
          "timestamp": "2025-01-01T12:00:00",
          "action": "audit|refactor|review",
          "summary": "Short description",
          "files_affected": ["file1.py", "file2.js"],
          "tokens_used": 15000,
          "outcome": "success|partial|failed"
        }
      ]
    }
    """
    history_dir = Path(path) / ".mde_history"
    index_path = history_dir / MDE_HISTORY_INDEX
    if not index_path.exists():
        return None
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def format_mde_history_as_text(history: Dict) -> str:
    """Formats the MDE history dict into a readable context string."""
    if not history:
        return ""
    lines = [f"--- MDE HISTORY: {history.get('project', 'unknown')} ---"]
    sessions = history.get("sessions", [])
    if sessions:
        for s in sessions[-5:]:
            ts = s.get("timestamp", "?")[:19]
            action = s.get("action", "?")
            summary = s.get("summary", "")[:80]
            outcome = s.get("outcome", "?")
            files = s.get("files_affected", [])
            files_str = ", ".join(files[:3])
            lines.append(f"  [{ts}] {action.upper()}: {summary} ({outcome})")
            if files_str:
                lines.append(f"         files: {files_str}")
    else:
        lines.append("  (no sessions recorded)")
    return "\n".join(lines)


def format_git_context(path: str = ".", n: int = 20) -> str:
    """Combines git log and MDE history into a single context block."""
    parts: List[str] = []

    git_log = get_git_log(path, n)
    if git_log:
        parts.append("--- GIT LOG (ultimos commits) ---")
        parts.append(git_log)

    history = get_mde_history(path)
    if history:
        parts.append(format_mde_history_as_text(history))
    else:
        parts.append("(no .mde_history encontrado)")

    return "\n\n".join(parts)
