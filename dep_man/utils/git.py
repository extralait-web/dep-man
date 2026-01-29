"""Git utilities, adopted from mypy's git utilities (https://github.com/python/mypy/blob/master/mypy/git.py)."""

from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def is_git_repo(direction: Path) -> bool:
    """Is the given directory version-controlled with git?"""
    return direction.joinpath(".git").exists()


def have_git() -> bool:  # pragma: no cover
    """Can we run the git executable?"""
    try:
        subprocess.check_output(["git", "--help"])
        return True
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def git_revision(direction: Path) -> str:
    """Get the SHA-1 of the HEAD of a git repository."""
    return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=direction).decode("utf-8").strip()
