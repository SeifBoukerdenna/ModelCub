#!/usr/bin/env python3
"""
ModelCub SDK Comprehensive Playground

Self-contained test suite for all SDK features.
Runs in isolated sandbox that is cleaned up automatically.
"""
import sys
import os
import shutil
from pathlib import Path
from PIL import Image
import traceback

# Add parent src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modelcub import Project, Dataset

# Sandbox directory
SANDBOX = Path(__file__).parent / "sandbox"


def section(title: str, char: str = "="):
    """Print section header."""
    print(f"\n{char * 60}")
    print(f"  {title}")
    print(f"{char * 60}")


def create_sample_images(directory: Path, count: int = 5, prefix: str = "img"):
    """Create sample images for testing."""
    directory.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        img = Image.new("RGB", (200, 200), color=(50 + i*40, 100, 200 - i*30))
        img.save(directory / f"{prefix}{i:03d}.jpg")


def setup_sandbox():
    """Create sandbox directory."""
    section("Setup: Creating Sandbox", "-")
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    SANDBOX.mkdir(parents=True)
    os.chdir(SANDBOX)
    print(f"✅ Sandbox: {SANDBOX}")


def cleanup_sandbox():
    """Remove sandbox directory."""
    section("Cleanup: Removing Sandbox", "-")
    os.chdir(SANDBOX.parent)
    if SANDBOX.exists():
        shutil.rmtree(SANDBOX)
    print("✅ Sandbox removed")


# ========== Test Functions ==========

def test_1_create_project():
    """Test: Create a new project."""
    section("1. Project Creation")

    print(">>> project = Project.init('test-project')")
    project = Project.init("test-project")

    print(f"\n✅ Created: {project.name}")
    print(f"   Path: {project.path}")
    print(f"   Created: {project.created}")
    print(f"   Version: {project.version}")

    assert project.name == "test-project"
    assert (project.path / ".modelcub").exists()

    return project


def test_2_import_with_classes(project: Project):
    """Test: Import dataset with classes."""
    section("2. Import Dataset with Classes")

    # Create images
    photos = SANDBOX / "photos"
    create_sample_images(photos, count=10, prefix="photo")

    print(">>> dataset = project.import_dataset(")
    print("...     source='photos',")
    print("...     name='animals',")
    print("...     classes=['cat', 'dog', 'bird']")
    print("... )")

    dataset = project.import_dataset(
        source=photos,
        name="animals",
        classes=["cat", "dog", "bird"]
    )

    classes = dataset.list_classes()

    print(f"\n✅ Imported: {dataset.name}")
    print(f"   Images: {dataset.images}")
    print(f"   Classes: {classes}")

    assert dataset.images == 10
    assert classes == ["cat", "dog", "bird"]

    return dataset


def test_3_class_operations(dataset: Dataset):
    """Test: Add, rename, remove classes."""
    section("3. Class Management Operations")

    # Add class
    print(">>> dataset.add_class('fish')")
    class_id = dataset.add_class('fish')
    print(f"   ✅ Added at ID {class_id}")

    # Add with specific ID
    print("\n>>> dataset.add_class('horse', class_id=10)")
    class_id = dataset.add_class('horse', class_id=10)
    print(f"   ✅ Added at ID {class_id}")

    # Rename
    print("\n>>> dataset.rename_class('bird', 'parrot')")
    dataset.rename_class('bird', 'parrot')
    print("   ✅ Renamed")

    # Remove
    print("\n>>> dataset.remove_class('dog')")
    dataset.remove_class('dog')
    print("   ✅ Removed")

    classes = dataset.list_classes()
    print(f"\n✅ Final classes: {classes}")

    assert 'parrot' in classes
    assert 'fish' in classes
    assert 'horse' in classes
    assert 'dog' not in classes
    assert 'bird' not in classes


def test_4_multiple_datasets(project: Project):
    """Test: Import multiple datasets."""
    section("4. Multiple Datasets")

    # Dataset 1
    photos1 = SANDBOX / "cats"
    create_sample_images(photos1, count=5, prefix="cat")

    ds1 = project.import_dataset(
        source=photos1,
        name="cats-only",
        classes=["cat"]
    )
    print(f"✅ Dataset 1: {ds1.name} ({ds1.images} images)")

    # Dataset 2
    photos2 = SANDBOX / "dogs"
    create_sample_images(photos2, count=7, prefix="dog")

    ds2 = project.import_dataset(
        source=photos2,
        name="dogs-only",
        classes=["dog", "puppy"]
    )
    print(f"✅ Dataset 2: {ds2.name} ({ds2.images} images)")

    # List all
    print("\n>>> project.list_datasets()")
    all_datasets = project.list_datasets()

    print(f"\n✅ Total datasets: {len(all_datasets)}")
    for ds in all_datasets:
        print(f"   • {ds.name}: {ds.images} images, {len(ds.list_classes())} classes")

    assert len(all_datasets) == 3  # animals, cats-only, dogs-only


def test_5_load_operations(project: Project):
    """Test: Load and access datasets."""
    section("5. Load Operations")

    # Get specific dataset
    print(">>> dataset = project.get_dataset('animals')")
    dataset = project.get_dataset('animals')
    print(f"✅ Loaded: {dataset.name}")

    # Access properties
    print(f"\n>>> dataset.images = {dataset.images}")
    print(f">>> dataset.status = {dataset.status}")
    print(f">>> dataset.classes = {dataset.list_classes()}")

    # Get info
    info = dataset.info()
    print(f"\n✅ Dataset info:")
    print(f"   Total: {info.total_images}")
    print(f"   Size: {info.size}")
    print(f"   Status: {info.status}")


def test_6_config_management(project: Project):
    """Test: Config access and modification."""
    section("6. Configuration")

    print(f">>> project.config.defaults.device")
    print(f"   {project.config.defaults.device}")

    print(f"\n>>> project.config.defaults.batch_size")
    print(f"   {project.config.defaults.batch_size}")

    print("\n>>> project.config.defaults.batch_size = 64")
    project.config.defaults.batch_size = 64

    print(">>> project.save_config()")
    project.save_config()

    # Reload to verify
    project2 = Project.load(project.path)
    assert project2.config.defaults.batch_size == 64

    print("✅ Config saved and verified")


def test_7_import_without_classes(project: Project):
    """Test: Import without specifying classes."""
    section("7. Import Without Classes")

    photos = SANDBOX / "unlabeled"
    create_sample_images(photos, count=3, prefix="unk")

    print(">>> dataset = project.import_dataset(")
    print("...     source='unlabeled',")
    print("...     name='unlabeled-data'")
    print("... )")

    dataset = project.import_dataset(
        source=photos,
        name="unlabeled-data",
    )

    classes = dataset.list_classes()

    print(f"✅ Imported: {dataset.name}")
    print(f"   Classes: {classes}")

    assert classes == []

    # Add classes later
    print("\n>>> dataset.add_class('unknown')")
    dataset.add_class('unknown')

    classes = dataset.list_classes()
    print(f"✅ Classes now: {classes}")

    assert classes == ['unknown']


def test_8_recursive_import(project: Project):
    """Test: Recursive directory import."""
    section("8. Recursive Import")

    # Create nested structure
    base = SANDBOX / "nested"
    (base / "folder1").mkdir(parents=True)
    (base / "folder2").mkdir(parents=True)
    create_sample_images(base / "folder1", count=3)
    create_sample_images(base / "folder2", count=4)

    print(">>> dataset = project.import_dataset(")
    print("...     source='nested',")
    print("...     name='nested-data',")
    print("...     recursive=True")
    print("... )")

    dataset = project.import_dataset(
        source=base,
        name="nested-data",
        recursive=True
    )

    print(f"✅ Imported: {dataset.images} images from subdirectories")
    assert dataset.images == 7


def test_9_dataset_deletion(project: Project):
    """Test: Delete datasets."""
    section("9. Dataset Deletion")

    initial_count = len(project.list_datasets())

    print(">>> dataset = project.get_dataset('nested-data')")
    dataset = project.get_dataset('nested-data')

    print(">>> dataset.delete(confirm=True)")
    dataset.delete(confirm=True)

    final_count = len(project.list_datasets())

    print(f"✅ Deleted dataset")
    print(f"   Before: {initial_count} datasets")
    print(f"   After: {final_count} datasets")

    assert final_count == initial_count - 1

# ========== Main Runner ==========

def run_all_tests():
    """Run all test functions."""
    tests = [
        test_1_create_project,
        test_2_import_with_classes,
        test_3_class_operations,
        test_4_multiple_datasets,
        test_5_load_operations,
        test_6_config_management,
        test_7_import_without_classes,
        test_8_recursive_import,
        test_9_dataset_deletion,
        # test_10_project_deletion,
    ]

    results = {"passed": 0, "failed": 0, "errors": []}
    context = {}

    for test_func in tests:
        try:
            # Pass context from previous tests
            if test_func.__name__.startswith("test_1"):
                result = test_func()
                if result:
                    context['project'] = result
            elif test_func.__name__.startswith("test_2"):
                result = test_func(context['project'])
                if result:
                    context['dataset'] = result
            elif test_func.__name__.startswith("test_3"):
                test_func(context['dataset'])
            elif test_func.__name__ in ["test_4_multiple_datasets", "test_5_load_operations",
                                       "test_6_config_management", "test_7_import_without_classes",
                                       "test_8_recursive_import", "test_9_dataset_deletion"]:
                test_func(context['project'])
            else:
                test_func()

            results["passed"] += 1
            print(f"✅ PASSED")

        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "test": test_func.__name__,
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            print(f"❌ FAILED: {e}")

    return results


def main():
    """Main entry point."""
    print("=" * 60)
    print("  ModelCub SDK - Comprehensive Test Suite")
    print("=" * 60)

    try:
        setup_sandbox()
        results = run_all_tests()

        # Summary
        section("Test Summary")
        print(f"✅ Passed: {results['passed']}")
        print(f"❌ Failed: {results['failed']}")

        if results['errors']:
            print("\nErrors:")
            for err in results['errors']:
                print(f"\n{err['test']}:")
                print(f"  {err['error']}")

        if results['failed'] == 0:
            section("🎉 All Tests Passed! 🎉")
            print("\nThe SDK is working perfectly!")
            print("\nQuick Start:")
            print("  project = Project.init('my-project')")
            print("  dataset = project.import_dataset(")
            print("      source='./photos',")
            print("      classes=['cat', 'dog']")
            print("  )")
            print("  dataset.rename_class('cat', 'feline')")

    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        traceback.print_exc()

    finally:
        cleanup_sandbox()


if __name__ == "__main__":
    main()