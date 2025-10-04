from __future__ import annotations
from pathlib import Path

CACHE_DIR = (Path.home() / ".cache" / "modelcub" / "datasets").resolve()

def project_root() -> Path:
    """Walk up from CWD to find a directory containing modelcub.yaml."""
    here = Path.cwd().resolve()
    for p in [here] + list(here.parents):
        if (p / "modelcub.yaml").exists():
            return p
    return here  # fallback; still works outside a project, but features are limited
