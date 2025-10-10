#!/usr/bin/env python3
"""
ModelCub SDK Playground

Interactive testing ground for the ModelCub Python SDK.
Run this to experiment with the API!

Usage:
    python playground.py
"""
import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modelcub import Project


def section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def demo_create_project():
    """Demo: Create a new project."""
    section("1. Creating a New Project")

    # Create project in /tmp
    print("\n>>> from modelcub import Project")
    print(">>> project = Project.init('playground-test')")

    project = Project.init("playground-test")

    print(f"\n✅ Created: {project}")
    print(f"   Path: {project.path}")
    print(f"   Name: {project.name}")
    print(f"   Created: {project.created}")
    print(f"   Version: {project.version}")

    return project


def demo_config_access(project: Project):
    """Demo: Access and modify config."""
    section("2. Accessing Configuration")

    print("\n>>> project.config.defaults.device")
    print(f"   {project.config.defaults.device}")

    print("\n>>> project.config.defaults.batch_size")
    print(f"   {project.config.defaults.batch_size}")

    print("\n>>> project.config.defaults.image_size")
    print(f"   {project.config.defaults.image_size}")

    # Using get_config
    print("\n>>> project.get_config('defaults.device')")
    print(f"   {project.get_config('defaults.device')}")

    # Modify config
    section("3. Modifying Configuration")

    print("\n>>> project.config.defaults.batch_size = 32")
    project.config.defaults.batch_size = 32

    print(">>> project.config.defaults.device = 'cpu'")
    project.config.defaults.device = "cpu"

    print(">>> project.save_config()")
    project.save_config()

    print("\n✅ Config saved!")

    # Verify by reloading
    print("\n>>> project.reload_config()")
    project.reload_config()

    print(f">>> project.config.defaults.batch_size")
    print(f"   {project.config.defaults.batch_size}")

    print(f">>> project.config.defaults.device")
    print(f"   {project.config.defaults.device}")


def demo_paths(project: Project):
    """Demo: Access project paths."""
    section("4. Project Paths")

    print("\n>>> project.path")
    print(f"   {project.path}")

    print("\n>>> project.modelcub_dir")
    print(f"   {project.modelcub_dir}")

    print("\n>>> project.datasets_dir")
    print(f"   {project.datasets_dir}")

    print("\n>>> project.runs_dir")
    print(f"   {project.runs_dir}")

    print("\n>>> project.reports_dir")
    print(f"   {project.reports_dir}")

    print("\n>>> project.cache_dir")
    print(f"   {project.cache_dir}")

    print("\n>>> project.history_dir")
    print(f"   {project.history_dir}")


def demo_registries(project: Project):
    """Demo: Access registries."""
    section("5. Registry Access")

    print("\n>>> project.datasets.list_datasets()")
    datasets = project.datasets.list_datasets()
    print(f"   {len(datasets)} datasets")

    if datasets:
        for ds in datasets:
            print(f"   - {ds['name']}: {ds.get('classes', [])}")
    else:
        print("   (no datasets yet)")

    print("\n>>> project.runs.list_runs()")
    runs = project.runs.list_runs()
    print(f"   {len(runs)} runs")

    if runs:
        for run in runs:
            print(f"   - {run['name']}")
    else:
        print("   (no runs yet)")


def demo_load_project():
    """Demo: Load existing project."""
    section("6. Loading Existing Project")

    print("\n>>> project = Project.load('playground-test')")
    project = Project.load("playground-test")

    print(f"\n✅ Loaded: {project}")
    print(f"   Name: {project.name}")
    print(f"   Device: {project.config.defaults.device}")
    print(f"   Batch size: {project.config.defaults.batch_size}")

    return project


def demo_exists():
    """Demo: Check if project exists."""
    section("7. Checking Project Existence")

    print("\n>>> Project.exists('playground-test')")
    exists = Project.exists("playground-test")
    print(f"   {exists}")

    print("\n>>> Project.exists('nonexistent-project')")
    exists = Project.exists("nonexistent-project")
    print(f"   {exists}")


def demo_context_manager(project: Project):
    """Demo: Using project as context manager."""
    section("8. Context Manager (Auto-save)")

    print("\n>>> with Project.load('playground-test') as project:")
    print("...     project.config.defaults.workers = 16")
    print("...     # Auto-saves on exit")

    with Project.load("playground-test") as p:
        p.config.defaults.workers = 16

    print("\n✅ Config auto-saved on context exit")

    # Verify
    p = Project.load("playground-test")
    print(f"\n>>> project.config.defaults.workers")
    print(f"   {p.config.defaults.workers}")


def demo_set_config():
    """Demo: Using set_config helper."""
    section("9. Using set_config Helper")

    project = Project.load("playground-test")

    print("\n>>> project.set_config('defaults.image_size', 1024)")
    project.set_config("defaults.image_size", 1024)

    print(">>> project.save_config()")
    project.save_config()

    print("\n>>> project.get_config('defaults.image_size')")
    value = project.get_config("defaults.image_size")
    print(f"   {value}")


def demo_cleanup():
    """Demo: Delete project."""
    section("10. Cleaning Up")

    print("\n>>> project = Project.load('playground-test')")
    project = Project.load("playground-test")

    print(">>> project.delete(confirm=True)")
    project.delete(confirm=True)

    print("\n✅ Project deleted!")

    print("\n>>> Project.exists('playground-test')")
    exists = Project.exists("playground-test")
    print(f"   {exists}")


def main():
    """Run all demos."""
    print("=" * 60)
    print("  ModelCub SDK Playground")
    print("  Interactive Demo of the Python API")
    print("=" * 60)

    try:
        # 1. Create project
        project = demo_create_project()

        # 2. Config access
        demo_config_access(project)

        # 3. Paths
        demo_paths(project)

        # 4. Registries
        demo_registries(project)

        # 5. Load project
        project = demo_load_project()

        # 6. Check existence
        demo_exists()

        # 7. Context manager
        demo_context_manager(project)

        # 8. set_config
        demo_set_config()

        # 9. Cleanup
        demo_cleanup()

        # Success!
        section("✅ All Demos Complete!")
        print("\nThe SDK is working perfectly!")
        print("\nTry it yourself:")
        print("  from modelcub import Project")
        print("  project = Project.init('my-project')")
        print("  print(project.name)")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

        # Try cleanup anyway
        try:
            if Project.exists("playground-test"):
                p = Project.load("playground-test")
                p.delete(confirm=True)
        except:
            pass


if __name__ == "__main__":
    main()