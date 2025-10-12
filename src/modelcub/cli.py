from __future__ import annotations
import argparse

from .commands.project import run as project_run
from .commands.ui import run as ui_run  # Fixed import
from .commands.dataset import run as dataset_run
from .commands.about import run as about_run
from .core.hardware import warn_cpu_mode, is_inside_project, suppress_warning, is_warning_suppressed
from .events import GPUWarningSuppressed, bus

def main(argv=None):
    parser = argparse.ArgumentParser(prog="modelcub", description="ModelCub CLI")
    parser.add_argument("--suppress-absent-gpu", action="store_true",
                       help="Suppress GPU/CPU warning for the rest of this terminal session")
    sub = parser.add_subparsers(dest="command", required=False)

    # ---- project ----
    p_proj = sub.add_parser("project", help="Project-level actions")
    proj_sub = p_proj.add_subparsers(dest="proj_cmd", required=True)

    p_proj_init = proj_sub.add_parser("init", help="Create a new ModelCub project")
    p_proj_init.add_argument(
        "name",
        help="Project name - creates ./<name>/ directory with full structure"
    )
    p_proj_init.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing project"
    )
    p_proj_init.add_argument(
        "--template",
        choices=["detection", "segmentation", "classification"],
        help="Project template (future proof)"
    )
    p_proj_init.set_defaults(func=project_run)

    p_proj_delete = proj_sub.add_parser("delete", help="Delete a ModelCub project (destructive)")
    p_proj_delete.add_argument(
        "target", nargs="?", default=None,
        help="Project name or path. If omitted, deletes the current project."
    )
    p_proj_delete.add_argument("--yes", action="store_true", help="Skip confirmation.")
    p_proj_delete.set_defaults(func=project_run)

    # ---- ui ----
    p_ui = sub.add_parser("ui", help="Launch ModelCub web UI")
    p_ui.add_argument(
        "--dev",
        action="store_true",
        help="Run in development mode with hot reload"
    )
    p_ui.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    p_ui.add_argument(
        "--host",
        default="127.0.0.1",
        help="Server host (default: 127.0.0.1)"
    )
    p_ui.set_defaults(func=ui_run)

    # ---- dataset ----
    p_ds = sub.add_parser("dataset", help="Manage datasets within a project")
    ds_sub = p_ds.add_subparsers(dest="ds_cmd", required=True)

    p_ds_add = ds_sub.add_parser("add", help="Add (create/import) a dataset under data/<name>")
    p_ds_add.add_argument("name", help="Dataset folder name under data/")
    p_ds_add.add_argument("--source", default="cub", help="Built-in source (e.g., cub, toy-shapes).")
    p_ds_add.add_argument("--classes", default=None, help="Override classes (comma-separated).")
    p_ds_add.add_argument("--n", type=int, default=200, help="(generators) total images.")
    p_ds_add.add_argument("--train-frac", type=float, default=0.8, help="(generators) train split fraction.")
    p_ds_add.add_argument("--imgsz", type=int, default=640, help="(generators) image size.")
    p_ds_add.add_argument("--seed", type=int, default=123, help="(generators) RNG seed.")
    p_ds_add.add_argument("--force", action="store_true", help="Overwrite non-empty dataset dir.")
    p_ds_add.set_defaults(func=dataset_run)

    p_ds_edit = ds_sub.add_parser("edit", help="Edit dataset classes")
    p_ds_edit.add_argument("name", help="Dataset name under data/")
    p_ds_edit.add_argument("--classes", required=True, help="New classes (comma-separated).")
    p_ds_edit.set_defaults(func=dataset_run)

    p_ds_del = ds_sub.add_parser("delete", help="Delete a dataset directory (asks for confirmation)")
    p_ds_del.add_argument("name", help="Dataset name under data/")
    p_ds_del.add_argument("--yes", action="store_true", help="Skip confirmation.")
    p_ds_del.add_argument("--purge-cache", action="store_true", help="Also delete cached archives for known sources.")
    p_ds_del.set_defaults(func=dataset_run)

    p_ds_list = ds_sub.add_parser("list", help="List datasets in the project")
    p_ds_list.set_defaults(func=dataset_run)

    p_ds_info = ds_sub.add_parser("info", help="Show dataset manifest and quick stats")
    p_ds_info.add_argument("name", help="Dataset name under data/")
    p_ds_info.set_defaults(func=dataset_run)

    # ---- about ----
    p_about = sub.add_parser("about", help="Show version and environment info.")
    p_about.set_defaults(func=about_run)

    args = parser.parse_args(argv)

    # Handle suppress flag - set for session and publish event
    if args.suppress_absent_gpu:
        suppress_warning()
        bus.publish(GPUWarningSuppressed())
        print("✓ GPU warning suppressed for this terminal session.")
        if args.command is None:
            return 0

    # Show GPU warning only if inside project and not suppressed
    if is_inside_project():
        warn_cpu_mode()

    # If no command given, show help
    if args.command is None:
        parser.print_help()
        return 0

    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())