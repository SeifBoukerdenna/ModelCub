from __future__ import annotations
import argparse
import os
from pathlib import Path

# ⭐ SMART WORKING DIRECTORY DETECTION
def get_user_working_dir() -> str:
    """Get the actual user's working directory, not the source directory."""
    cwd = Path.cwd().resolve()

    if (cwd / "cli.py").exists() or (cwd / "__init__.py").exists() and cwd.name == "modelcub":
        possible_root = cwd
        while possible_root.parent != possible_root:
            parent = possible_root.parent
            if (parent / ".git").exists() or parent.name not in ["src", "modelcub"]:
                return str(parent)
            possible_root = parent
        return str(cwd.parent.parent)

    return str(cwd)

ORIGINAL_WORKING_DIR = get_user_working_dir()
os.environ["MODELCUB_WORKING_DIR"] = ORIGINAL_WORKING_DIR

from .commands.project import run as project_run
from .commands.ui import run as ui_run
from .commands.dataset import run as dataset_run
from .commands.about import run as about_run
from .core.hardware import warn_cpu_mode, is_inside_project, suppress_warning
from .events import GPUWarningSuppressed, bus

def main(argv=None):
    parser = argparse.ArgumentParser(prog="modelcub", description="ModelCub CLI")
    parser.add_argument("--suppress-absent-gpu", action="store_true",
                       help="Suppress GPU/CPU warning for the rest of this terminal session")
    sub = parser.add_subparsers(dest="command", required=False)

    # ---- project ----
    p_proj = sub.add_parser("project", help="Project-level actions")
    proj_sub = p_proj.add_subparsers(dest="proj_cmd", required=True)

    # project init
    p_proj_init = proj_sub.add_parser("init", help="Create a new ModelCub project")
    p_proj_init.add_argument("name", help="Project name - creates ./<n>/ directory")
    p_proj_init.add_argument("--force", action="store_true", help="Overwrite existing project")
    p_proj_init.add_argument("--template", choices=["detection", "segmentation", "classification"],
                            help="Project template")
    p_proj_init.set_defaults(func=project_run)

    # project delete
    p_proj_delete = proj_sub.add_parser("delete", help="Delete a ModelCub project")
    p_proj_delete.add_argument("target", nargs="?", default=None,
                              help="Project name or path (default: current directory)")
    p_proj_delete.add_argument("--yes", action="store_true", help="Skip confirmation")
    p_proj_delete.set_defaults(func=project_run)

    # project config
    p_proj_config = proj_sub.add_parser("config", help="Manage project configuration")
    config_sub = p_proj_config.add_subparsers(dest="config_cmd", required=True)

    # project config show
    p_config_show = config_sub.add_parser("show", help="Show all configuration")
    p_config_show.add_argument("--path", default=None, help="Project path (default: current directory)")
    p_config_show.set_defaults(func=project_run)

    # project config get
    p_config_get = config_sub.add_parser("get", help="Get a configuration value")
    p_config_get.add_argument("key", help="Config key (e.g., defaults.device)")
    p_config_get.add_argument("--path", default=None, help="Project path (default: current directory)")
    p_config_get.set_defaults(func=project_run)

    # project config set
    p_config_set = config_sub.add_parser("set", help="Set a configuration value")
    p_config_set.add_argument("key", help="Config key (e.g., defaults.batch_size)")
    p_config_set.add_argument("value", help="New value")
    p_config_set.add_argument("--path", default=None, help="Project path (default: current directory)")
    p_config_set.set_defaults(func=project_run)

    # ---- ui ----
    p_ui = sub.add_parser("ui", help="Launch ModelCub web UI")
    p_ui.add_argument("--dev", action="store_true", help="Run in development mode")
    p_ui.add_argument("--port", type=int, default=8000, help="Server port")
    p_ui.add_argument("--host", default="127.0.0.1", help="Server host")
    p_ui.set_defaults(func=ui_run)

    # ---- dataset ----
    p_ds = sub.add_parser("dataset", help="Manage datasets")
    ds_sub = p_ds.add_subparsers(dest="ds_cmd", required=True)

    p_ds_add = ds_sub.add_parser("add", help="Add a dataset")
    p_ds_add.add_argument("name", help="Dataset name")
    p_ds_add.add_argument("--source", default="cub", help="Data source")
    p_ds_add.add_argument("--classes", default=None, help="Classes (comma-separated)")
    p_ds_add.add_argument("--n", type=int, default=200, help="Total images")
    p_ds_add.add_argument("--train-frac", type=float, default=0.8, help="Train fraction")
    p_ds_add.add_argument("--imgsz", type=int, default=640, help="Image size")
    p_ds_add.add_argument("--seed", type=int, default=123, help="Random seed")
    p_ds_add.add_argument("--force", action="store_true", help="Overwrite existing")
    p_ds_add.set_defaults(func=dataset_run)

    p_ds_edit = ds_sub.add_parser("edit", help="Edit dataset classes")
    p_ds_edit.add_argument("name", help="Dataset name")
    p_ds_edit.add_argument("--classes", required=True, help="New classes")
    p_ds_edit.set_defaults(func=dataset_run)

    p_ds_del = ds_sub.add_parser("delete", help="Delete a dataset")
    p_ds_del.add_argument("name", help="Dataset name")
    p_ds_del.add_argument("--yes", action="store_true", help="Skip confirmation")
    p_ds_del.add_argument("--purge-cache", action="store_true", help="Delete cached archives")
    p_ds_del.set_defaults(func=dataset_run)

    p_ds_list = ds_sub.add_parser("list", help="List datasets")
    p_ds_list.set_defaults(func=dataset_run)

    p_ds_info = ds_sub.add_parser("info", help="Show dataset info")
    p_ds_info.add_argument("name", help="Dataset name")
    p_ds_info.set_defaults(func=dataset_run)

    # ---- about ----
    p_about = sub.add_parser("about", help="Show version and environment info")
    p_about.set_defaults(func=about_run)

    args = parser.parse_args(argv)

    # Handle suppress flag
    if args.suppress_absent_gpu:
        suppress_warning()
        bus.publish(GPUWarningSuppressed())
        print("✓ GPU warning suppressed for this terminal session.")
        if args.command is None:
            return 0

    # Show GPU warning if inside project
    if is_inside_project():
        warn_cpu_mode()

    # No command given
    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())