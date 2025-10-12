"""
Tests for Dataset SDK.
"""
from pathlib import Path
import pytest
from PIL import Image

from modelcub import Project, Dataset
from modelcub.sdk.dataset import DatasetInfo


def test_dataset_from_images_basic(tmp_path, monkeypatch):
    """Test importing images via SDK."""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    Project.init("test-project", path=".")

    # Create source images
    source = tmp_path / "photos"
    source.mkdir()

    for i in range(5):
        img_path = source / f"img{i}.jpg"
        Image.new("RGB", (100, 100)).save(img_path)

    # Import via SDK
    dataset = Dataset.from_images(source, name="my-photos")

    assert dataset.name == "my-photos"
    assert dataset.images == 5
    assert dataset.status == "unlabeled"


def test_dataset_from_images_auto_name(tmp_path, monkeypatch):
    """Test auto-generated dataset name."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    source = tmp_path / "vacation-pics"
    source.mkdir()

    img_path = source / "img.jpg"
    Image.new("RGB", (50, 50)).save(img_path)

    dataset = Dataset.from_images(source)

    assert "vacation-pics" in dataset.name
    assert dataset.images == 1


def test_dataset_from_images_recursive(tmp_path, monkeypatch):
    """Test recursive import."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    source = tmp_path / "photos"
    source.mkdir()

    # Root level
    Image.new("RGB", (50, 50)).save(source / "root.jpg")

    # Subdirectory
    subdir = source / "sub"
    subdir.mkdir()
    Image.new("RGB", (50, 50)).save(subdir / "sub.jpg")

    dataset = Dataset.from_images(source, name="recursive", recursive=True)

    assert dataset.images == 2


def test_dataset_from_images_symlink(tmp_path, monkeypatch):
    """Test import with symlinks."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    source = tmp_path / "photos"
    source.mkdir()
    Image.new("RGB", (50, 50)).save(source / "img.jpg")

    dataset = Dataset.from_images(source, name="symlink-test", copy=False)

    assert dataset.images == 1

    # Verify symlink
    imported_img = dataset.path / "images" / "unlabeled" / "img.jpg"
    assert imported_img.is_symlink()


def test_dataset_load(tmp_path, monkeypatch):
    """Test loading existing dataset."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    source = tmp_path / "photos"
    source.mkdir()
    Image.new("RGB", (50, 50)).save(source / "img.jpg")

    # Import
    Dataset.from_images(source, name="test-load")

    # Load
    dataset = Dataset.load("test-load")

    assert dataset.name == "test-load"
    assert dataset.images == 1


def test_dataset_properties(tmp_path, monkeypatch):
    """Test dataset properties."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    source = tmp_path / "photos"
    source.mkdir()

    for i in range(3):
        Image.new("RGB", (100, 100)).save(source / f"img{i}.jpg")

    dataset = Dataset.from_images(source, name="props-test")

    assert dataset.name == "props-test"
    assert dataset.images == 3
    assert dataset.status == "unlabeled"
    assert dataset.classes == []
    assert isinstance(dataset.path, Path)
    assert dataset.path.exists()
    assert dataset.id  # Should have an ID
    assert dataset.source  # Should have source path


def test_dataset_info(tmp_path, monkeypatch):
    """Test dataset info method."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    source = tmp_path / "photos"
    source.mkdir()

    for i in range(5):
        Image.new("RGB", (100, 100)).save(source / f"img{i}.jpg")

    dataset = Dataset.from_images(source, name="info-test")

    info = dataset.info()

    assert isinstance(info, DatasetInfo)
    assert info.name == "info-test"
    assert info.total_images == 5
    assert info.unlabeled_images == 5
    assert info.train_images == 0
    assert info.valid_images == 0
    assert info.status == "unlabeled"
    assert info.size_bytes > 0
    assert info.size  # Human-readable size


def test_dataset_list(tmp_path, monkeypatch):
    """Test listing all datasets."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    # Create multiple datasets
    for name in ["dataset1", "dataset2", "dataset3"]:
        source = tmp_path / name
        source.mkdir()
        Image.new("RGB", (50, 50)).save(source / "img.jpg")
        Dataset.from_images(source, name=name)

    datasets = Dataset.list()

    assert len(datasets) == 3
    assert all(isinstance(ds, Dataset) for ds in datasets)
    assert set(ds.name for ds in datasets) == {"dataset1", "dataset2", "dataset3"}


def test_dataset_list_empty(tmp_path, monkeypatch):
    """Test listing when no datasets exist."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    datasets = Dataset.list()

    assert datasets == []


def test_dataset_exists(tmp_path, monkeypatch):
    """Test checking if dataset exists."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    source = tmp_path / "photos"
    source.mkdir()
    Image.new("RGB", (50, 50)).save(source / "img.jpg")

    Dataset.from_images(source, name="exists-test")

    assert Dataset.exists("exists-test") is True
    assert Dataset.exists("nonexistent") is False


def test_dataset_delete(tmp_path, monkeypatch):
    """Test deleting a dataset."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    source = tmp_path / "photos"
    source.mkdir()
    Image.new("RGB", (50, 50)).save(source / "img.jpg")

    dataset = Dataset.from_images(source, name="delete-test")

    assert Dataset.exists("delete-test")

    dataset.delete(confirm=True)

    assert not Dataset.exists("delete-test")


def test_dataset_delete_requires_confirm(tmp_path, monkeypatch):
    """Test that delete requires confirmation."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    source = tmp_path / "photos"
    source.mkdir()
    Image.new("RGB", (50, 50)).save(source / "img.jpg")

    dataset = Dataset.from_images(source, name="delete-test")

    with pytest.raises(ValueError, match="confirm=True"):
        dataset.delete()

    # Dataset should still exist
    assert Dataset.exists("delete-test")


def test_dataset_repr_str(tmp_path, monkeypatch):
    """Test string representations."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    source = tmp_path / "photos"
    source.mkdir()
    Image.new("RGB", (50, 50)).save(source / "img.jpg")

    dataset = Dataset.from_images(source, name="repr-test")

    repr_str = repr(dataset)
    assert "repr-test" in repr_str
    assert "Dataset" in repr_str

    str_str = str(dataset)
    assert str_str == "repr-test"


def test_dataset_load_nonexistent_raises(tmp_path, monkeypatch):
    """Test loading nonexistent dataset raises."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    with pytest.raises(ValueError, match="not found"):
        Dataset.load("nonexistent")


def test_dataset_from_yolo_not_implemented(tmp_path, monkeypatch):
    """Test that YOLO import raises NotImplementedError."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    with pytest.raises(NotImplementedError, match="coming soon"):
        Dataset.from_yolo("./data")


def test_dataset_from_roboflow_not_implemented(tmp_path, monkeypatch):
    """Test that Roboflow import raises NotImplementedError."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    with pytest.raises(NotImplementedError, match="coming soon"):
        Dataset.from_roboflow("export.zip")


def test_dataset_info_repr(tmp_path, monkeypatch):
    """Test DatasetInfo repr."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    source = tmp_path / "photos"
    source.mkdir()
    Image.new("RGB", (50, 50)).save(source / "img.jpg")

    dataset = Dataset.from_images(source, name="info-repr")
    info = dataset.info()

    repr_str = repr(info)
    assert "Dataset" in repr_str
    assert "info-repr" in repr_str
    assert "unlabeled" in repr_str


def test_dataset_from_images_validation_failure(tmp_path, monkeypatch):
    """Test that import fails gracefully with no valid images."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-project")

    source = tmp_path / "empty"
    source.mkdir()

    with pytest.raises(RuntimeError, match="Failed to import"):
        Dataset.from_images(source, name="fail-test")