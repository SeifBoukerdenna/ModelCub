"""
Unit tests for ModelCub registries.

Tests DatasetRegistry, RunRegistry (with training additions), and ModelRegistry.
"""
import pytest
import yaml
import json
import time
import threading
from pathlib import Path
from datetime import datetime


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project structure."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Create directory structure
    (project_root / ".modelcub").mkdir()
    (project_root / "data" / "datasets").mkdir(parents=True)
    (project_root / "models").mkdir()
    (project_root / "runs").mkdir()

    return project_root


@pytest.fixture
def dataset_registry(temp_project):
    """Create DatasetRegistry instance."""
    from modelcub.core.registries import DatasetRegistry
    return DatasetRegistry(temp_project)


@pytest.fixture
def run_registry(temp_project):
    """Create RunRegistry instance."""
    from modelcub.core.registries import RunRegistry
    return RunRegistry(temp_project)


@pytest.fixture
def model_registry(temp_project):
    """Create ModelRegistry instance."""
    from modelcub.core.registries import ModelRegistry
    return ModelRegistry(temp_project)


# ============================================================================
# DatasetRegistry Tests
# ============================================================================

def test_dataset_registry_init(dataset_registry):
    """Test registry initialization."""
    assert dataset_registry.registry_path.exists() is False
    registry = dataset_registry._load_registry()
    assert registry == {"datasets": {}}


def test_add_dataset(dataset_registry):
    """Test adding dataset to registry."""
    dataset_info = {
        "id": "ds-001",
        "name": "test-dataset",
        "num_images": 100,
        "classes": ["cat", "dog"]
    }

    dataset_registry.add_dataset(dataset_info)

    # Verify it was saved
    assert dataset_registry.exists("test-dataset")
    retrieved = dataset_registry.get_dataset("test-dataset")
    assert retrieved["name"] == "test-dataset"
    assert retrieved["num_images"] == 100


def test_list_datasets(dataset_registry):
    """Test listing datasets."""
    dataset_registry.add_dataset({"id": "ds-001", "name": "dataset-1"})
    dataset_registry.add_dataset({"id": "ds-002", "name": "dataset-2"})

    datasets = dataset_registry.list_datasets()
    assert len(datasets) == 2
    assert {d["name"] for d in datasets} == {"dataset-1", "dataset-2"}


def test_remove_dataset(dataset_registry):
    """Test removing dataset."""
    dataset_registry.add_dataset({"id": "ds-001", "name": "test-dataset"})
    assert dataset_registry.exists("test-dataset")

    dataset_registry.remove_dataset("test-dataset")
    assert not dataset_registry.exists("test-dataset")


def test_dataset_not_found(dataset_registry):
    """Test error when dataset doesn't exist."""
    from modelcub.core.exceptions import DatasetNotFoundError

    with pytest.raises(DatasetNotFoundError):
        dataset_registry.get_dataset("nonexistent")


# ============================================================================
# RunRegistry Tests - Basic Operations
# ============================================================================

def test_run_registry_init(run_registry):
    """Test run registry initialization."""
    registry = run_registry._load_registry()
    assert registry == {"runs": {}}


def test_add_run(run_registry):
    """Test adding run to registry."""
    run_info = {
        "id": "run-001",
        "status": "pending",
        "dataset_name": "test-dataset",
        "created": datetime.utcnow().isoformat() + "Z"
    }

    run_registry.add_run(run_info)

    retrieved = run_registry.get_run("run-001")
    assert retrieved is not None
    assert retrieved["status"] == "pending"


def test_update_run(run_registry):
    """Test updating run."""
    run_registry.add_run({
        "id": "run-001",
        "status": "pending",
        "metrics": {}
    })

    run_registry.update_run("run-001", {
        "status": "running",
        "pid": 12345
    })

    run = run_registry.get_run("run-001")
    assert run["status"] == "running"
    assert run["pid"] == 12345


def test_list_runs(run_registry):
    """Test listing runs."""
    run_registry.add_run({"id": "run-001", "status": "pending"})
    run_registry.add_run({"id": "run-002", "status": "running"})

    runs = run_registry.list_runs()
    assert len(runs) == 2
    assert {r["id"] for r in runs} == {"run-001", "run-002"}


def test_remove_run(run_registry):
    """Test removing run."""
    run_registry.add_run({"id": "run-001", "status": "completed"})
    assert run_registry.get_run("run-001") is not None

    run_registry.remove_run("run-001")
    assert run_registry.get_run("run-001") is None


# ============================================================================
# RunRegistry Tests - State Validation
# ============================================================================

def test_valid_state_transition_pending_to_running(run_registry):
    """Test valid transition: pending → running."""
    run_registry.add_run({"id": "run-001", "status": "pending"})

    # Should not raise
    run_registry.update_run("run-001", {"status": "running"})
    assert run_registry.get_run("run-001")["status"] == "running"


def test_valid_state_transition_running_to_completed(run_registry):
    """Test valid transition: running → completed."""
    run_registry.add_run({"id": "run-001", "status": "running"})

    run_registry.update_run("run-001", {"status": "completed"})
    assert run_registry.get_run("run-001")["status"] == "completed"


def test_valid_state_transition_running_to_failed(run_registry):
    """Test valid transition: running → failed."""
    run_registry.add_run({"id": "run-001", "status": "running"})

    run_registry.update_run("run-001", {"status": "failed"})
    assert run_registry.get_run("run-001")["status"] == "failed"


def test_valid_state_transition_pending_to_cancelled(run_registry):
    """Test valid transition: pending → cancelled."""
    run_registry.add_run({"id": "run-001", "status": "pending"})

    run_registry.update_run("run-001", {"status": "cancelled"})
    assert run_registry.get_run("run-001")["status"] == "cancelled"


def test_invalid_state_transition_completed_to_running(run_registry):
    """Test invalid transition: completed → running."""
    run_registry.add_run({"id": "run-001", "status": "completed"})

    with pytest.raises(ValueError, match="Invalid status transition"):
        run_registry.update_run("run-001", {"status": "running"})


def test_invalid_state_transition_pending_to_completed(run_registry):
    """Test invalid transition: pending → completed."""
    run_registry.add_run({"id": "run-001", "status": "pending"})

    with pytest.raises(ValueError, match="Invalid status transition"):
        run_registry.update_run("run-001", {"status": "completed"})


def test_invalid_state_transition_failed_to_running(run_registry):
    """Test invalid transition: failed → running."""
    run_registry.add_run({"id": "run-001", "status": "failed"})

    with pytest.raises(ValueError, match="Invalid status transition"):
        run_registry.update_run("run-001", {"status": "running"})


def test_update_non_status_fields_no_validation(run_registry):
    """Test updating non-status fields doesn't trigger validation."""
    run_registry.add_run({"id": "run-001", "status": "running"})

    # Should not raise even though status isn't changing
    run_registry.update_run("run-001", {
        "pid": 12345,
        "metrics": {"map50": 0.85}
    })

    run = run_registry.get_run("run-001")
    assert run["pid"] == 12345
    assert run["metrics"]["map50"] == 0.85


# ============================================================================
# RunRegistry Tests - Atomic Operations
# ============================================================================

def test_atomic_write_creates_lock_file(run_registry, temp_project):
    """Test that atomic write uses lock file."""
    run_registry.add_run({"id": "run-001", "status": "pending"})

    # Lock file should not exist after operation
    lock_file = temp_project / ".modelcub" / ".runs.yaml.lock"
    assert not lock_file.exists()


def test_concurrent_writes_are_serialized(run_registry, temp_project):
    """Test that concurrent writes don't corrupt registry."""
    results = []
    errors = []

    def add_runs(start_id, count):
        try:
            for i in range(count):
                run_id = f"run-{start_id + i:03d}"
                run_registry.add_run({
                    "id": run_id,
                    "status": "pending",
                    "thread": threading.current_thread().name
                })
            results.append("success")
        except Exception as e:
            errors.append(str(e))

    # Create multiple threads adding runs concurrently
    threads = []
    for i in range(5):
        t = threading.Thread(target=add_runs, args=(i * 10, 10))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Verify no errors
    assert len(errors) == 0

    # Verify all runs were added
    runs = run_registry.list_runs()
    assert len(runs) == 50


def test_file_lock_timeout(run_registry, temp_project):
    """Test that file lock times out if held too long."""
    from modelcub.core.io import FileLock

    lock_path = run_registry.registry_path

    # Acquire lock and hold it
    lock1 = FileLock(lock_path, timeout=1.0)
    lock1.acquire()

    try:
        # Try to acquire again - should timeout
        lock2 = FileLock(lock_path, timeout=1.0)
        with pytest.raises(TimeoutError):
            lock2.acquire()
    finally:
        lock1.release()


# ============================================================================
# ModelRegistry Tests
# ============================================================================

def test_model_registry_init(model_registry):
    """Test model registry initialization."""
    registry = model_registry._load_registry()
    assert registry == {"models": {}}


def test_promote_model(model_registry, temp_project):
    """Test promoting a model."""
    # Create fake model file
    run_dir = temp_project / "runs" / "run-001"
    run_dir.mkdir(parents=True)
    model_file = run_dir / "best.pt"
    model_file.write_text("fake model weights")

    version = model_registry.promote_model(
        name="detector-v1",
        run_id="run-001",
        model_path=model_file,
        metadata={"map50": 0.85}
    )

    # Verify model was promoted
    model = model_registry.get_model("detector-v1")
    assert model is not None
    assert model["name"] == "detector-v1"
    assert model["run_id"] == "run-001"
    assert model["metadata"]["map50"] == 0.85
    assert version is not None

    # Verify file was copied
    promoted_file = temp_project / "models" / "detector-v1" / "best.pt"
    assert promoted_file.exists()


def test_promote_model_file_not_found(model_registry, temp_project):
    """Test error when model file doesn't exist."""
    with pytest.raises(FileNotFoundError):
        model_registry.promote_model(
            name="detector-v1",
            run_id="run-001",
            model_path=temp_project / "nonexistent.pt"
        )


def test_promote_model_already_exists(model_registry, temp_project):
    """Test error when model name already exists."""
    # Create and promote first model
    model_file = temp_project / "runs" / "run-001" / "best.pt"
    model_file.parent.mkdir(parents=True)
    model_file.write_text("fake weights")

    model_registry.promote_model("detector-v1", "run-001", model_file)

    # Try to promote with same name
    with pytest.raises(ValueError, match="already exists"):
        model_registry.promote_model("detector-v1", "run-002", model_file)


def test_list_models(model_registry, temp_project):
    """Test listing promoted models."""
    # Promote multiple models
    for i in range(3):
        model_file = temp_project / "runs" / f"run-{i:03d}" / "best.pt"
        model_file.parent.mkdir(parents=True)
        model_file.write_text(f"weights-{i}")

        model_registry.promote_model(
            name=f"model-v{i+1}",
            run_id=f"run-{i:03d}",
            model_path=model_file
        )

    models = model_registry.list_models()
    assert len(models) == 3
    assert {m["name"] for m in models} == {"model-v1", "model-v2", "model-v3"}


def test_get_model(model_registry, temp_project):
    """Test getting model by name."""
    model_file = temp_project / "runs" / "run-001" / "best.pt"
    model_file.parent.mkdir(parents=True)
    model_file.write_text("weights")

    model_registry.promote_model("detector-v1", "run-001", model_file)

    model = model_registry.get_model("detector-v1")
    assert model["name"] == "detector-v1"

    # Non-existent model
    assert model_registry.get_model("nonexistent") is None


def test_remove_model(model_registry, temp_project):
    """Test removing promoted model."""
    model_file = temp_project / "runs" / "run-001" / "best.pt"
    model_file.parent.mkdir(parents=True)
    model_file.write_text("weights")

    model_registry.promote_model("detector-v1", "run-001", model_file)

    # Verify it exists
    assert model_registry.get_model("detector-v1") is not None
    model_dir = temp_project / "models" / "detector-v1"
    assert model_dir.exists()

    # Remove it
    model_registry.remove_model("detector-v1")

    # Verify it's gone
    assert model_registry.get_model("detector-v1") is None
    assert not model_dir.exists()


def test_remove_model_not_found(model_registry):
    """Test error when removing non-existent model."""
    with pytest.raises(ValueError, match="Model not found"):
        model_registry.remove_model("nonexistent")


# ============================================================================
# Integration Tests
# ============================================================================

def test_full_training_workflow(run_registry, model_registry, temp_project):
    """Test complete training workflow from run to model promotion."""
    # Create run
    run_registry.add_run({
        "id": "run-001",
        "status": "pending",
        "dataset_name": "test-dataset",
        "created": datetime.utcnow().isoformat() + "Z"
    })

    # Start training
    run_registry.update_run("run-001", {
        "status": "running",
        "pid": 12345
    })

    # Complete training
    run_registry.update_run("run-001", {
        "status": "completed",
        "pid": None,
        "metrics": {"map50": 0.85, "map50_95": 0.72}
    })

    # Create model file
    model_file = temp_project / "runs" / "run-001" / "train" / "weights" / "best.pt"
    model_file.parent.mkdir(parents=True)
    model_file.write_text("trained weights")

    # Promote to production
    model_registry.promote_model(
        name="detector-v1",
        run_id="run-001",
        model_path=model_file,
        metadata={"map50": 0.85}
    )

    # Verify workflow
    run = run_registry.get_run("run-001")
    assert run["status"] == "completed"

    model = model_registry.get_model("detector-v1")
    assert model["run_id"] == "run-001"
    assert model["metadata"]["map50"] == 0.85


def test_registry_persistence(temp_project):
    """Test that registry changes persist across instances."""
    from modelcub.core.registries import RunRegistry

    # Create first instance and add run
    registry1 = RunRegistry(temp_project)
    registry1.add_run({"id": "run-001", "status": "pending"})

    # Create second instance and verify run exists
    registry2 = RunRegistry(temp_project)
    run = registry2.get_run("run-001")
    assert run is not None
    assert run["status"] == "pending"

    # Update via second instance
    registry2.update_run("run-001", {"status": "running"})

    # Verify in third instance
    registry3 = RunRegistry(temp_project)
    run = registry3.get_run("run-001")
    assert run["status"] == "running"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])