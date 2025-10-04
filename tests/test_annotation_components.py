# tests/test_annotation_components.py
"""
Example tests demonstrating how to test the decoupled annotation components.
"""
import pytest
from pathlib import Path
from modelcub.services.annotation.models import Annotation, ImageAnnotation, ImageInfo
from modelcub.services.annotation.storage import AnnotationStorage
from modelcub.services.annotation.image_handler import ImageHandler
from modelcub.services.annotation.exporters import YOLOExporter, COCOExporter


def test_annotation_model_serialization():
    """Test Annotation model to_dict and from_dict."""
    ann = Annotation(
        id='ann_1',
        type='bbox',
        label='cat',
        points=[[10, 20], [30, 40]],
        confidence=0.95
    )

    # Serialize
    data = ann.to_dict()
    assert data['id'] == 'ann_1'
    assert data['type'] == 'bbox'
    assert data['label'] == 'cat'

    # Deserialize
    ann2 = Annotation.from_dict(data)
    assert ann2.id == ann.id
    assert ann2.type == ann.type
    assert ann2.label == ann.label
    assert ann2.points == ann.points


def test_image_annotation_model():
    """Test ImageAnnotation model."""
    annotations = [
        Annotation('1', 'bbox', 'cat', [[0, 0], [10, 10]]),
        Annotation('2', 'bbox', 'dog', [[20, 20], [30, 30]])
    ]

    img_ann = ImageAnnotation(
        image_path='/path/to/img.jpg',
        image_id='img_1',
        width=640,
        height=480,
        annotations=annotations,
        timestamp='2025-01-01T00:00:00'
    )

    # Test serialization
    data = img_ann.to_dict()
    assert len(data['annotations']) == 2

    # Test deserialization
    img_ann2 = ImageAnnotation.from_dict(data)
    assert len(img_ann2.annotations) == 2
    assert img_ann2.image_id == 'img_1'


def test_annotation_storage(tmp_path):
    """Test AnnotationStorage component."""
    storage = AnnotationStorage(tmp_path)

    # Create test annotation
    ann = Annotation('1', 'bbox', 'cat', [[0, 0], [10, 10]])
    img_ann = ImageAnnotation(
        image_path='/test/img.jpg',
        image_id='img_1',
        width=640,
        height=480,
        annotations=[ann],
        timestamp='2025-01-01T00:00:00'
    )

    # Test save
    annotations = {'img_1': img_ann}
    storage.save_all(annotations)

    # Verify file exists
    assert (tmp_path / 'annotations.json').exists()

    # Test load
    loaded = storage.load_all()
    assert 'img_1' in loaded
    assert loaded['img_1'].image_id == 'img_1'
    assert len(loaded['img_1'].annotations) == 1


def test_image_handler(tmp_path):
    """Test ImageHandler component."""
    # Create test images
    img_dir = tmp_path / 'images'
    img_dir.mkdir()
    (img_dir / 'cat.jpg').write_bytes(b'fake_image')
    (img_dir / 'dog.png').write_bytes(b'fake_image')

    subdir = img_dir / 'subdir'
    subdir.mkdir()
    (subdir / 'bird.jpg').write_bytes(b'fake_image')

    handler = ImageHandler(img_dir)

    # Test discovery
    images = handler.discover_images({})
    assert len(images) == 3

    # Test find by ID
    img = handler.find_image_by_id('cat.jpg', images)
    assert img is not None
    assert img.name == 'cat.jpg'

    # Test annotation status update
    handler.update_annotation_status('cat.jpg', True, images)
    img = handler.find_image_by_id('cat.jpg', images)
    assert img.has_annotations is True


def test_yolo_exporter():
    """Test YOLO exporter."""
    classes = ['cat', 'dog']
    exporter = YOLOExporter(classes)

    # Create test annotations
    ann1 = Annotation('1', 'bbox', 'cat', [[100, 100], [200, 200]])
    ann2 = Annotation('2', 'bbox', 'dog', [[300, 300], [400, 400]])

    img_ann = ImageAnnotation(
        image_path='/test/img.jpg',
        image_id='img_1',
        width=640,
        height=480,
        annotations=[ann1, ann2],
        timestamp='2025-01-01'
    )

    # Export
    result = exporter.export({'img_1': img_ann})

    # Verify format
    assert 'img_1' in result
    lines = result.strip().split('\n')
    # Should have comment line + 2 annotation lines
    assert len([l for l in lines if l and not l.startswith('#')]) == 2

    # First annotation should be class 0 (cat)
    first_line = [l for l in lines if l and not l.startswith('#')][0]
    assert first_line.startswith('0 ')


def test_coco_exporter():
    """Test COCO exporter."""
    classes = ['cat', 'dog']
    exporter = COCOExporter(classes)

    # Create test annotation
    ann = Annotation('1', 'bbox', 'cat', [[100, 100], [200, 200]])
    img_ann = ImageAnnotation(
        image_path='/test/img.jpg',
        image_id='img_1',
        width=640,
        height=480,
        annotations=[ann],
        timestamp='2025-01-01'
    )

    # Export
    result = exporter.export({'img_1': img_ann})

    # Verify COCO structure
    assert 'images' in result
    assert 'annotations' in result
    assert 'categories' in result
    assert len(result['images']) == 1
    assert len(result['annotations']) == 1
    assert len(result['categories']) == 2


def test_image_info_model():
    """Test ImageInfo model."""
    info = ImageInfo(
        id='subdir/image.jpg',
        path='/full/path/to/image.jpg',
        name='image.jpg',
        relative_path='subdir/image.jpg',
        has_annotations=True
    )

    # Test serialization
    data = info.to_dict()
    assert data['id'] == 'subdir/image.jpg'
    assert data['has_annotations'] is True


def test_annotation_storage_empty_dir(tmp_path):
    """Test storage with non-existent annotations file."""
    storage = AnnotationStorage(tmp_path)

    # Load from empty directory
    annotations = storage.load_all()
    assert annotations == {}


def test_annotation_storage_save_one(tmp_path):
    """Test saving single annotation."""
    storage = AnnotationStorage(tmp_path)
    annotations = {}

    # Create and save one annotation
    ann = Annotation('1', 'bbox', 'cat', [[0, 0], [10, 10]])
    img_ann = ImageAnnotation(
        image_path='/test/img.jpg',
        image_id='img_1',
        width=640,
        height=480,
        annotations=[ann],
        timestamp='2025-01-01'
    )

    storage.save_one('img_1', img_ann, annotations)

    # Verify it's in the dict and saved to disk
    assert 'img_1' in annotations

    loaded = storage.load_all()
    assert 'img_1' in loaded


def test_image_handler_no_images(tmp_path):
    """Test image handler with empty directory."""
    img_dir = tmp_path / 'empty'
    img_dir.mkdir()

    handler = ImageHandler(img_dir)
    images = handler.discover_images({})

    assert len(images) == 0


def test_yolo_exporter_empty_annotations():
    """Test YOLO export with no annotations."""
    exporter = YOLOExporter(['cat', 'dog'])
    result = exporter.export({})

    assert result == ''


def test_coco_exporter_empty_annotations():
    """Test COCO export with no annotations."""
    exporter = COCOExporter(['cat', 'dog'])
    result = exporter.export({})

    assert len(result['images']) == 0
    assert len(result['annotations']) == 0
    assert len(result['categories']) == 2  # Categories always present