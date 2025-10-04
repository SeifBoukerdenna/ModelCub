from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from ..core.io import delete_tree
from ..events import ProjectInitialized, ProjectDeleted, bus

DEFAULT_YAML = """# ModelCub project
project: {project_name}
images: data
labels: data/labels
models_dir: models
# Default classes act as a fallback when a dataset does not specify classes
classes: [object]
"""
DEFAULT_GITIGNORE = """# ModelCub
models/
runs/
.cache/
__pycache__/
*.pyc
*.pyo
*.DS_Store
"""

@dataclass
class InitProjectRequest:
    path: str
    name: str | None
    force: bool = False

@dataclass
class DeleteProjectRequest:
    target: str | None
    yes: bool = False

def _write_if_missing(path: Path, content: str, *, force: bool) -> None:
    if path.exists() and not force:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def _resolve_delete_target(target: str | None) -> Path:
    if target is None:
        return Path.cwd().resolve()
    p = Path(target)
    return (p if p.is_absolute() else (Path.cwd() / p)).resolve()

def _looks_like_project(root: Path) -> bool:
    return (root / "modelcub.yaml").exists()

def init_project(req: InitProjectRequest) -> tuple[int, str]:
    root = Path(req.path).resolve()
    root.mkdir(parents=True, exist_ok=True)
    name = req.name or root.name

    # dirs
    for d in ("data", "data/labels", "models"):
        (root / d).mkdir(parents=True, exist_ok=True)

    # files
    _write_if_missing(root / "modelcub.yaml", DEFAULT_YAML.format(project_name=name), force=req.force)
    _write_if_missing(root / ".gitignore", DEFAULT_GITIGNORE, force=False)

    bus.publish(ProjectInitialized(path=str(root), name=name))
    return 0, f"Initialized ModelCub project at: {root}\n- modelcub.yaml (project: {name})\n- data/, models/ created"

def delete_project(req: DeleteProjectRequest) -> tuple[int, str]:
    root = _resolve_delete_target(req.target)
    if not _looks_like_project(root):
        return 2, f"No modelcub.yaml in {root}. Not a ModelCub project."

    if not req.yes:
        # The caller (commands layer) should have asked for confirmation.
        # We keep this guard to be safe.
        return 2, "Refusing to delete without confirmation (--yes)."

    delete_tree(root)
    bus.publish(ProjectDeleted(path=str(root)))
    return 0, f"Deleted project directory: {root}"
