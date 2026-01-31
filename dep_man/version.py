"""version.py, adopted from pydantic version.py (https://github.com/pydantic/pydantic/blob/main/pydantic/version.py)."""

from __future__ import annotations

import sys

__all__ = "VERSION", "version_info"

from .utils import git

VERSION = "0.1.2"


def version_info() -> str:
    """Return complete version information."""
    import importlib.metadata
    import platform
    from pathlib import Path

    package_names = {
        "pyright",
        "typing_extensions",
    }
    related_packages = []

    for dist in importlib.metadata.distributions():
        name = dist.metadata["Name"]
        if name in package_names:
            related_packages.append(f"{name}-{dist.version}")

    dep_man_dir = Path(__file__).parents[1].resolve()
    most_recent_commit = git.git_revision(dep_man_dir) if git.is_git_repo(dep_man_dir) and git.have_git() else "unknown"

    info = {
        "dep_man version": VERSION,
        "python version": sys.version,
        "platform": platform.platform(),
        "related packages": " ".join(related_packages),
        "commit": most_recent_commit,
    }
    return "\n".join("{:>30} {}".format(k + ":", str(v).replace("\n", " ")) for k, v in info.items())
