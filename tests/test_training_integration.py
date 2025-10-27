"""
Integration tests for training workflow.

Tests complete create → start → monitor → complete flow.
"""
import pytest
import time
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def training_project(tmp_path):
    """Create complete project structure for training tests."""
    project_root = tmp_path / "project"

    (project_root / ".modelcub").mkdir(parents=True)
    (project_root / ".modelcub" / "snapshots").mkdir()
    (project_root / "data" / "datasets").mkdir(parents=True)
    (project_root / "runs").mkdir()

    from modelcub.core.registries import initialize_registries
    initialize_registries(project_root)

    dataset_name = "test-dataset"
    dataset_path = project_root / "data" / "datasets" / dataset_name

    train_images = dataset_path / "train" / "images"
    train_labels = dataset_path / "train" / "labels"
    valid_images = dataset_path / "valid" / "images"
    valid_labels = dataset_path / "valid" / "labels"

    for path in [train_images, train_labels, valid_images, valid_labels]:
        path.mkdir(parents=True)

    for i in range(5):
        (train_images / f"img{i}.jpg").touch()
        (train_labels / f"img{i}.txt").write_text("0 0.5 0.5 0.2 0.2")

    for i in range(2):
        (valid_images / f"val{i}.jpg").touch()
        (valid_labels / f"val{i}.txt").write_text("0 0.5 0.5 0.2 0.2")

    dataset_yaml = dataset_path / "dataset.yaml"
    dataset_yaml.write_text(yaml.safe_dump({
        'path': str(dataset_path),
        'train': 'train/images',
        'val': 'valid/images',
        'names': ['cat', 'dog'],
        'nc': 2
    }))

    from modelcub.core.registries import DatasetRegistry
    registry = DatasetRegistry(project_root)
    registry.add_dataset({
        'id': 'ds-001',
        'name': dataset_name,
        'num_images': 7,
        'classes': ['cat', 'dog'],
        'num_classes': 2
    })

    return project_root, dataset_name


@pytest.fixture
def training_service(training_project):
    """Create TrainingService instance."""
    project_root, _ = training_project
    from modelcub.services.training import TrainingService
    return TrainingService(project_root)


def test_create_run_success(training_service, training_project):
    """Test creating a training run."""
    _, dataset_name = training_project

    run_id = training_service.create_run(
        dataset_name=dataset_name,
        model="yolov8n",
        epochs=10,
        device="cpu"
    )

    assert run_id.startswith("run-")

    run = training_service.get_status(run_id)
    assert run['status'] == 'pending'
    assert run['dataset_name'] == dataset_name
    assert run['config']['model'] == 'yolov8n'
    assert run['config']['epochs'] == 10


def test_create_run_invalid_dataset(training_service):
    """Test creating run with non-existent dataset fails."""
    with pytest.raises(ValueError, match="Dataset not found"):
        training_service.create_run(
            dataset_name="nonexistent",
            model="yolov8n",
            epochs=10
        )


def test_create_run_invalid_model(training_service, training_project):
    """Test creating run with invalid model fails."""
    _, dataset_name = training_project

    with pytest.raises(ValueError, match="Unknown model"):
        training_service.create_run(
            dataset_name=dataset_name,
            model="yolov5n",
            epochs=10
        )


def test_create_run_generates_snapshot(training_service, training_project):
    """Test run creation generates dataset snapshot."""
    project_root, dataset_name = training_project

    run_id = training_service.create_run(
        dataset_name=dataset_name,
        model="yolov8n",
        epochs=10
    )

    run = training_service.get_status(run_id)
    snapshot_id = run['dataset_snapshot_id']

    snapshot_path = project_root / ".modelcub" / "snapshots" / f"{snapshot_id}.json"
    assert snapshot_path.exists()


def test_create_run_generates_lockfile(training_service, training_project):
    """Test run creation generates lockfile."""
    project_root, dataset_name = training_project

    run_id = training_service.create_run(
        dataset_name=dataset_name,
        model="yolov8n",
        epochs=10
    )

    run = training_service.get_status(run_id)
    lockfile_path = project_root / run['artifacts_path'] / "config.lock.yaml"

    assert lockfile_path.exists()


def test_create_run_emits_event(training_service, training_project):
    """Test run creation emits TrainingRunCreated event."""
    from modelcub.events.events import bus
    from modelcub.events.training import TrainingRunCreated

    _, dataset_name = training_project
    events = []

    def handler(event):
        events.append(event)

    bus.subscribe(TrainingRunCreated, handler)

    try:
        run_id = training_service.create_run(
            dataset_name=dataset_name,
            model="yolov8n",
            epochs=10,
            device="cpu"
        )

        assert len(events) == 1
        assert events[0].run_id == run_id
        assert events[0].model == "yolov8n"
    finally:
        bus.unsubscribe(TrainingRunCreated, handler)


def test_start_run_validation_fails(training_service, training_project):
    """Test start_run fails validation checks."""
    project_root, dataset_name = training_project

    empty_dataset = "empty-dataset"
    empty_path = project_root / "data" / "datasets" / empty_dataset
    (empty_path / "train" / "images").mkdir(parents=True)
    (empty_path / "valid" / "images").mkdir(parents=True)
    (empty_path / "dataset.yaml").write_text("names: [cat]\nnc: 1")

    from modelcub.core.registries import DatasetRegistry
    registry = DatasetRegistry(project_root)
    registry.add_dataset({
        'id': 'ds-002',
        'name': empty_dataset,
        'num_images': 0,
        'classes': ['cat'],
        'num_classes': 1
    })

    run_id = training_service.create_run(
        dataset_name=empty_dataset,
        model="yolov8n",
        epochs=10
    )

    with pytest.raises(ValueError, match="No images found"):
        training_service.start_run(run_id)

    run = training_service.get_status(run_id)
    assert run['status'] == 'failed'


def test_start_run_not_pending(training_service, training_project):
    """Test start_run fails if run not pending."""
    _, dataset_name = training_project

    run_id = training_service.create_run(
        dataset_name=dataset_name,
        model="yolov8n",
        epochs=10
    )

    # Transition to running first, then to completed
    training_service.run_registry.update_run(run_id, {'status': 'running'})
    training_service.run_registry.update_run(run_id, {'status': 'completed'})

    with pytest.raises(ValueError, match="not pending"):
        training_service.start_run(run_id)


@patch('modelcub.core.processes.is_process_alive')
@patch('modelcub.core.processes.spawn_training')
def test_start_run_success(mock_spawn, mock_alive, training_service, training_project):
    """Test starting a training run."""
    _, dataset_name = training_project

    mock_spawn.return_value = 12345
    mock_alive.return_value = True

    run_id = training_service.create_run(
        dataset_name=dataset_name,
        model="yolov8n",
        epochs=10,
        device="cpu"
    )

    training_service.start_run(run_id)

    run = training_service.get_status(run_id)
    assert run['status'] == 'running'
    assert run['pid'] == 12345
    assert 'started' in run


@patch('modelcub.core.processes.is_process_alive')
@patch('modelcub.core.processes.spawn_training')
def test_start_run_emits_event(mock_spawn, mock_alive, training_service, training_project):
    """Test start_run emits TrainingStarted event."""
    from modelcub.events.events import bus
    from modelcub.events.training import TrainingStarted

    _, dataset_name = training_project
    mock_spawn.return_value = 12345
    mock_alive.return_value = True
    events = []

    def handler(event):
        events.append(event)

    bus.subscribe(TrainingStarted, handler)

    try:
        run_id = training_service.create_run(
            dataset_name=dataset_name,
            model="yolov8n",
            epochs=10
        )

        training_service.start_run(run_id)

        assert len(events) == 1
        assert events[0].run_id == run_id
        assert events[0].pid == 12345
    finally:
        bus.unsubscribe(TrainingStarted, handler)


@patch('modelcub.core.processes.is_process_alive')
@patch('modelcub.core.processes.terminate_process')
@patch('modelcub.core.processes.spawn_training')
def test_stop_run_success(mock_spawn, mock_terminate, mock_alive, training_service, training_project):
    """Test stopping a running training run."""
    _, dataset_name = training_project
    mock_spawn.return_value = 12345
    mock_alive.return_value = True

    run_id = training_service.create_run(
        dataset_name=dataset_name,
        model="yolov8n",
        epochs=10
    )

    training_service.start_run(run_id)
    training_service.stop_run(run_id)

    mock_terminate.assert_called_once_with(12345, timeout=10.0)

    run = training_service.get_status(run_id)
    assert run['status'] == 'cancelled'
    assert run['pid'] is None


@patch('modelcub.core.processes.spawn_training')
def test_stop_run_not_running(mock_spawn, training_service, training_project):
    """Test stop_run fails if run not running."""
    _, dataset_name = training_project

    run_id = training_service.create_run(
        dataset_name=dataset_name,
        model="yolov8n",
        epochs=10
    )

    with pytest.raises(ValueError, match="not running"):
        training_service.stop_run(run_id)


@patch('modelcub.core.processes.is_process_alive')
@patch('modelcub.core.processes.spawn_training')
def test_get_status_detects_dead_process(mock_spawn, mock_alive, training_service, training_project):
    """Test get_status detects when process dies."""
    project_root, dataset_name = training_project
    mock_spawn.return_value = 12345

    run_id = training_service.create_run(
        dataset_name=dataset_name,
        model="yolov8n",
        epochs=10
    )

    # Process is alive during start
    mock_alive.return_value = True
    training_service.start_run(run_id)

    # Process dies
    mock_alive.return_value = False

    run_path = project_root / "runs" / run_id
    results_csv = run_path / "train" / "results.csv"
    results_csv.parent.mkdir(parents=True)
    results_csv.write_text("epoch,metrics/mAP50(B),metrics/mAP50-95(B)\n1,0.5,0.4")

    status = training_service.get_status(run_id)

    assert status['status'] == 'completed'
    assert status['pid'] is None


def test_list_runs_all(training_service, training_project):
    """Test listing all runs."""
    _, dataset_name = training_project

    run1 = training_service.create_run(dataset_name=dataset_name, model="yolov8n", epochs=10)
    time.sleep(1)
    run2 = training_service.create_run(dataset_name=dataset_name, model="yolov8s", epochs=20)

    runs = training_service.list_runs()
    assert len(runs) == 2
    assert {r['id'] for r in runs} == {run1, run2}


def test_list_runs_filtered(training_service, training_project):
    """Test listing runs filtered by status."""
    _, dataset_name = training_project

    run1 = training_service.create_run(dataset_name=dataset_name, model="yolov8n", epochs=10)
    run2 = training_service.create_run(dataset_name=dataset_name, model="yolov8s", epochs=20)

    # Transition properly: pending → running → completed
    training_service.run_registry.update_run(run2, {'status': 'running'})
    training_service.run_registry.update_run(run2, {'status': 'completed'})

    pending = training_service.list_runs(status='pending')
    assert len(pending) == 1
    assert pending[0]['id'] == run1

    completed = training_service.list_runs(status='completed')
    assert len(completed) == 1
    assert completed[0]['id'] == run2


@patch('modelcub.core.processes.is_process_alive')
def test_orphaned_process_recovery(mock_alive, training_project):
    """Test orphaned processes are recovered on init."""
    from modelcub.services.training import TrainingService
    from modelcub.events.events import bus
    from modelcub.events.training import OrphanedProcessRecovered

    project_root, dataset_name = training_project
    events = []

    def handler(event):
        events.append(event)

    bus.subscribe(OrphanedProcessRecovered, handler)

    try:
        service = TrainingService(project_root)

        run_id = service.create_run(
            dataset_name=dataset_name,
            model="yolov8n",
            epochs=10
        )

        # Manually mark as running (simulating crash)
        service.run_registry.update_run(run_id, {
            'status': 'running',
            'pid': 99999
        })

        # Process is dead
        mock_alive.return_value = False

        # Create new service - should recover orphan
        service2 = TrainingService(project_root)

        run = service2.get_status(run_id)
        assert run['status'] == 'failed'

        assert len(events) == 1
        assert events[0].run_id == run_id
        assert events[0].pid == 99999
    finally:
        bus.unsubscribe(OrphanedProcessRecovered, handler)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])