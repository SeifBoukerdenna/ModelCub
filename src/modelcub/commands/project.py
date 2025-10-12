"""Project management commands."""
from pathlib import Path
from modelcub.services.project_service import (
    init_project,
    delete_project,
    InitProjectRequest,
    DeleteProjectRequest
)
from modelcub.sdk.project import Project
from modelcub.core.config import load_config


def run(args) -> int:
    """Route project subcommands."""
    cmd = args.proj_cmd

    if cmd == "init":
        return _init(args)
    elif cmd == "delete":
        return _delete(args)
    elif cmd == "config":
        return _config(args)
    else:
        print(f"Unknown project command: {cmd}")
        return 1


def _init(args) -> int:
    """Handle: modelcub project init <name>"""
    req = InitProjectRequest(
        path=args.name,
        name=args.name,
        force=args.force
    )
    code, msg = init_project(req)
    print(msg)
    return code


def _delete(args) -> int:
    """Handle: modelcub project delete [target]"""
    req = DeleteProjectRequest(
        target=args.target,
        yes=args.yes
    )
    code, msg = delete_project(req)
    print(msg)
    return code


def _config(args) -> int:
    """Handle: modelcub project config <subcommand>"""
    config_cmd = args.config_cmd

    if config_cmd == "show":
        return _config_show(args)
    elif config_cmd == "get":
        return _config_get(args)
    elif config_cmd == "set":
        return _config_set(args)
    else:
        print(f"Unknown config command: {config_cmd}")
        return 1


def _config_show(args) -> int:
    """
    Show all configuration.

    Usage: modelcub project config show [--path <project>]
    """
    try:
        # Load project
        project_path = args.path if args.path else "."
        project = Project.load(project_path)

        print(f"\n📋 Configuration for: {project.name}")
        print(f"   Project path: {project.path}")
        print()

        # Show project section
        print("🔹 Project:")
        print(f"   name: {project.config.project.name}")
        print(f"   created: {project.config.project.created}")
        print(f"   version: {project.config.project.version}")
        print()

        # Show defaults section
        print("🔹 Defaults:")
        print(f"   device: {project.config.defaults.device}")
        print(f"   batch_size: {project.config.defaults.batch_size}")
        print(f"   image_size: {project.config.defaults.image_size}")
        print(f"   workers: {project.config.defaults.workers}")
        print(f"   format: {project.config.defaults.format}")
        print()

        # Show paths section
        print("🔹 Paths:")
        print(f"   data: {project.config.paths.data}")
        print(f"   runs: {project.config.paths.runs}")
        print(f"   reports: {project.config.paths.reports}")
        print()

        print("💡 To edit config:")
        print("   modelcub project config set <key> <value>")
        print("   Example: modelcub project config set defaults.batch_size 32")
        print()
        print("⚠️  Do NOT edit .modelcub/config.yaml directly!")
        print("   Always use the CLI, SDK, or UI to modify configuration.")
        print()

        return 0

    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Failed to load project: {e}")
        return 1


def _config_get(args) -> int:
    """
    Get a configuration value.

    Usage: modelcub project config get <key> [--path <project>]
    Example: modelcub project config get defaults.device
    """
    try:
        # Load project
        project_path = args.path if args.path else "."
        project = Project.load(project_path)

        # Get value
        key = args.key
        value = project.get_config(key, default=None)

        if value is None:
            print(f"❌ Config key not found: {key}")
            print()
            print("Available keys:")
            print("  project.name, project.created, project.version")
            print("  defaults.device, defaults.batch_size, defaults.image_size")
            print("  defaults.workers, defaults.format")
            print("  paths.data, paths.runs, paths.reports")
            return 1

        # Print result
        print(f"{key} = {value}")
        return 0

    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Failed to get config: {e}")
        return 1


def _config_set(args) -> int:
    """
    Set a configuration value.

    Usage: modelcub project config set <key> <value> [--path <project>]
    Example: modelcub project config set defaults.batch_size 32
    """
    try:
        # Load project
        project_path = args.path if args.path else "."
        project = Project.load(project_path)

        key = args.key
        value = args.value

        # Convert value to appropriate type
        converted_value = _convert_value(value)

        # Validate key exists
        old_value = project.get_config(key, default="__NOT_FOUND__")
        if old_value == "__NOT_FOUND__":
            print(f"❌ Config key not found: {key}")
            print()
            print("Available keys:")
            print("  defaults.device, defaults.batch_size, defaults.image_size")
            print("  defaults.workers, defaults.format")
            print("  paths.data, paths.runs, paths.reports")
            print()
            print("⚠️  Project metadata (project.name, project.created) cannot be changed.")
            return 1

        # Prevent changing project metadata
        if key.startswith("project."):
            print(f"❌ Cannot modify project metadata: {key}")
            print("   Project name, created date, and version are immutable.")
            return 1

        # Set value
        try:
            project.set_config(key, converted_value)
            project.save_config()

            print(f"✅ Configuration updated:")
            print(f"   {key}: {old_value} → {converted_value}")
            print()
            print(f"💾 Saved to: {project.path}/.modelcub/config.yaml")
            return 0

        except ValueError as e:
            print(f"❌ Invalid config path: {e}")
            return 1

    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Failed to set config: {e}")
        return 1


def _convert_value(value: str):
    """Convert string value to appropriate Python type."""
    # Try int
    try:
        return int(value)
    except ValueError:
        pass

    # Try float
    try:
        return float(value)
    except ValueError:
        pass

    # Try boolean
    if value.lower() in ("true", "yes", "1"):
        return True
    if value.lower() in ("false", "no", "0"):
        return False

    # Return as string
    return value