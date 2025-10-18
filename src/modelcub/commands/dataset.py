"""Dataset management commands."""
import click
from pathlib import Path


@click.group()
def dataset():
    """Manage datasets."""
    pass


@dataset.command()
def list():
    """List all datasets in the project."""
    from modelcub.services.dataset_service import list_datasets

    result = list_datasets()
    click.echo(result.message)
    raise SystemExit(0 if result.success else result.code)


@dataset.command()
@click.argument('name')
def info(name: str):
    """Show detailed information about a dataset."""
    from modelcub.services.dataset_service import info_dataset

    result = info_dataset(name)
    click.echo(result.message)
    raise SystemExit(0 if result.success else result.code)


@dataset.command()
@click.argument('name')
@click.option('--source', '-s', required=True, help='Dataset source (e.g., cub, shapes)')
@click.option('--classes', help='Override classes (comma-separated)')
@click.option('--n', type=int, default=200, help='Number of images for generated datasets')
@click.option('--train-frac', type=float, default=0.8, help='Training split fraction')
@click.option('--imgsz', type=int, default=640, help='Image size for generated datasets')
@click.option('--seed', type=int, default=123, help='Random seed')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing dataset')
def add(name: str, source: str, classes: str, n: int, train_frac: float,
        imgsz: int, seed: int, force: bool):
    """Add a new dataset from a source."""
    from modelcub.services.dataset_service import add_dataset, AddDatasetRequest

    req = AddDatasetRequest(
        name=name,
        source=source,
        classes_override=classes,
        n=n,
        train_frac=train_frac,
        imgsz=imgsz,
        seed=seed,
        force=force
    )

    result = add_dataset(req)
    click.echo(result.message)
    raise SystemExit(0 if result.success else result.code)


@dataset.command(name='import')
@click.option('--source', required=True, type=click.Path(exists=True),
              help='Source directory containing images')
@click.option('--name', help='Dataset name (auto-generated if not provided)')
@click.option('--classes', help='Classes (comma-separated)')
@click.option('--symlink', is_flag=True, help='Create symlinks instead of copying files')
@click.option('--no-validate', is_flag=True, help='Skip image validation')
@click.option('--recursive', is_flag=True, help='Recursively scan subdirectories')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing dataset with same name')
def import_(source: str, name: str, classes: str, symlink: bool,
            no_validate: bool, recursive: bool, force: bool):
    """Import images from a folder."""
    from modelcub.services.image_service import import_images, ImportImagesRequest
    from modelcub.core.images import scan_directory
    from modelcub.core.paths import project_root

    source_path = Path(source).resolve()

    classes_list = None
    if classes:
        classes_list = [c.strip() for c in classes.split(",") if c.strip()]

    click.echo(f"🔍 Scanning {source_path}...")
    scan_result = scan_directory(source_path, recursive=recursive)

    if scan_result.total_count == 0:
        click.echo(f"❌ No image files found in {source_path}")
        click.echo("Consider running the command with the --recursive flag if images are in subfolders")
        raise SystemExit(2)

    click.echo(f"   Found {scan_result.total_count} image files")

    if not no_validate:
        click.echo("\n✓ Validating images...")
        click.echo("   [████████████████████] 100%")
        click.echo()
        click.echo(f"   ✅ {scan_result.valid_count} valid images")

        if scan_result.invalid_count > 0:
            click.echo(f"   ⚠️  {scan_result.invalid_count} skipped (corrupt/unreadable)")

            if scan_result.invalid_count <= 5:
                for path, error in scan_result.invalid:
                    click.echo(f"      • {path.name}: {error}")
            else:
                for path, error in scan_result.invalid[:3]:
                    click.echo(f"      • {path.name}: {error}")
                click.echo(f"      ... and {scan_result.invalid_count - 3} more")

    if scan_result.valid_count == 0:
        click.echo("\n❌ No valid images to import")
        raise SystemExit(2)

    name_display = name or "(auto-generated)"
    click.echo(f"\n📦 Importing as '{name_display}'...")

    req = ImportImagesRequest(
        project_path=project_root(),
        source=source_path,
        dataset_name=name,
        classes=classes_list,
        copy=not symlink,
        validate=not no_validate,
        recursive=recursive,
        force=force
    )

    if not symlink:
        click.echo("   Copying files...")
    else:
        click.echo("   Creating symlinks...")

    click.echo("   [████████████████████] 100%")
    click.echo()

    result = import_images(req)

    if result.success:
        click.echo(result.message)
        if classes_list:
            click.echo(f"   Classes: {', '.join(classes_list)}")
        raise SystemExit(0)
    else:
        click.echo(f"❌ {result.message}")
        raise SystemExit(1)


@dataset.command()
@click.argument('name')
@click.option('--new-name', help='New dataset name')
@click.option('--classes', '-c', help='New classes (comma-separated)')
def edit(name: str, new_name: str, classes: str):
    """Edit dataset metadata."""
    from modelcub.services.dataset_service import edit_dataset, EditDatasetRequest

    if not new_name and not classes:
        click.echo("❌ Provide at least one option: --new-name or --classes")
        raise SystemExit(2)

    if classes:
        req = EditDatasetRequest(name=name, classes=classes)
        result = edit_dataset(req)
        click.echo(result.message)
        raise SystemExit(0 if result.success else result.code)

    if new_name:
        click.echo("⚠️  Dataset renaming not yet implemented")
        raise SystemExit(1)


@dataset.command()
@click.argument('name')
@click.option('--yes', '-y', is_flag=True, help='Confirm deletion without prompting')
@click.option('--purge-cache', is_flag=True, help='Also delete cached downloads')
def delete(name: str, yes: bool, purge_cache: bool):
    """Delete a dataset."""
    from modelcub.services.dataset_service import delete_dataset, DeleteDatasetRequest

    req = DeleteDatasetRequest(name=name, yes=yes, purge_cache=purge_cache)
    result = delete_dataset(req)
    click.echo(result.message)
    raise SystemExit(0 if result.success else result.code)


# ============ dataset classes subcommands ============

@dataset.group()
def classes():
    """Manage dataset classes."""
    pass


@classes.command(name='list')
@click.argument('dataset')
def classes_list(dataset: str):
    """List classes in a dataset."""
    from modelcub.sdk.project import Project
    from modelcub.core.exceptions import DatasetNotFoundError

    try:
        project = Project.load()
        class_list = project.datasets.list_classes(dataset)

        if not class_list:
            click.echo(f"⚠️  No classes in dataset: {dataset}")
            raise SystemExit(0)

        click.echo(f"Classes in {dataset}:")
        for idx, class_name in enumerate(class_list):
            click.echo(f"  {idx}: {class_name}")
        click.echo(f"\n✨ Total: {len(class_list)} classes")
        raise SystemExit(0)

    except DatasetNotFoundError as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Not in a ModelCub project: {e}")
        raise SystemExit(2)


@classes.command(name='add')
@click.argument('dataset')
@click.argument('class_name')
@click.option('--id', 'class_id', type=int, help='Class ID (auto-assigned if not provided)')
def classes_add(dataset: str, class_name: str, class_id: int):
    """Add a class to a dataset."""
    from modelcub.sdk.project import Project
    from modelcub.core.exceptions import DatasetNotFoundError, ClassExistsError

    try:
        project = Project.load()
        assigned_id = project.datasets.add_class(dataset, class_name, class_id)
        click.echo(f"✅ Added class: {class_name} (ID: {assigned_id})")
        raise SystemExit(0)

    except (DatasetNotFoundError, ClassExistsError) as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Not in a ModelCub project: {e}")
        raise SystemExit(2)


@classes.command(name='remove')
@click.argument('dataset')
@click.argument('class_name')
@click.option('--yes', '-y', is_flag=True, help='Skip confirmation')
def classes_remove(dataset: str, class_name: str, yes: bool):
    """Remove a class from a dataset."""
    from modelcub.sdk.project import Project
    from modelcub.core.exceptions import DatasetNotFoundError, ClassNotFoundError

    try:
        project = Project.load()

        if not yes:
            class_list = project.datasets.list_classes(dataset)
            if class_name not in class_list:
                click.echo(f"❌ Class not found: {class_name}")
                raise SystemExit(2)

            confirm = click.confirm(f"Remove '{class_name}' from {dataset}?", default=False)
            if not confirm:
                click.echo("❌ Cancelled")
                raise SystemExit(1)

        project.datasets.remove_class(dataset, class_name)
        click.echo(f"✅ Removed class: {class_name}")
        click.echo("⚠️  Existing labels unchanged")
        raise SystemExit(0)

    except (DatasetNotFoundError, ClassNotFoundError) as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Not in a ModelCub project: {e}")
        raise SystemExit(2)


@classes.command(name='rename')
@click.argument('dataset')
@click.argument('old_name')
@click.argument('new_name')
def classes_rename(dataset: str, old_name: str, new_name: str):
    """Rename a class."""
    from modelcub.sdk.project import Project
    from modelcub.core.exceptions import DatasetNotFoundError, ClassNotFoundError, ClassExistsError

    try:
        project = Project.load()
        project.datasets.rename_class(dataset, old_name, new_name)
        click.echo(f"✅ Renamed: {old_name} → {new_name}")
        raise SystemExit(0)

    except (DatasetNotFoundError, ClassNotFoundError, ClassExistsError) as e:
        click.echo(f"❌ {e}")
        raise SystemExit(2)
    except Exception as e:
        click.echo(f"❌ Not in a ModelCub project: {e}")
        raise SystemExit(2)