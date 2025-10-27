"""
Unit tests for training validation.
"""
import pytest
from pathlib import Path
from modelcub.services.training.validation import (
    ValidationError,
    validate_gpu,
    validate_disk_space,
    validate_dataset_structure,
    validate_dataset_has_images,
    validate_dataset_yaml,
    validate_model_name,
    validate_all
)


def test_validate_model_name_valid():
    """Test validation of valid model names."""
    validate_model_name("yolov8n")
    validate_model_name("yolov8s")
    validate_model_name("yolov9c")
    validate_model_name("yolov10m")
    validate_model_name("yolov11x")
    validate_model_name("custom.pt")


def test_validate_model_name_invalid():
    """Test validation fails for invalid model names."""
    with pytest.raises(ValidationError) as exc_info:
        validate_model_name("yolov5n")
    assert exc_info.value.code == "TRAIN_MODEL_INVALID"

    with pytest.raises(ValidationError) as exc_info:
        validate_model_name("invalid-model")
    assert exc_info.value.code == "TRAIN_MODEL_INVALID"


def test_validate_gpu_cpu_device():
    """Test GPU validation passes for CPU device."""
    validate_gpu("cpu")


def test_validate_gpu_cuda_no_torch(monkeypatch):
    """Test GPU validation fails when PyTorch not installed."""
    import builtins
    original_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "torch":
            raise ImportError("No module named 'torch'")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', mock_import)

    with pytest.raises(ValidationError) as exc_info:
        validate_gpu("cuda:0")
    assert exc_info.value.code == "TRAIN_DEVICE_UNAVAILABLE"


def test_validate_disk_space_sufficient(tmp_path):
    """Test disk space validation passes with sufficient space."""
    validate_disk_space(tmp_path, required_gb=0.001)


def test_validate_disk_space_insufficient(tmp_path, monkeypatch):
    """Test disk space validation fails with insufficient space."""
    import shutil

    def mock_disk_usage(path):
        from collections import namedtuple
        DiskUsage = namedtuple('usage', ['total', 'used', 'free'])
        return DiskUsage(total=1000, used=900, free=100)

    monkeypatch.setattr(shutil, 'disk_usage', mock_disk_usage)

    with pytest.raises(ValidationError) as exc_info:
        validate_disk_space(tmp_path, required_gb=1.0)
    assert exc_info.value.code == "TRAIN_DISK_LOW"


def test_validate_dataset_structure_valid(tmp_path):
    """Test dataset structure validation with valid structure."""
    dataset_path = tmp_path / "dataset"
    (dataset_path / "train" / "images").mkdir(parents=True)
    (dataset_path / "valid" / "images").mkdir(parents=True)

    validate_dataset_structure(dataset_path)


def test_validate_dataset_structure_missing_train(tmp_path):
    """Test validation fails when train split missing."""
    dataset_path = tmp_path / "dataset"
    (dataset_path / "valid" / "images").mkdir(parents=True)

    with pytest.raises(ValidationError) as exc_info:
        validate_dataset_structure(dataset_path)
    assert exc_info.value.code == "TRAIN_DATASET_NO_SPLITS"


def test_validate_dataset_structure_missing_valid(tmp_path):
    """Test validation fails when valid split missing."""
    dataset_path = tmp_path / "dataset"
    (dataset_path / "train" / "images").mkdir(parents=True)

    with pytest.raises(ValidationError) as exc_info:
        validate_dataset_structure(dataset_path)
    assert exc_info.value.code == "TRAIN_DATASET_NO_SPLITS"


def test_validate_dataset_has_images_valid(tmp_path):
    """Test image validation with images present."""
    dataset_path = tmp_path / "dataset"
    train_images = dataset_path / "train" / "images"
    valid_images = dataset_path / "valid" / "images"
    train_images.mkdir(parents=True)
    valid_images.mkdir(parents=True)

    (train_images / "img1.jpg").touch()
    (train_images / "img2.jpg").touch()
    (valid_images / "img3.jpg").touch()

    counts = validate_dataset_has_images(dataset_path)
    assert counts['train'] == 2
    assert counts['valid'] == 1


def test_validate_dataset_has_images_no_train(tmp_path):
    """Test validation fails when no training images."""
    dataset_path = tmp_path / "dataset"
    train_images = dataset_path / "train" / "images"
    valid_images = dataset_path / "valid" / "images"
    train_images.mkdir(parents=True)
    valid_images.mkdir(parents=True)

    (valid_images / "img1.jpg").touch()

    with pytest.raises(ValidationError) as exc_info:
        validate_dataset_has_images(dataset_path)
    assert exc_info.value.code == "TRAIN_DATASET_NO_LABELS"


def test_validate_dataset_has_images_no_valid(tmp_path):
    """Test validation fails when no validation images."""
    dataset_path = tmp_path / "dataset"
    train_images = dataset_path / "train" / "images"
    valid_images = dataset_path / "valid" / "images"
    train_images.mkdir(parents=True)
    valid_images.mkdir(parents=True)

    (train_images / "img1.jpg").touch()

    with pytest.raises(ValidationError) as exc_info:
        validate_dataset_has_images(dataset_path)
    assert exc_info.value.code == "TRAIN_DATASET_NO_LABELS"


def test_validate_dataset_yaml_valid(tmp_path):
    """Test dataset.yaml validation with valid file."""
    dataset_path = tmp_path / "dataset"
    dataset_path.mkdir()

    dataset_yaml = dataset_path / "dataset.yaml"
    dataset_yaml.write_text("names: [cat, dog]\nnc: 2")

    validate_dataset_yaml(dataset_path)


def test_validate_dataset_yaml_missing(tmp_path):
    """Test validation fails when dataset.yaml missing."""
    dataset_path = tmp_path / "dataset"
    dataset_path.mkdir()

    with pytest.raises(ValidationError) as exc_info:
        validate_dataset_yaml(dataset_path)
    assert exc_info.value.code == "TRAIN_DATASET_INVALID"


def test_validate_dataset_yaml_empty(tmp_path):
    """Test validation fails when dataset.yaml empty."""
    dataset_path = tmp_path / "dataset"
    dataset_path.mkdir()

    dataset_yaml = dataset_path / "dataset.yaml"
    dataset_yaml.write_text("")

    with pytest.raises(ValidationError) as exc_info:
        validate_dataset_yaml(dataset_path)
    assert exc_info.value.code == "TRAIN_DATASET_INVALID"


def test_validate_dataset_yaml_invalid_format(tmp_path):
    """Test validation fails with invalid YAML."""
    dataset_path = tmp_path / "dataset"
    dataset_path.mkdir()

    dataset_yaml = dataset_path / "dataset.yaml"
    dataset_yaml.write_text("invalid: yaml: syntax:")

    with pytest.raises(ValidationError) as exc_info:
        validate_dataset_yaml(dataset_path)
    assert exc_info.value.code == "TRAIN_DATASET_INVALID"


def test_validate_all_integration(tmp_path):
    """Test validate_all with complete valid dataset."""
    dataset_path = tmp_path / "dataset"
    train_images = dataset_path / "train" / "images"
    valid_images = dataset_path / "valid" / "images"
    train_images.mkdir(parents=True)
    valid_images.mkdir(parents=True)

    (train_images / "img1.jpg").touch()
    (valid_images / "img2.jpg").touch()

    dataset_yaml = dataset_path / "dataset.yaml"
    dataset_yaml.write_text("names: [cat, dog]\nnc: 2")

    counts = validate_all(
        dataset_path=dataset_path,
        model="yolov8n",
        device="cpu",
        project_root=tmp_path
    )

    assert counts['train'] == 1
    assert counts['valid'] == 1


def test_validation_error_has_code():
    """Test ValidationError includes error code."""
    error = ValidationError("Test error", "TEST_CODE")
    assert str(error) == "Test error"
    assert error.code == "TEST_CODE"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])