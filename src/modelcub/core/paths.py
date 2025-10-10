"""
Path resolution for ModelCub projects.

Updated to work with new .modelcub/ architecture.
"""
from __future__ import annotations
from pathlib import Path
from typing import Optional

# Cache directory (user-level, not project-level)
CACHE_DIR = (Path.home() / ".cache" / "modelcub" / "datasets").resolve()


def project_root() -> Path:
    """
    Find the project root by looking for .modelcub/ or modelcub.yaml.

    Walks up from CWD to find a directory containing:
    - .modelcub/ (new architecture)
    - modelcub.yaml (legacy fallback)
    """
    here = Path.cwd().resolve()

    for p in [here] + list(here.parents):
        # Prefer new architecture
        if (p / ".modelcub").is_dir():
            return p
        # Fallback to legacy
        if (p / "modelcub.yaml").exists():
            return p

    # If not in a project, return CWD
    return here


def modelcub_dir() -> Path:
    """Get the .modelcub directory for the current project."""
    return project_root() / ".modelcub"


def config_file() -> Path:
    """Get path to .modelcub/config.yaml."""
    return modelcub_dir() / "config.yaml"


def datasets_registry() -> Path:
    """Get path to .modelcub/datasets.yaml."""
    return modelcub_dir() / "datasets.yaml"


def runs_registry() -> Path:
    """Get path to .modelcub/runs.yaml."""
    return modelcub_dir() / "runs.yaml"


def history_dir() -> Path:
    """Get path to .modelcub/history/."""
    return modelcub_dir() / "history"


def cache_dir() -> Path:
    """Get path to .modelcub/cache/."""
    return modelcub_dir() / "cache"


def backups_dir() -> Path:
    """Get path to .modelcub/backups/."""
    return modelcub_dir() / "backups"


def datasets_dir() -> Path:
    """
    Get path to datasets directory.

    Tries to load from config, falls back to data/datasets
    """
    try:
        from .config import load_config
        config = load_config(project_root())
        if config:
            return project_root() / config.paths.data / "datasets"
    except:
        pass

    # Fallback
    return project_root() / "data" / "datasets"


def runs_dir() -> Path:
    """
    Get path to runs directory.

    Tries to load from config, falls back to runs/
    """
    try:
        from .config import load_config
        config = load_config(project_root())
        if config:
            return project_root() / config.paths.runs
    except:
        pass

    # Fallback
    return project_root() / "runs"


def reports_dir() -> Path:
    """
    Get path to reports directory.

    Tries to load from config, falls back to reports/
    """
    try:
        from .config import load_config
        config = load_config(project_root())
        if config:
            return project_root() / config.paths.reports
    except:
        pass

    # Fallback
    return project_root() / "reports"