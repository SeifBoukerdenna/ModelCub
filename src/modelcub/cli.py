"""
ModelCub CLI - Main command-line interface.
"""
import sys
import argparse
from pathlib import Path


def project_run(args) -> int:
    """Handle project commands."""
    from modelcub.services.project_service import (
        init_project, delete_project,
        InitProjectRequest, DeleteProjectRequest
    )
    from modelcub.core.config import load_config
    from modelcub.core.paths import project_root

    if args.proj_cmd == "init":
        req = InitProjectRequest(
            path=args.path,
            name=args.name,
            force=args.force
        )
        code, msg = init_project(req)
        print(msg)
        return code

    elif args.proj_cmd == "delete":
        req = DeleteProjectRequest(
            target=args.target,
            yes=args.yes
        )
        code, msg = delete_project(req)
        print(msg)
        return code

    elif args.proj_cmd == "config":
        try:
            root = project_root()
            config = load_config(root)
            if not config:
                print("❌ Not in a ModelCub project")
                return 2
        except Exception as e:
            print(f"❌ Error loading project: {e}")
            return 2

        if args.config_cmd == "show":
            print(config.to_yaml_string())
            return 0

        elif args.config_cmd == "get":
            parts = args.key.split(".")
            value = config

            try:
                for part in parts:
                    if hasattr(value, part):
                        value = getattr(value, part)
                    else:
                        print(f"❌ Config key not found: {args.key}")
                        return 2

                print(value)
                return 0
            except Exception as e:
                print(f"❌ Error getting config: {e}")
                return 2

        elif args.config_cmd == "set":
            parts = args.key.split(".")
            obj = config

            try:
                for part in parts[:-1]:
                    if hasattr(obj, part):
                        obj = getattr(obj, part)
                    else:
                        print(f"❌ Config key not found: {args.key}")
                        return 2

                attr_name = parts[-1]
                if not hasattr(obj, attr_name):
                    print(f"❌ Config key not found: {args.key}")
                    return 2

                current = getattr(obj, attr_name)
                if isinstance(current, int):
                    value = int(args.value)
                elif isinstance(current, float):
                    value = float(args.value)
                elif isinstance(current, bool):
                    value = args.value.lower() in ("true", "1", "yes")
                else:
                    value = args.value

                setattr(obj, attr_name, value)

                from modelcub.core.config import save_config
                save_config(root, config)

                print(f"✅ Set {args.key} = {value}")
                return 0
            except Exception as e:
                print(f"❌ Error setting config: {e}")
                return 2

    return 0


def dataset_run(args) -> int:
    """Handle dataset commands."""
    from modelcub.services.dataset_service import (
        add_dataset, list_datasets, info_dataset,
        edit_dataset, delete_dataset,
        AddDatasetRequest, EditDatasetRequest, DeleteDatasetRequest
    )

    if args.ds_cmd == "import":
        return handle_dataset_import(args)

    elif args.ds_cmd == "add":
        req = AddDatasetRequest(
            name=args.name,
            source=args.source,
            classes_override=args.classes,
            n=args.n,
            train_frac=args.train_frac,
            imgsz=args.imgsz,
            seed=args.seed,
            force=args.force
        )
        code, msg = add_dataset(req)
        print(msg)
        return code

    elif args.ds_cmd == "list":
        code, output = list_datasets()
        print(output)
        return code

    elif args.ds_cmd == "info":
        code, output = info_dataset(args.name)
        print(output)
        return code

    elif args.ds_cmd == "edit":
        req = EditDatasetRequest(
            name=args.name,
            new_name=getattr(args, "new_name", None),
            classes=getattr(args, "classes", None)
        )
        code, msg = edit_dataset(req)
        print(msg)
        return code

    elif args.ds_cmd == "delete":
        if not args.yes:
            print(f"⚠️  About to delete dataset: {args.name}")
            confirm = input("Type dataset name to confirm: ")
            if confirm != args.name:
                print("❌ Deletion cancelled")
                return 1

        req = DeleteDatasetRequest(
            name=args.name,
            yes=args.yes,
            purge_cache=getattr(args, "purge_cache", False)
        )
        code, msg = delete_dataset(req)
        print(msg)
        return code

    return 0


def handle_dataset_import(args) -> int:
    """Handle dataset import command."""
    from pathlib import Path
    from modelcub.services.image_service import import_images, ImportImagesRequest
    from modelcub.core.images import scan_directory
    from modelcub.core.paths import project_root

    source = Path(args.source).resolve()

    # Parse classes if provided
    classes = None
    if args.classes:
        classes = [c.strip() for c in args.classes.split(",") if c.strip()]

    print(f"🔍 Scanning {source}...")
    scan_result = scan_directory(source, recursive=args.recursive)

    if scan_result.total_count == 0:
        print(f"❌ No image files found in {source}")
        print(f"Consider running the command with the --recursive flag if images are in subfolders")
        return 2

    print(f"   Found {scan_result.total_count} image files")

    if not args.no_validate:
        print("\n✓ Validating images...")
        print("   [████████████████████] 100%")
        print()
        print(f"   ✅ {scan_result.valid_count} valid images")

        if scan_result.invalid_count > 0:
            print(f"   ⚠️  {scan_result.invalid_count} skipped (corrupt/unreadable)")

            if scan_result.invalid_count <= 5:
                for path, error in scan_result.invalid:
                    print(f"      • {path.name}: {error}")
            else:
                for path, error in scan_result.invalid[:3]:
                    print(f"      • {path.name}: {error}")
                print(f"      ... and {scan_result.invalid_count - 3} more")

    if scan_result.valid_count == 0:
        print("\n❌ No valid images to import")
        return 2

    name_display = args.name or "(auto-generated)"
    print(f"\n📦 Importing as '{name_display}'...")

    req = ImportImagesRequest(
        project_path=project_root(),
        source=source,
        dataset_name=args.name,
        classes=classes,
        copy=not args.symlink,
        validate=not args.no_validate,
        recursive=args.recursive,
        force=args.force
    )

    if not args.symlink:
        print("   Copying files...")
    else:
        print("   Creating symlinks...")

    print("   [████████████████████] 100%")
    print()

    result = import_images(req)

    if result.success:
        print(result.message)
        if classes:
            print(f"   Classes: {', '.join(classes)}")
        return 0
    else:
        print(f"❌ {result.message}")
        return 1


def classes_run(args) -> int:
    """Handle dataset classes commands."""
    from modelcub.sdk.project import Project
    from modelcub.core.exceptions import (
        DatasetNotFoundError,
        ClassExistsError,
        ClassNotFoundError
    )

    try:
        project = Project.load()
    except Exception as e:
        print(f"❌ Not in a ModelCub project: {e}")
        return 2

    try:
        if args.class_cmd == "list":
            classes = project.datasets.list_classes(args.dataset)

            if not classes:
                print(f"⚠️  No classes in dataset: {args.dataset}")
                return 0

            print(f"Classes in {args.dataset}:")
            for idx, class_name in enumerate(classes):
                print(f"  {idx}: {class_name}")
            print(f"\n✨ Total: {len(classes)} classes")
            return 0

        elif args.class_cmd == "add":
            class_id = project.datasets.add_class(
                args.dataset,
                args.class_name,
                args.id
            )
            print(f"✅ Added class: {args.class_name} (ID: {class_id})")
            return 0

        elif args.class_cmd == "remove":
            if not args.yes:
                classes = project.datasets.list_classes(args.dataset)
                if args.class_name not in classes:
                    print(f"❌ Class not found: {args.class_name}")
                    return 2

                confirm = input(f"Remove '{args.class_name}' from {args.dataset}? [y/N]: ")
                if confirm.lower() not in ('y', 'yes'):
                    print("❌ Cancelled")
                    return 1

            project.datasets.remove_class(args.dataset, args.class_name)
            print(f"✅ Removed class: {args.class_name}")
            print("⚠️  Existing labels unchanged")
            return 0

        elif args.class_cmd == "rename":
            project.datasets.rename_class(
                args.dataset,
                args.old_name,
                args.new_name
            )
            print(f"✅ Renamed: {args.old_name} → {args.new_name}")
            return 0

    except DatasetNotFoundError as e:
        print(f"❌ {e}")
        return 2
    except (ClassExistsError, ClassNotFoundError) as e:
        print(f"❌ {e}")
        return 2
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0


def ui_run(args) -> int:
    """Run UI command."""
    from modelcub.commands.ui import run
    return run(args)


def annotate_run(args) -> int:
    """Handle annotation commands."""
    from modelcub.sdk import Project

    try:
        project = Project.load()
        dataset = project.get_dataset(args.dataset)
    except Exception as e:
        print(f"❌ {e}")
        return 2

    if args.ann_cmd == "stats":
        stats = dataset.annotation_stats()
        print(f"📊 {args.dataset}")
        print(f"   Total: {stats['total_images']}")
        print(f"   Labeled: {stats['labeled']}")
        print(f"   Progress: {stats['progress']:.1%}")
        print(f"   Total boxes: {stats['total_boxes']}")
        return 0

    elif args.ann_cmd == "list":
        anns = dataset.get_annotations()
        labeled = [a for a in anns if a['num_boxes'] > 0]
        print(f"Labeled images in {args.dataset}:")
        for ann in labeled:
            print(f"  {ann['image_id']}: {ann['num_boxes']} boxes")
        return 0


def job_run(args) -> int:
    """Handle annotation job commands."""
    from modelcub.services.job_service import (
        create_job, start_job, pause_job, cancel_job,
        list_jobs, get_job_status as get_job_status_handler, watch_job
    )

    if args.job_cmd == "create":
        return create_job(args)

    elif args.job_cmd == "start":
        return start_job(args)

    elif args.job_cmd == "pause":
        return pause_job(args)

    elif args.job_cmd == "cancel":
        return cancel_job(args)

    elif args.job_cmd == "list":
        return list_jobs(args)

    elif args.job_cmd == "status":
        return get_job_status_handler(args)

    elif args.job_cmd == "watch":
        return watch_job(args)

    return 0


def setup_parsers() -> argparse.ArgumentParser:
    """Setup argument parsers for all commands."""
    parser = argparse.ArgumentParser(
        prog="modelcub",
        description="ModelCub - Complete computer vision platform"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="modelcub 0.0.2"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # ---- project ----
    p_proj = sub.add_parser("project", help="Manage projects")
    proj_sub = p_proj.add_subparsers(dest="proj_cmd", required=True)

    # project init
    p_proj_init = proj_sub.add_parser("init", help="Initialize a new project")
    p_proj_init.add_argument("path", default=".", nargs="?", help="Project path")
    p_proj_init.add_argument("--name", default=None, help="Project name")
    p_proj_init.add_argument("--force", action="store_true", help="Overwrite existing project")
    p_proj_init.set_defaults(func=project_run)

    # project delete
    p_proj_delete = proj_sub.add_parser("delete", help="Delete a project")
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

    # dataset import
    p_ds_import = ds_sub.add_parser("import", help="Import images from a folder")
    p_ds_import.add_argument("--source", required=True, help="Source directory containing images")
    p_ds_import.add_argument("--name", default=None, help="Dataset name (auto-generated if not provided)")
    p_ds_import.add_argument("--classes", default=None, help="Classes (comma-separated)")
    p_ds_import.add_argument("--symlink", action="store_true", help="Create symlinks instead of copying files")
    p_ds_import.add_argument("--no-validate", action="store_true", help="Skip image validation")
    p_ds_import.add_argument("--recursive", action="store_true", help="Recursively scan subdirectories")
    p_ds_import.add_argument("--force", action="store_true", help="Overwrite existing dataset with same name")
    p_ds_import.set_defaults(func=dataset_run)

    # dataset add
    p_ds_add = ds_sub.add_parser("add", help="Add a dataset")
    p_ds_add.add_argument("name", help="Dataset name")
    p_ds_add.add_argument("--source", default="cub", help="Data source")
    p_ds_add.add_argument("--classes", default=None, help="Classes (comma-separated)")
    p_ds_add.add_argument("--n", type=int, default=200, help="Total images")
    p_ds_add.add_argument("--train-frac", type=float, default=0.8, help="Train fraction")
    p_ds_add.add_argument("--imgsz", type=int, default=640, help="Image size")
    p_ds_add.add_argument("--seed", type=int, default=123, help="Random seed")
    p_ds_add.add_argument("--force", action="store_true", help="Overwrite existing dataset")
    p_ds_add.set_defaults(func=dataset_run)

    # dataset list
    p_ds_list = ds_sub.add_parser("list", help="List all datasets")
    p_ds_list.set_defaults(func=dataset_run)

    # dataset info
    p_ds_info = ds_sub.add_parser("info", help="Show dataset information")
    p_ds_info.add_argument("name", help="Dataset name")
    p_ds_info.set_defaults(func=dataset_run)

    # dataset edit
    p_ds_edit = ds_sub.add_parser("edit", help="Edit dataset metadata")
    p_ds_edit.add_argument("name", help="Dataset name")
    p_ds_edit.add_argument("--new-name", help="New dataset name")
    p_ds_edit.add_argument("--classes", help="New classes (comma-separated)")
    p_ds_edit.set_defaults(func=dataset_run)

    # dataset delete
    p_ds_delete = ds_sub.add_parser("delete", help="Delete a dataset")
    p_ds_delete.add_argument("name", help="Dataset name")
    p_ds_delete.add_argument("--yes", action="store_true", help="Skip confirmation")
    p_ds_delete.add_argument("--purge-cache", action="store_true", help="Also delete cache")
    p_ds_delete.set_defaults(func=dataset_run)

    # dataset classes
    p_ds_classes = ds_sub.add_parser("classes", help="Manage dataset classes")
    classes_sub = p_ds_classes.add_subparsers(dest="class_cmd", required=True)

    # dataset classes list
    p_class_list = classes_sub.add_parser("list", help="List classes in a dataset")
    p_class_list.add_argument("dataset", help="Dataset name")
    p_class_list.set_defaults(func=classes_run)

    # dataset classes add
    p_class_add = classes_sub.add_parser("add", help="Add a class to a dataset")
    p_class_add.add_argument("dataset", help="Dataset name")
    p_class_add.add_argument("class_name", help="Class name to add")
    p_class_add.add_argument("--id", type=int, default=None,
                            help="Class ID (auto-assigned if not provided)")
    p_class_add.set_defaults(func=classes_run)

    # dataset classes remove
    p_class_remove = classes_sub.add_parser("remove", help="Remove a class from a dataset")
    p_class_remove.add_argument("dataset", help="Dataset name")
    p_class_remove.add_argument("class_name", help="Class name to remove")
    p_class_remove.add_argument("--yes", action="store_true", help="Skip confirmation")
    p_class_remove.set_defaults(func=classes_run)

    # dataset classes rename
    p_class_rename = classes_sub.add_parser("rename", help="Rename a class")
    p_class_rename.add_argument("dataset", help="Dataset name")
    p_class_rename.add_argument("old_name", help="Current class name")
    p_class_rename.add_argument("new_name", help="New class name")
    p_class_rename.set_defaults(func=classes_run)

    # ---- annotate ----
    p_ann = sub.add_parser("annotate", help="Annotation commands")
    ann_sub = p_ann.add_subparsers(dest="ann_cmd", required=True)

    p_ann_stats = ann_sub.add_parser("stats", help="Show annotation stats")
    p_ann_stats.add_argument("dataset", help="Dataset name")
    p_ann_stats.set_defaults(func=annotate_run)

    p_ann_list = ann_sub.add_parser("list", help="List annotations")
    p_ann_list.add_argument("dataset", help="Dataset name")
    p_ann_list.set_defaults(func=annotate_run)

    # ---- job ----
    p_job = sub.add_parser("job", help="Manage annotation jobs")
    job_sub = p_job.add_subparsers(dest="job_cmd", required=True)

    # job create
    p_job_create = job_sub.add_parser("create", help="Create an annotation job")
    p_job_create.add_argument("dataset", help="Dataset name")
    p_job_create.add_argument("--images", nargs="+", help="Specific image IDs to annotate")
    p_job_create.add_argument("--workers", type=int, default=4, help="Number of worker threads")
    p_job_create.add_argument("--auto-start", action="store_true", help="Automatically start the job")
    p_job_create.set_defaults(func=job_run)

    # job start
    p_job_start = job_sub.add_parser("start", help="Start or resume a job")
    p_job_start.add_argument("job_id", help="Job ID")
    p_job_start.add_argument("--watch", action="store_true", help="Watch job progress")
    p_job_start.set_defaults(func=job_run)

    # job pause
    p_job_pause = job_sub.add_parser("pause", help="Pause a running job")
    p_job_pause.add_argument("job_id", help="Job ID")
    p_job_pause.set_defaults(func=job_run)

    # job cancel
    p_job_cancel = job_sub.add_parser("cancel", help="Cancel a job")
    p_job_cancel.add_argument("job_id", help="Job ID")
    p_job_cancel.add_argument("--force", action="store_true", help="Skip confirmation")
    p_job_cancel.set_defaults(func=job_run)

    # job list
    p_job_list = job_sub.add_parser("list", help="List all jobs")
    p_job_list.add_argument("--status", choices=["pending", "running", "paused", "completed", "failed", "cancelled"],
                           help="Filter by status")
    p_job_list.set_defaults(func=job_run)

    # job status
    p_job_status = job_sub.add_parser("status", help="Get detailed job status")
    p_job_status.add_argument("job_id", help="Job ID")
    p_job_status.set_defaults(func=job_run)

    # job watch
    p_job_watch = job_sub.add_parser("watch", help="Watch job progress")
    p_job_watch.add_argument("job_id", help="Job ID")
    p_job_watch.set_defaults(func=job_run)

    return parser


def main() -> int:
    """Main CLI entry point."""
    parser = setup_parsers()
    args = parser.parse_args()

    if hasattr(args, "func"):
        try:
            return args.func(args)
        except KeyboardInterrupt:
            print("\n❌ Interrupted by user")
            return 130
        except Exception as e:
            print(f"❌ Error: {e}")
            if "--debug" in sys.argv:
                import traceback
                traceback.print_exc()
            return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())