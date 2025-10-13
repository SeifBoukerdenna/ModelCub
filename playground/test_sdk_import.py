#!/usr/bin/env python3
"""
Simple SDK test: Create project and import dataset with classes.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from modelcub import Project

def test_import_with_classes():
    """Test importing dataset with classes via SDK."""

    print("=" * 60)
    print("  SDK Import Test with Classes")
    print("=" * 60)

    # 1. Create test project
    print("\n1. Creating project...")
    project = Project.init("sdk-test-project", force=True)
    print(f"   ✓ Created: {project.name}")

    # 2. Import dataset with classes
    print("\n2. Importing dataset with classes...")

    source_path = Path.home() / "Downloads" / "data"
    if not source_path.exists():
        print(f"   ✗ Source path not found: {source_path}")
        print("   Please update source_path in the script")
        return

    classes = ["a", "b", "c", "d"]
    print(f"   Source: {source_path}")
    print(f"   Classes: {classes}")

    dataset = project.import_dataset(
        source=str(source_path),
        name="test-dataset",
        classes=classes,
        recursive=True,
        copy=True,
        validate=True
    )

    print(f"   ✓ Imported: {dataset.name}")
    print(f"   ✓ Images: {dataset.images}")

    # 3. Verify classes
    print("\n3. Verifying classes...")
    stored_classes = dataset.list_classes()
    print(f"   Stored classes: {stored_classes}")

    if stored_classes == classes:
        print("   ✓ Classes match!")
    else:
        print(f"   ✗ Mismatch! Expected: {classes}, Got: {stored_classes}")

    # 4. Check dataset.yaml
    print("\n4. Checking dataset.yaml...")
    dataset_yaml = dataset.path / "dataset.yaml"
    if dataset_yaml.exists():
        import yaml
        with open(dataset_yaml) as f:
            config = yaml.safe_load(f)
        print(f"   names: {config.get('names')}")
        print(f"   nc: {config.get('nc')}")
    else:
        print("   ✗ dataset.yaml not found")

    # 5. Check manifest.json
    print("\n5. Checking manifest.json...")
    manifest_json = dataset.path / "manifest.json"
    if manifest_json.exists():
        import json
        with open(manifest_json) as f:
            manifest = json.load(f)
        print(f"   classes: {manifest.get('classes')}")
    else:
        print("   ✗ manifest.json not found")

    # 6. Check registry
    print("\n6. Checking registry...")
    registry_data = project.datasets.get_dataset(dataset.name)
    print(f"   classes: {registry_data.get('classes')}")
    print(f"   num_classes: {registry_data.get('num_classes')}")

    print("\n" + "=" * 60)
    print("  Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_import_with_classes()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()