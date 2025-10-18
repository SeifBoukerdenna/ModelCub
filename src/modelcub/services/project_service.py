"""Project service with logging and timing."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from ..core.io import delete_tree
from ..core.config import Config, create_default_config, save_config, load_config
from ..core.registries import initialize_registries
from ..core.service_result import ServiceResult
from ..core.service_logging import log_service_call
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

PLAYGROUND_TEMPLATE = '''"""
ModelCub SDK Playground

Quick experimentation and testing with your project's SDK.
Run with: python playground.py
"""
from modelcub import Project, Dataset
from pathlib import Path

# Auto-load current project
project = Project.load()
print(f"📦 Project: {{project.name}}")
print(f"📍 Path: {{project.path}}")
print()

# ========== Helper Functions ==========

def list_datasets():
    """Show all datasets in this project."""
    datasets = project.list_datasets()
    if not datasets:
        print("  No datasets yet")
        return []

    for ds in datasets:
        print(f"  - {{ds.name}} (v{{ds.version}}): {{ds.num_images}} images, {{len(ds.classes)}} classes")
    return datasets


def list_runs():
    """Show all training runs."""
    runs = project.list_runs()
    if not runs:
        print("  No training runs yet")
        return []

    for run in runs:
        print(f"  - {{run.name}}: {{run.status}}")
    return runs


def load_dataset(name: str):
    """Load a dataset by name."""
    dataset = project.get_dataset(name)
    print(f"\\nLoaded: {{dataset.name}}")
    print(f"  Images: {{dataset.num_images}}")
    print(f"  Classes: {{', '.join(dataset.classes)}}")
    return dataset


# ========== Quick Overview ==========

if __name__ == "__main__":
    print("📊 Datasets:")
    datasets = list_datasets()

    print("\\n🏃 Training Runs:")
    runs = list_runs()

    print("\\n" + "="*50)
    print("Add your experiments below:")
    print("="*50)

    # ========== Your Experiments Here ==========

    # Example: Load and inspect a dataset
    # dataset = load_dataset("my-dataset-v1")
    # print(f"First image: {{dataset.image_paths[0]}}")

    # Example: Get dataset statistics
    # stats = dataset.get_stats()
    # print(f"Class distribution: {{stats.class_distribution}}")

    # Example: Load a training run
    # run = project.get_run("my-run-20241010")
    # print(f"Best mAP50: {{run.results.best_map50}}")
    # print(f"Training time: {{run.results.training_time}}")

    # Example: Create a new dataset programmatically
    # new_dataset = project.create_dataset(
    #     name="test-dataset",
    #     source="/path/to/images",
    #     format="yolo"
    # )

    pass  # Your code here
'''


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
    (modelcub_dir / "logs").mkdir(parents=True, exist_ok=True)


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

    playground_path = root / "playground.py"
    if not playground_path.exists() or force:
        playground_path.write_text(PLAYGROUND_TEMPLATE, encoding="utf-8")

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


@log_service_call("init_project")
def init_project(req: InitProjectRequest) -> ServiceResult[str]:
    """Initialize a new ModelCub project."""
    root = Path(req.path).resolve()
    root.mkdir(parents=True, exist_ok=True)

    name = req.name or root.name

    if not req.force and _looks_like_project(root):
        config = load_config(root)
        if config:
            msg = f"Project already initialized: {name}\nUse --force to reinitialize."
            return ServiceResult.error(msg, code=1)

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
   ├── playground.py      (SDK experimentation)
   └── .gitignore         (git defaults)

🔧 Configuration: .modelcub/config.yaml
   • Device: {config.defaults.device}
   • Batch size: {config.defaults.batch_size}
   • Image size: {config.defaults.image_size}
   • Format: {config.defaults.format}

📚 Next steps:
   1. Experiment with SDK: python playground.py
   2. Add a dataset: modelcub dataset add my-data --source ./data
   3. List datasets: modelcub dataset list

Project root: {root}
"""

    return ServiceResult.ok(data=str(root), message=msg)


@log_service_call("delete_project")
def delete_project(req: DeleteProjectRequest) -> ServiceResult[str]:
    """Delete a ModelCub project directory."""
    root = _resolve_delete_target(req.target)

    if not _looks_like_project(root):
        msg = f"❌ Not a ModelCub project: {root}\n   (No .modelcub/ or modelcub.yaml found)"
        return ServiceResult.error(msg, code=2)

    if not req.yes:
        msg = (
            f"⚠️  Refusing to delete without confirmation.\n"
            f"   Target: {root}\n"
            f"   Use --yes flag to confirm deletion."
        )
        return ServiceResult.error(msg, code=3)

    if _is_repository(root):
        msg = (
            f"❌ Target looks like a source code repository: {root}\n"
            f"   Found indicators: .git, pyproject.toml, or setup.py\n"
            f"   Refusing to delete for safety."
        )
        return ServiceResult.error(msg, code=4)

    try:
        bus.publish(ProjectDeleted(path=str(root)))
        delete_tree(root)
        msg = f"✅ Deleted project: {root}"
        return ServiceResult.ok(data=str(root), message=msg)
    except Exception as e:
        msg = f"❌ Failed to delete project: {e}"
        return ServiceResult.error(msg, code=5)