"""Project management commands."""
import click
from pathlib import Path
from modelcub.services.project_service import (
    init_project, delete_project,
    InitProjectRequest, DeleteProjectRequest
)
from modelcub.core.config import load_config
from modelcub.core.paths import project_root


@click.group()
def project():
    """Manage ModelCub projects."""
    pass


@project.command(name='list')
@click.option('--path', type=click.Path(exists=True), default='.', help='Directory to search')
def list_projects(path: str):
    """List all ModelCub projects in directory."""
    from modelcub.sdk import Project

    search_path = Path(path).resolve()
    projects = []

    click.echo(f"🔍 Searching for projects in {search_path}...")

    # Find all .modelcub directories
    for item in search_path.rglob(".modelcub"):
        if item.is_dir():
            project_path = item.parent
            try:
                proj = Project.load(str(project_path))
                projects.append(proj)
            except Exception as e:
                click.echo(f"⚠️  Warning: Failed to load project at {project_path}: {e}", err=True)

    if not projects:
        click.echo("No ModelCub projects found.")
        raise SystemExit(0)

    click.echo(f"\nFound {len(projects)} project(s):\n")
    for proj in projects:
        click.echo(f"  • {proj.name}")
        click.echo(f"    Path: {proj.path}")
        click.echo(f"    Created: {proj.created}")
        click.echo()

    raise SystemExit(0)


@project.command()
@click.argument('path', type=click.Path(), default='.')
@click.option('--name', '-n', help='Project name (defaults to directory name)')
@click.option('--force', '-f', is_flag=True, help='Overwrite existing project')
def init(path: str, name: str, force: bool):
    """Initialize a new ModelCub project."""
    req = InitProjectRequest(
        path=path,
        name=name,
        force=force
    )
    code, msg = init_project(req)
    click.echo(msg)
    raise SystemExit(code)


@project.command()
@click.argument('target', type=click.Path(), required=False)
@click.option('--yes', '-y', is_flag=True, help='Confirm deletion without prompting')
def delete(target: str, yes: bool):
    """Delete a ModelCub project directory."""
    req = DeleteProjectRequest(
        target=target,
        yes=yes
    )
    code, msg = delete_project(req)
    click.echo(msg)
    raise SystemExit(code)


@project.group()
def config():
    """Manage project configuration."""
    pass


@config.command(name='show')
def config_show():
    """Show full project configuration."""
    try:
        root = project_root()
        cfg = load_config(root)
        if not cfg:
            click.echo("❌ Not in a ModelCub project")
            raise SystemExit(2)
        click.echo(cfg.to_yaml_string())
    except Exception as e:
        click.echo(f"❌ Error loading project: {e}")
        raise SystemExit(2)


@config.command(name='get')
@click.argument('key')
def config_get(key: str):
    """Get a configuration value by key (e.g., 'defaults.device')."""
    try:
        root = project_root()
        cfg = load_config(root)
        if not cfg:
            click.echo("❌ Not in a ModelCub project")
            raise SystemExit(2)

        parts = key.split(".")
        value = cfg

        for part in parts:
            if hasattr(value, part):
                value = getattr(value, part)
            else:
                click.echo(f"❌ Config key not found: {key}")
                raise SystemExit(2)

        click.echo(value)
    except Exception as e:
        click.echo(f"❌ Error getting config: {e}")
        raise SystemExit(2)


@config.command(name='set')
@click.argument('key')
@click.argument('value')
def config_set(key: str, value: str):
    """Set a configuration value by key."""
    try:
        root = project_root()
        cfg = load_config(root)
        if not cfg:
            click.echo("❌ Not in a ModelCub project")
            raise SystemExit(2)

        parts = key.split(".")
        target = cfg

        # Navigate to parent
        for part in parts[:-1]:
            if hasattr(target, part):
                target = getattr(target, part)
            else:
                click.echo(f"❌ Config key not found: {key}")
                raise SystemExit(2)

        # Set value on parent
        attr_name = parts[-1]
        if not hasattr(target, attr_name):
            click.echo(f"❌ Config key not found: {key}")
            raise SystemExit(2)

        # Type conversion
        current = getattr(target, attr_name)
        if isinstance(current, bool):
            typed_value = value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(current, int):
            typed_value = int(value)
        elif isinstance(current, float):
            typed_value = float(value)
        else:
            typed_value = value

        setattr(target, attr_name, typed_value)

        # Save config
        from modelcub.core.config import save_config
        save_config(root, cfg)

        click.echo(f"✅ Set {key} = {typed_value}")
    except Exception as e:
        click.echo(f"❌ Error setting config: {e}")
        raise SystemExit(2)