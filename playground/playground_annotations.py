#!/usr/bin/env python3
"""
ModelCub SDK - Annotation Playground

Tests annotation features in isolated sandbox.
"""
import sys
import os
import shutil
from pathlib import Path
from PIL import Image
import traceback

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from modelcub import Project, Dataset, Box

SANDBOX = Path(__file__).parent / "sandbox_annotations"


def section(title: str, char: str = "="):
    """Print section header."""
    print(f"\n{char * 60}")
    print(f"  {title}")
    print(f"{char * 60}")


def create_sample_images(directory: Path, count: int = 5, prefix: str = "img"):
    """Create sample images for testing."""
    directory.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        img = Image.new("RGB", (640, 480), color=(50 + i*40, 100, 200 - i*30))
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

def test_1_setup_dataset():
    """Test: Setup project and dataset."""
    section("1. Setup Project & Dataset")

    print(">>> project = Project.init('anno-project')")
    project = Project.init("anno-project")

    photos = SANDBOX / "images"
    create_sample_images(photos, count=15, prefix="photo")

    print("\n>>> dataset = project.import_dataset(")
    print("...     source='images',")
    print("...     name='animals',")
    print("...     classes=['cat', 'dog', 'bird']")
    print("... )")

    dataset = project.import_dataset(
        source=photos,
        name="animals",
        classes=["cat", "dog", "bird"]
    )

    print(f"\n✅ Dataset: {dataset.name}")
    print(f"   Images: {dataset.images}")
    print(f"   Classes: {dataset.list_classes()}")

    assert dataset.images == 15

    return project, dataset


def test_2_save_annotations(dataset: Dataset):
    """Test: Save annotations."""
    section("2. Save Annotations")

    print(">>> boxes = [")
    print("...     Box(class_id=0, x=0.5, y=0.5, w=0.2, h=0.3),")
    print("...     Box(class_id=1, x=0.7, y=0.3, w=0.15, h=0.25)")
    print("... ]")
    print(">>> dataset.save_annotation('photo000', boxes)")

    boxes = [
        Box(class_id=0, x=0.5, y=0.5, w=0.2, h=0.3),
        Box(class_id=1, x=0.7, y=0.3, w=0.15, h=0.25)
    ]

    result = dataset.save_annotation("photo000", boxes)

    print(f"\n✅ Saved: {result['boxes_saved']} boxes")
    print(f"   Warnings: {len(result['warnings'])}")

    assert result['boxes_saved'] == 2


def test_3_get_annotation(dataset: Dataset):
    """Test: Retrieve annotation."""
    section("3. Get Annotation")

    print(">>> ann = dataset.get_annotation('photo000')")
    ann = dataset.get_annotation("photo000")

    print(f"\n✅ Image: {ann['image_id']}")
    print(f"   Status: {ann['status']}")
    print(f"   Boxes: {len(ann['boxes'])}")

    for i, box in enumerate(ann['boxes']):
        print(f"     [{i}] class={box['class_id']}, x={box['x']:.2f}, y={box['y']:.2f}, w={box['w']:.2f}, h={box['h']:.2f}")

    assert len(ann['boxes']) == 2
    assert ann['status'] == 'labeled'


def test_4_multiple_annotations(dataset: Dataset):
    """Test: Annotate multiple images."""
    section("4. Multiple Annotations")

    print("Annotating 5 images...")

    for i in range(1, 6):
        boxes = [Box(class_id=i % 3, x=0.5, y=0.5, w=0.15, h=0.2)]
        dataset.save_annotation(f"photo{i:03d}", boxes)
        print(f"  ✓ photo{i:03d}")

    print("\n✅ Annotated 5 more images")


def test_5_annotation_stats(dataset: Dataset):
    """Test: Get statistics."""
    section("5. Annotation Statistics")

    print(">>> stats = dataset.annotation_stats()")
    stats = dataset.annotation_stats()

    print(f"\n✅ Statistics:")
    print(f"   Total images: {stats['total_images']}")
    print(f"   Labeled: {stats['labeled']}")
    print(f"   Unlabeled: {stats['unlabeled']}")
    print(f"   Progress: {stats['progress']:.1%}")
    print(f"   Total boxes: {stats['total_boxes']}")
    print(f"   Avg boxes/image: {stats['avg_boxes_per_image']:.2f}")

    print(f"\n   Class distribution:")
    for cls, count in stats['class_distribution'].items():
        print(f"     {cls}: {count}")

    assert stats['labeled'] == 6
    assert stats['total_boxes'] == 7


def test_6_get_all_annotations(dataset: Dataset):
    """Test: List all annotations."""
    section("6. List All Annotations")

    print(">>> all_anns = dataset.get_annotations()")
    all_anns = dataset.get_annotations()

    labeled = [a for a in all_anns if a['num_boxes'] > 0]
    unlabeled = [a for a in all_anns if a['num_boxes'] == 0]

    print(f"\n✅ Total: {len(all_anns)} images")
    print(f"   Labeled: {len(labeled)}")
    print(f"   Unlabeled: {len(unlabeled)}")

    print("\n   Labeled images:")
    for ann in labeled[:5]:
        print(f"     {ann['image_id']}: {ann['num_boxes']} boxes")


def test_7_delete_box(dataset: Dataset):
    """Test: Delete bounding box."""
    section("7. Delete Bounding Box")

    # Check before
    ann_before = dataset.get_annotation("photo000")
    print(f"Before: {len(ann_before['boxes'])} boxes")

    print("\n>>> dataset.delete_box('photo000', 0)")
    dataset.delete_box("photo000", 0)

    # Check after
    ann_after = dataset.get_annotation("photo000")
    print(f"After: {len(ann_after['boxes'])} boxes")

    print("\n✅ Deleted first box")

    assert len(ann_after['boxes']) == 1


def test_8_overwrite_annotation(dataset: Dataset):
    """Test: Overwrite existing annotation."""
    section("8. Overwrite Annotation")

    new_boxes = [
        Box(class_id=2, x=0.3, y=0.4, w=0.1, h=0.15),
        Box(class_id=2, x=0.6, y=0.6, w=0.12, h=0.18),
        Box(class_id=0, x=0.8, y=0.2, w=0.08, h=0.1)
    ]

    print(">>> dataset.save_annotation('photo000', new_boxes)")
    result = dataset.save_annotation("photo000", new_boxes)

    ann = dataset.get_annotation("photo000")

    print(f"\n✅ Overwrote annotation")
    print(f"   New boxes: {len(ann['boxes'])}")

    assert len(ann['boxes']) == 3


def test_9_validation(dataset: Dataset):
    """Test: Coordinate validation."""
    section("9. Coordinate Validation")

    print("Testing out-of-bounds coordinates...")

    # Out of bounds boxes (should be clamped)
    bad_boxes = [
        Box(class_id=0, x=1.5, y=-0.2, w=0.3, h=0.4),
        Box(class_id=99, x=0.5, y=0.5, w=0.1, h=0.1)  # Invalid class
    ]

    print(">>> dataset.save_annotation('photo010', bad_boxes)")
    result = dataset.save_annotation("photo010", bad_boxes)

    print(f"\n✅ Validation:")
    print(f"   Saved: {result['boxes_saved']}")
    print(f"   Skipped: {result['boxes_skipped']}")
    print(f"   Warnings: {len(result['warnings'])}")

    for warning in result['warnings']:
        print(f"     • {warning}")

    assert result['boxes_saved'] == 1
    assert result['boxes_skipped'] == 1


# ========== Main Runner ==========

def run_all_tests():
    """Run all test functions."""
    tests = [
        test_1_setup_dataset,
        test_2_save_annotations,
        test_3_get_annotation,
        test_4_multiple_annotations,
        test_5_annotation_stats,
        test_6_get_all_annotations,
        test_7_delete_box,
        test_8_overwrite_annotation,
        test_9_validation,
    ]

    results = {"passed": 0, "failed": 0, "errors": []}
    context = {}

    for test_func in tests:
        try:
            if test_func.__name__ == "test_1_setup_dataset":
                project, dataset = test_func()
                context['project'] = project
                context['dataset'] = dataset
            else:
                test_func(context['dataset'])

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
    print("  ModelCub SDK - Annotation Test Suite")
    print("=" * 60)

    try:
        setup_sandbox()
        results = run_all_tests()

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
            print("\nAnnotation SDK is working perfectly!")
            print("\nQuick Start:")
            print("  dataset = project.get_dataset('my-dataset')")
            print("  boxes = [Box(class_id=0, x=0.5, y=0.5, w=0.2, h=0.3)]")
            print("  dataset.save_annotation('img_001', boxes)")
            print("  stats = dataset.annotation_stats()")

    except Exception as e:
        print(f"\n❌ Fatal Error: {e}")
        traceback.print_exc()

    finally:
        cleanup_sandbox()


if __name__ == "__main__":
    main()