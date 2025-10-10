"""
Project service with Timeline architecture.

Creates the full .modelcub/ structure as specified in timeline.md
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from ..core.io import delete_tree
from ..core.config import Config, create_default_config, save_config, load_config
from ..core.registries import initialize_registries
from ..events import ProjectInitialized, ProjectDeleted, bus


SIMPLE_PROJECT_MARKER = """# ModelCub Project
# Full configuration in .modelcub/config.yaml
project: {name}
"""

DEFAULT_GITIGNORE = """# ModelCub
.modelcub/cache/
runs/
reports/
*.pt
*.onnx
__pycache__/
*.pyc
*.pyo
.DS_Store
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


def _create_directory_structure(root: Path, config: Config) -> None:
    """Create the full project directory structure."""
    (root / config.paths.data / "datasets").mkdir(parents=True, exist_ok=True)
    (root / config.paths.runs).mkdir(parents=True, exist_ok=True)
    (root / config.paths.reports).mkdir(parents=True, exist_ok=True)

    modelcub_dir = root / ".modelcub"
    modelcub_dir.mkdir(parents=True, exist_ok=True)

    (modelcub_dir / "history" / "commits").mkdir(parents=True, exist_ok=True)
    (modelcub_dir / "history" / "snapshots").mkdir(parents=True, exist_ok=True)
    (modelcub_dir / "cache").mkdir(parents=True, exist_ok=True)
    (modelcub_dir / "backups").mkdir(parents=True, exist_ok=True)


def _write_project_files(root: Path, name: str, config: Config, force: bool) -> None:
    """Write project configuration files."""
    save_config(root, config)

    marker_path = root / "modelcub.yaml"
    if not marker_path.exists() or force:
        marker_path.write_text(SIMPLE_PROJECT_MARKER.format(name=name), encoding="utf-8")

    initialize_registries(root)

    gitignore_path = root / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(DEFAULT_GITIGNORE, encoding="utf-8")

    for empty_dir in [
        root / config.paths.data / "datasets",
        root / config.paths.runs,
        root / config.paths.reports,
    ]:
        gitkeep = empty_dir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("# Keep this directory in git\n", encoding="utf-8")


def _resolve_delete_target(target: str | None) -> Path:
    """Resolve the target path for deletion."""
    if target is None:
        return Path.cwd().resolve()
    p = Path(target)
    return (p if p.is_absolute() else (Path.cwd() / p)).resolve()


def _looks_like_project(root: Path) -> bool:
    """Check if directory looks like a ModelCub project."""
    if (root / ".modelcub").exists():
        return True
    if (root / "modelcub.yaml").exists():
        return True
    return False


def _is_repository(root: Path) -> bool:
    """Detect if path looks like a source code repository."""
    danger_files = {".git", "pyproject.toml", "setup.py", "setup.cfg", "src"}
    repo_markers = {f for f in danger_files if (root / f).exists()}
    return len(repo_markers) >= 2


def init_project(req: InitProjectRequest) -> tuple[int, str]:
    """
    Initialize a new ModelCub project with full timeline architecture.
    """
    root = Path(req.path).resolve()
    root.mkdir(parents=True, exist_ok=True)

    name = req.name or root.name

    if not req.force and _looks_like_project(root):
        config = load_config(root)
        if config:
            return 1, f"Project already initialized: {name}\nUse --force to reinitialize."

    config = create_default_config(name)

    _create_directory_structure(root, config)
    _write_project_files(root, name, config, req.force)

    bus.publish(ProjectInitialized(path=str(root), name=name))

    msg = f"""✨ Initialized ModelCub project: {name}

📁 Created structure:
   ├── .modelcub/         (config, registries, history)
   ├── data/datasets/     (your datasets)
   ├── runs/              (training outputs)
   ├── reports/           (generated reports)
   ├── modelcub.yaml      (project marker)
   └── .gitignore         (git defaults)

🔧 Configuration: .modelcub/config.yaml
   • Device: {config.defaults.device}
   • Batch size: {config.defaults.batch_size}
   • Image size: {config.defaults.image_size}
   • Format: {config.defaults.format}

📚 Next steps:
   1. Add a dataset: modelcub dataset add my-data --source cub
   2. List datasets: modelcub dataset list

Project root: {root}
"""

    return 0, msg


def delete_project(req: DeleteProjectRequest) -> tuple[int, str]:
    """
    Delete a ModelCub project directory.
    """
    root = _resolve_delete_target(req.target)

    if not _looks_like_project(root):
        return 2, f"❌ Not a ModelCub project: {root}\n   (No .modelcub/ or modelcub.yaml found)"

    if not req.yes:
        return 2, (
            f"⚠️  Refusing to delete without confirmation.\n"
            f"   Target: {root}\n"
            f"   Use --yes flag to confirm deletion."
        )

    if _is_repository(root):
        return 2, (
            f"🚨 SAFETY: Refusing to delete {root}\n\n"
            f"   This appears to be a source repository!\n"
            f"   Detected: .git, pyproject.toml, or similar files\n\n"
            f"   To delete a ModelCub project:\n"
            f"   1. Navigate OUT of the project first\n"
            f"   2. Run: modelcub project delete <path> --yes\n\n"
            f"   Or delete manually: rm -rf {root}"
        )

    delete_tree(root)

    bus.publish(ProjectDeleted(path=str(root)))

    return 0, f"✅ Deleted project directory: {root}"