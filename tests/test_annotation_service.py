import json
from pathlib import Path
import pytest

from modelcub.services.project_service import init_project, InitProjectRequest
from modelcub.services.dataset_service import add_dataset, AddDatasetRequest
from modelcub.services.annotation_service import (
    save_annotation, get_annotation, delete_annotation, get_annotation_stats,
    SaveAnnotationRequest, GetAnnotationRequest, DeleteAnnotationRequest,
    BoundingBox
)

def _init_project():
    code, _ = init_project(InitProjectRequest(path=".", name="test", force=False))
    assert code == 0

def test_save_and_get_annotation(fake_shapes_generator):
    """Test basic save/load cycle"""
    _init_project()

    # Create dataset
    code, _ = add_dataset(AddDatasetRequest(name="test-ds", source="toy-shapes", n=5))
    assert code == 0

    # Save annotation
    boxes = [
        BoundingBox(class_id=0, x=0.5, y=0.5, w=0.2, h=0.3),
        BoundingBox(class_id=1, x=0.7, y=0.3, w=0.15, h=0.25)
    ]

    req = SaveAnnotationRequest(dataset_name="test-ds", image_id="img_00000", boxes=boxes)
    code, msg = save_annotation(req)
    assert code == 0

    result = json.loads(msg)
    assert result["boxes_saved"] == 2

    # Verify label file created
    label_file = Path("data/datasets/test-ds/train/img_00000.txt")
    assert label_file.exists()

    # Get annotation back
    get_req = GetAnnotationRequest(dataset_name="test-ds", image_id="img_00000")
    code, msg = get_annotation(get_req)
    assert code == 0

    annotation = json.loads(msg)
    assert annotation["image_id"] == "img_00000"
    assert len(annotation["boxes"]) == 2
    assert annotation["status"] == "labeled"

def test_annotation_validation(fake_shapes_generator):
    """Test coordinate clamping and class validation"""
    _init_project()
    code, _ = add_dataset(AddDatasetRequest(name="test-ds", source="toy-shapes", n=5))

    # Out of bounds coordinates (should clamp)
    boxes = [
        BoundingBox(class_id=0, x=1.5, y=-0.2, w=0.3, h=0.4),  # Out of bounds
        BoundingBox(class_id=99, x=0.5, y=0.5, w=0.1, h=0.1),  # Invalid class
    ]

    req = SaveAnnotationRequest(dataset_name="test-ds", image_id="img_00000", boxes=boxes)
    code, msg = save_annotation(req)
    assert code == 0

    result = json.loads(msg)
    assert result["boxes_saved"] == 1  # Only first box (clamped)
    assert result["boxes_skipped"] == 1  # Second box (invalid class)
    assert len(result["warnings"]) >= 1

def test_delete_annotation_box(fake_shapes_generator):
    """Test deleting single box"""
    _init_project()
    code, _ = add_dataset(AddDatasetRequest(name="test-ds", source="toy-shapes", n=5))

    # Create annotation with 2 boxes
    boxes = [
        BoundingBox(class_id=0, x=0.3, y=0.3, w=0.1, h=0.1),
        BoundingBox(class_id=0, x=0.7, y=0.7, w=0.1, h=0.1)
    ]
    save_annotation(SaveAnnotationRequest("test-ds", "img_00000", boxes))

    # Delete first box
    del_req = DeleteAnnotationRequest(dataset_name="test-ds", image_id="img_00000", box_index=0)
    code, msg = delete_annotation(del_req)
    assert code == 0

    # Verify only 1 box remains
    get_req = GetAnnotationRequest(dataset_name="test-ds", image_id="img_00000")
    code, msg = get_annotation(get_req)
    annotation = json.loads(msg)
    assert len(annotation["boxes"]) == 1

def test_annotation_stats(fake_shapes_generator):
    """Test statistics calculation"""
    _init_project()
    code, _ = add_dataset(AddDatasetRequest(name="test-ds", source="toy-shapes", n=10))

    # Annotate 3 images
    for i in range(3):
        boxes = [BoundingBox(class_id=0, x=0.5, y=0.5, w=0.2, h=0.2)]
        save_annotation(SaveAnnotationRequest("test-ds", f"img_0000{i}", boxes))

    # Get stats
    code, msg = get_annotation_stats("test-ds")
    assert code == 0

    stats = json.loads(msg)
    assert stats["total_images"] >= 8  # Should have ~8 in train split
    assert stats["labeled"] == 3
    assert stats["total_boxes"] == 3
    assert 0 < stats["progress"] < 1

def test_annotation_events(fake_shapes_generator, subscribe_events):
    """Test event publishing"""
    _init_project()
    code, _ = add_dataset(AddDatasetRequest(name="test-ds", source="toy-shapes", n=5))

    boxes = [BoundingBox(class_id=0, x=0.5, y=0.5, w=0.2, h=0.2)]
    save_annotation(SaveAnnotationRequest("test-ds", "img_00000", boxes))

    # Check event was published
    event_names = [type(e).__name__ for e in subscribe_events]
    assert "AnnotationSaved" in event_names