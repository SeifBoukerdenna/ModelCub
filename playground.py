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
from PIL import Image

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modelcub import Project, Dataset


def section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def demo_create_project():
    """Demo: Create a new project."""
    section("1. Creating a New Project")

    print("\n>>> from modelcub import Project, Dataset")
    print(">>> project = Project.init('modelcub-demo-sdk')")

    project = Project.init("modelcub-demo-sdk")

    # Change into project directory
    import os
    os.chdir(project.path)

    print(f"\n✅ Created: {project}")
    print(f"   Path: {project.path}")
    print(f"   Name: {project.name}")
    print(f"   Created: {project.created}")
    print(f"   Version: {project.version}")

    return project


def demo_import_images(project: Project):
    """Demo: Import images into a dataset."""
    section("2. Importing Images")

    # Create sample images
    photos_dir = Path("sample-photos")
    photos_dir.mkdir(exist_ok=True)

    print("\n# Creating sample images...")
    for i in range(5):
        img_path = photos_dir / f"photo{i}.jpg"
        img = Image.new("RGB", (200, 200), color=(100 + i*30, 150, 200))
        img.save(img_path)

    print(">>> dataset = Dataset.from_images('sample-photos', name='my-photos')")
    dataset = Dataset.from_images(photos_dir, name="my-photos")

    print(f"\n✅ Imported: {dataset}")
    print(f"   Name: {dataset.name}")
    print(f"   Images: {dataset.images}")
    print(f"   Status: {dataset.status}")

    return dataset


def demo_dataset_properties(dataset: Dataset):
    """Demo: Access dataset properties."""
    section("3. Dataset Properties")

    print("\n>>> dataset.name")
    print(f"   {dataset.name}")

    print("\n>>> dataset.images")
    print(f"   {dataset.images}")

    print("\n>>> dataset.status")
    print(f"   {dataset.status}")

    print("\n>>> dataset.classes")
    print(f"   {dataset.classes}")

    print("\n>>> dataset.id")
    print(f"   {dataset.id}")

    print("\n>>> dataset.path")
    print(f"   {dataset.path}")


def demo_dataset_info(dataset: Dataset):
    """Demo: Get detailed dataset info."""
    section("4. Dataset Info")

    print("\n>>> info = dataset.info()")
    info = dataset.info()

    print(f"\n   Name: {info.name}")
    print(f"   Total images: {info.total_images}")
    print(f"   Unlabeled: {info.unlabeled_images}")
    print(f"   Status: {info.status}")
    print(f"   Size: {info.size}")
    print(f"   Path: {info.path}")


def demo_import_recursive():
    """Demo: Import with subdirectories."""
    section("5. Recursive Import")

    # Create nested structure
    nested_dir = Path("nested-photos")
    nested_dir.mkdir(exist_ok=True)

    for folder in ["cats", "dogs"]:
        subdir = nested_dir / folder
        subdir.mkdir(exist_ok=True)
        for i in range(3):
            img_path = subdir / f"{folder}{i}.jpg"
            Image.new("RGB", (150, 150)).save(img_path)

    print("\n>>> dataset = Dataset.from_images(")
    print("...     'nested-photos',")
    print("...     name='animals',")
    print("...     recursive=True")
    print("... )")

    dataset = Dataset.from_images(
        nested_dir,
        name="animals",
        recursive=True
    )

    print(f"\n✅ Imported: {dataset.name}")
    print(f"   Images: {dataset.images} (from subdirectories)")

    return dataset


def demo_list_datasets():
    """Demo: List all datasets."""
    section("6. Listing Datasets")

    print("\n>>> datasets = Dataset.list()")
    datasets = Dataset.list()

    print(f"\n   Found {len(datasets)} datasets:")
    for ds in datasets:
        print(f"   • {ds.name}: {ds.images} images ({ds.status})")


def demo_load_dataset():
    """Demo: Load existing dataset."""
    section("7. Loading Existing Dataset")

    print("\n>>> dataset = Dataset.load('my-photos')")
    dataset = Dataset.load("my-photos")

    print(f"\n✅ Loaded: {dataset}")
    print(f"   Images: {dataset.images}")

    return dataset


def demo_dataset_exists():
    """Demo: Check if dataset exists."""
    section("8. Checking Dataset Existence")

    print("\n>>> Dataset.exists('my-photos')")
    exists = Dataset.exists("my-photos")
    print(f"   {exists}")

    print("\n>>> Dataset.exists('nonexistent')")
    exists = Dataset.exists("nonexistent")
    print(f"   {exists}")


def demo_import_auto_name():
    """Demo: Import with auto-generated name."""
    section("9. Auto-Generated Names")

    # Create another folder
    auto_dir = Path("vacation-pics")
    auto_dir.mkdir(exist_ok=True)

    for i in range(3):
        img_path = auto_dir / f"pic{i}.jpg"
        Image.new("RGB", (100, 100)).save(img_path)

    print("\n>>> dataset = Dataset.from_images('vacation-pics')")
    print("# Name will be auto-generated")

    dataset = Dataset.from_images(auto_dir)

    print(f"\n✅ Auto-named: {dataset.name}")

    return dataset


def demo_config_access(project: Project):
    """Demo: Access and modify config."""
    section("10. Project Configuration")

    print("\n>>> project.config.defaults.device")
    print(f"   {project.config.defaults.device}")

    print("\n>>> project.config.defaults.batch_size = 32")
    project.config.defaults.batch_size = 32
    project.save_config()

    print("✅ Config updated")


def demo_cleanup():
    """Demo: Delete everything."""
    section("11. Cleanup")

    print("\n# Deleting all datasets...")
    for dataset in Dataset.list():
        print(f">>> Dataset.load('{dataset.name}').delete(confirm=True)")
        dataset.delete(confirm=True)

    print("\n# Deleting sample folders...")
    import shutil
    for folder in ["sample-photos", "nested-photos", "vacation-pics"]:
        if Path(folder).exists():
            shutil.rmtree(folder)

    print("\n# Deleting project...")
    print(">>> project = Project.load('.')")
    project = Project.load(".")
    print(">>> project.delete(confirm=True)")
    project.delete(confirm=True)

    print("\n✅ Cleanup complete!")


def main():
    """Run all demos."""
    print("=" * 60)
    print("  ModelCub SDK Playground")
    print("  Interactive Demo of the Python API")
    print("=" * 60)

    try:
        # Project demos
        project = demo_create_project()

        # Dataset demos
        dataset = demo_import_images(project)
        demo_dataset_properties(dataset)
        demo_dataset_info(dataset)
        demo_import_recursive()
        demo_list_datasets()
        dataset = demo_load_dataset()
        demo_dataset_exists()
        demo_import_auto_name()

        # Config demo
        demo_config_access(project)

        # Cleanup
        demo_cleanup()

        # Success!
        section("✅ All Demos Complete!")
        print("\nThe SDK is working perfectly!")
        print("\nTry it yourself:")
        print("  from modelcub import Project, Dataset")
        print("  project = Project.init('my-project', path='.')")
        print("  dataset = Dataset.from_images('./photos', name='my-data')")
        print("  print(dataset.info())")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

        # Try cleanup anyway
        try:
            import shutil
            import os

            # Try to change to project dir if exists
            project_dir = Path("modelcub-demo-sdk")
            if project_dir.exists():
                os.chdir(project_dir)

                # Clean up sample folders
                for folder in ["sample-photos", "nested-photos", "vacation-pics"]:
                    if Path(folder).exists():
                        shutil.rmtree(folder)

                # Delete project
                if Project.exists("."):
                    p = Project.load(".")
                    p.delete(confirm=True)

                # Go back and remove project directory
                os.chdir("..")
        except:
            pass


if __name__ == "__main__":
    main()