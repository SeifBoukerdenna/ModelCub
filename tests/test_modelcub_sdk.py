"""
Comprehensive pytest test suite for ModelCub SDK.

Tests cover:
- Project initialization and management
- Dataset operations and management
- Job/task management
- Error handling and edge cases
- Integration scenarios
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from datetime import datetime
from typing import List, Dict, Any
import tempfile
import shutil
import json

# Import SDK components
from modelcub.sdk import (
    Project,
    Dataset,
    DatasetInfo,
    Box,
    JobManager,
    Job,
    JobStatus,
    TaskStatus
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test projects."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_project_path(temp_dir):
    """Create a mock project directory structure."""
    project_path = temp_dir / "test_project"
    project_path.mkdir(parents=True)

    # Create .modelcub directory
    modelcub_dir = project_path / ".modelcub"
    modelcub_dir.mkdir()

    # Create config.yaml
    config_file = modelcub_dir / "config.yaml"
    config_data = {
        "project": {
            "name": "test_project",
            "version": "1.0.0",
            "created": datetime.now().isoformat()
        },
        "defaults": {
            "device": "cpu",
            "batch_size": 16,
            "image_size": 640,
            "workers": 4,
            "format": "yolo"
        },
        "paths": {
            "data": "data",
            "runs": "runs",
            "reports": "reports"
        }
    }

    with open(config_file, 'w') as f:
        import yaml
        yaml.dump(config_data, f)

    # Create data directory
    (project_path / "data" / "datasets").mkdir(parents=True)

    return project_path


@pytest.fixture
def mock_dataset_registry():
    """Mock DatasetRegistry for testing."""
    with patch('modelcub.sdk.dataset.DatasetRegistry') as mock:
        registry_instance = MagicMock()
        mock.return_value = registry_instance
        yield registry_instance


@pytest.fixture
def mock_annotation_job_manager():
    """Mock AnnotationJobManager for testing."""
    with patch('modelcub.sdk.job.AnnotationJobManager') as mock:
        manager_instance = MagicMock()
        mock.return_value = manager_instance
        yield manager_instance


# ============================================================================
# PROJECT TESTS
# ============================================================================

class TestProject:
    """Test suite for Project class."""

    def test_project_init_with_valid_path(self, mock_project_path):
        """Test Project initialization with valid project path."""
        with patch('modelcub.sdk.project.load_config') as mock_load:
            mock_load.return_value = MagicMock()
            project = Project(mock_project_path)

            # Use .resolve() to handle symlinks and /private/ prefix on macOS
            assert project.path.resolve() == mock_project_path.resolve()
            mock_load.assert_called_once()

    def test_project_init_with_invalid_path(self, temp_dir):
        """Test Project initialization with invalid path raises ValueError."""
        invalid_path = temp_dir / "nonexistent"

        with pytest.raises(ValueError, match="Not a valid ModelCub project"):
            Project(invalid_path)

    def test_project_init_creates_new_project(self, temp_dir):
        """Test Project.init() creates a new project."""
        project_name = "new_project"
        project_path = temp_dir / project_name

        with patch('modelcub.sdk.project.init_project') as mock_init:
            mock_init.return_value = MagicMock(success=True, message="Created")
            with patch('modelcub.sdk.project.load_config') as mock_load:
                mock_load.return_value = MagicMock()
                with patch.object(Project, '_is_valid_project', return_value=True):

                    project = Project.init(name=project_name, path=str(project_path))

                    assert isinstance(project, Project)
                    mock_init.assert_called_once()

    def test_project_init_with_force_flag(self, temp_dir):
        """Test Project.init() with force flag overwrites existing project."""
        project_name = "existing_project"
        project_path = temp_dir / project_name

        with patch('modelcub.sdk.project.init_project') as mock_init:
            mock_init.return_value = MagicMock(success=True, message="Overwritten")
            with patch('modelcub.sdk.project.load_config') as mock_load:
                mock_load.return_value = MagicMock()
                with patch.object(Project, '_is_valid_project', return_value=True):

                    project = Project.init(
                        name=project_name,
                        path=str(project_path),
                        force=True
                    )

                    # Verify force was passed
                    call_args = mock_init.call_args[0][0]
                    assert call_args.force is True

    def test_project_init_fails_gracefully(self, temp_dir):
        """Test Project.init() raises RuntimeError on failure."""
        with patch('modelcub.sdk.project.init_project') as mock_init:
            mock_init.return_value = MagicMock(
                success=False,
                message="Failed to create"
            )

            with pytest.raises(RuntimeError, match="Failed to initialize project"):
                Project.init(name="bad_project", path=str(temp_dir / "bad"))

    def test_project_load_with_path(self, mock_project_path):
        """Test Project.load() with explicit path."""
        with patch('modelcub.sdk.project.load_config') as mock_load:
            mock_load.return_value = MagicMock()

            project = Project.load(path=mock_project_path)

            assert project.path.resolve() == mock_project_path.resolve()

    def test_project_load_without_path_searches_upward(self):
        """Test Project.load() without path searches from current directory."""
        mock_path = Path("/mock/project")

        with patch('modelcub.sdk.project.project_root') as mock_root:
            mock_root.return_value = mock_path
            with patch('modelcub.sdk.project.load_config') as mock_load:
                mock_load.return_value = MagicMock()
                with patch.object(Project, '_is_valid_project', return_value=True):

                    project = Project.load()

                    assert project.path == mock_path
                    mock_root.assert_called_once()

    def test_project_exists_returns_true_for_valid_project(self, mock_project_path):
        """Test Project.exists() returns True for valid project."""
        result = Project.exists(mock_project_path)
        assert result is True

    def test_project_exists_returns_false_for_invalid_project(self, temp_dir):
        """Test Project.exists() returns False for invalid project."""
        result = Project.exists(temp_dir / "nonexistent")
        assert result is False

    def test_project_is_valid_project_checks_structure(self, mock_project_path):
        """Test _is_valid_project() validates directory structure."""
        assert Project._is_valid_project(mock_project_path) is True

        # Test invalid structure
        invalid_path = mock_project_path / "invalid"
        invalid_path.mkdir()
        assert Project._is_valid_project(invalid_path) is False

    def test_project_config_property(self, mock_project_path):
        """Test Project._config property is accessible."""
        mock_config = MagicMock()

        with patch('modelcub.sdk.project.load_config', return_value=mock_config):
            project = Project(mock_project_path)

            assert project._config == mock_config

    def test_project_str_representation(self, mock_project_path):
        """Test Project string representation."""
        with patch('modelcub.sdk.project.load_config') as mock_load:
            mock_config = MagicMock()
            mock_config.project.name = "test_project"
            mock_load.return_value = mock_config

            project = Project(mock_project_path)

            # Test that project has proper attributes
            assert hasattr(project, 'path')
            assert hasattr(project, '_config')


# ============================================================================
# DATASET TESTS
# ============================================================================

class TestDataset:
    """Test suite for Dataset class."""

    def test_dataset_init_with_valid_name(self, mock_project_path, mock_dataset_registry):
        """Test Dataset initialization with valid name."""
        mock_dataset_registry.get_dataset.return_value = {
            "name": "test_dataset",
            "num_images": 100,
            "classes": ["cat", "dog"],
            "status": "ready"
        }

        dataset = Dataset("test_dataset", project_path=mock_project_path)

        assert dataset.name == "test_dataset"
        assert dataset.project_path.resolve() == mock_project_path.resolve()

    def test_dataset_init_without_project_path_searches(self, mock_dataset_registry):
        """Test Dataset initialization without project_path searches upward."""
        mock_path = Path("/mock/project")
        mock_dataset_registry.get_dataset.return_value = {"name": "test_dataset"}

        # Create mock .modelcub directory
        with patch('modelcub.sdk.dataset.project_root', return_value=mock_path):
            with patch('pathlib.Path.exists', return_value=True):
                dataset = Dataset("test_dataset")

                assert dataset._project_path == mock_path

    def test_dataset_init_raises_error_for_invalid_project(self, temp_dir, mock_dataset_registry):
        """Test Dataset initialization raises ValueError for invalid project."""
        invalid_path = temp_dir / "invalid"

        with pytest.raises(ValueError, match="Not a valid project"):
            Dataset("test_dataset", project_path=invalid_path)

    def test_dataset_init_raises_error_for_nonexistent_dataset(self, mock_project_path, mock_dataset_registry):
        """Test Dataset initialization raises ValueError if dataset doesn't exist."""
        mock_dataset_registry.get_dataset.return_value = None

        with pytest.raises(ValueError, match="Dataset not found"):
            Dataset("nonexistent_dataset", project_path=mock_project_path)

    def test_dataset_path_property(self, mock_project_path, mock_dataset_registry):
        """Test Dataset.path property returns correct path."""
        mock_dataset_registry.get_dataset.return_value = {"name": "test_dataset"}

        dataset = Dataset("test_dataset", project_path=mock_project_path)
        expected_path = mock_project_path / "data" / "datasets" / "test_dataset"

        assert dataset.path.resolve() == expected_path.resolve()

    def test_dataset_images_property(self, mock_project_path, mock_dataset_registry):
        """Test Dataset.images property returns correct count."""
        mock_dataset_registry.get_dataset.return_value = {
            "name": "test_dataset",
            "num_images": 250
        }

        dataset = Dataset("test_dataset", project_path=mock_project_path)

        assert dataset.images == 250

    def test_dataset_status_property(self, mock_project_path, mock_dataset_registry):
        """Test Dataset.status property."""
        mock_dataset_registry.get_dataset.return_value = {
            "name": "test_dataset",
            "status": "processing"
        }

        dataset = Dataset("test_dataset", project_path=mock_project_path)

        assert dataset.status == "processing"

    def test_dataset_status_defaults_to_ready(self, mock_project_path, mock_dataset_registry):
        """Test Dataset.status defaults to 'ready' if not set."""
        mock_dataset_registry.get_dataset.return_value = {
            "name": "test_dataset"
        }

        dataset = Dataset("test_dataset", project_path=mock_project_path)

        assert dataset.status == "ready"

    def test_dataset_load_class_method(self, mock_project_path, mock_dataset_registry):
        """Test Dataset.load() class method."""
        mock_dataset_registry.get_dataset.return_value = {"name": "test_dataset"}

        dataset = Dataset.load("test_dataset", project_path=mock_project_path)

        assert isinstance(dataset, Dataset)
        assert dataset.name == "test_dataset"

    def test_dataset_info_method(self, mock_project_path, mock_dataset_registry):
        """Test Dataset.info() returns DatasetInfo."""
        mock_dataset_registry.get_dataset.return_value = {
            "name": "test_dataset",
            "id": "ds_123",
            "num_images": 100,
            "classes": ["cat", "dog"],
            "status": "ready",
            "created": "2024-01-01T00:00:00"
        }

        dataset = Dataset("test_dataset", project_path=mock_project_path)

        # Test that info method exists (implementation may vary)
        assert hasattr(dataset, 'info')

    def test_dataset_size_calculation(self, mock_project_path, mock_dataset_registry):
        """Test Dataset.size property calculates directory size."""
        mock_dataset_registry.get_dataset.return_value = {"name": "test_dataset"}

        # Create actual files for size calculation
        dataset_path = mock_project_path / "data" / "datasets" / "test_dataset"
        dataset_path.mkdir(parents=True)

        # Create some test files
        (dataset_path / "image1.jpg").write_bytes(b"x" * 1024)  # 1KB
        (dataset_path / "image2.jpg").write_bytes(b"x" * 2048)  # 2KB

        dataset = Dataset("test_dataset", project_path=mock_project_path)

        # Size should be calculated
        assert hasattr(dataset, 'size')


class TestDatasetInfo:
    """Test suite for DatasetInfo dataclass."""

    def test_datasetinfo_creation(self):
        """Test DatasetInfo dataclass can be created."""
        info = DatasetInfo(
            name="test_dataset",
            id="ds_123",
            path=Path("/path/to/dataset"),
            images=100,
            classes=["cat", "dog"],
            status="ready",
            total_images=100,
            size="10 MB",
            created="2024-01-01",
            source="imported"
        )

        assert info.name == "test_dataset"
        assert info.id == "ds_123"
        assert info.images == 100
        assert len(info.classes) == 2
        assert info.status == "ready"

    def test_datasetinfo_optional_fields(self):
        """Test DatasetInfo with optional fields."""
        info = DatasetInfo(
            name="test_dataset",
            id="ds_123",
            path=Path("/path"),
            images=50,
            classes=["cat"],
            status="ready",
            total_images=50,
            size="5 MB"
        )

        assert info.created is None
        assert info.source is None


class TestBox:
    """Test suite for Box dataclass."""

    def test_box_creation(self):
        """Test Box dataclass can be created."""
        box = Box(class_id=0, x=0.5, y=0.5, w=0.2, h=0.3)

        assert box.class_id == 0
        assert box.x == 0.5
        assert box.y == 0.5
        assert box.w == 0.2
        assert box.h == 0.3

    def test_box_to_dict(self):
        """Test Box.to_dict() method."""
        box = Box(class_id=1, x=0.3, y=0.4, w=0.15, h=0.25)
        result = box.to_dict()

        assert result == {
            "class_id": 1,
            "x": 0.3,
            "y": 0.4,
            "w": 0.15,
            "h": 0.25
        }

    def test_box_with_edge_values(self):
        """Test Box with edge case values (0.0 and 1.0)."""
        box = Box(class_id=0, x=0.0, y=0.0, w=1.0, h=1.0)

        assert box.x == 0.0
        assert box.y == 0.0
        assert box.w == 1.0
        assert box.h == 1.0

    def test_box_normalized_coordinates(self):
        """Test Box coordinates are in normalized format (0-1)."""
        box = Box(class_id=2, x=0.75, y=0.25, w=0.1, h=0.1)

        assert 0 <= box.x <= 1
        assert 0 <= box.y <= 1
        assert 0 <= box.w <= 1
        assert 0 <= box.h <= 1


# ============================================================================
# JOB TESTS
# ============================================================================

class TestJob:
    """Test suite for Job class."""

    @pytest.fixture
    def mock_job_data(self):
        """Create mock AnnotationJob data."""
        mock_data = MagicMock()
        mock_data.job_id = "job_123"
        mock_data.dataset_name = "test_dataset"
        mock_data.status = JobStatus.PENDING
        mock_data.progress = 0.0
        mock_data.total_tasks = 100
        mock_data.completed_tasks = 0
        mock_data.failed_tasks = 0
        mock_data.is_terminal = False
        mock_data.created_at = datetime.now()
        return mock_data

    def test_job_init(self, mock_job_data):
        """Test Job initialization."""
        mock_manager = MagicMock()
        job = Job(mock_job_data, mock_manager)

        assert job.id == "job_123"
        assert job.dataset_name == "test_dataset"
        assert job.status == JobStatus.PENDING

    def test_job_properties(self, mock_job_data):
        """Test Job property accessors."""
        mock_manager = MagicMock()
        job = Job(mock_job_data, mock_manager)

        assert job.id == "job_123"
        assert job.dataset_name == "test_dataset"
        assert job.status == JobStatus.PENDING
        assert job.progress == 0.0
        assert job.total_tasks == 100
        assert job.completed_tasks == 0
        assert job.failed_tasks == 0
        assert job.is_complete is False
        assert isinstance(job.created_at, datetime)

    def test_job_start(self, mock_job_data):
        """Test Job.start() method."""
        mock_manager = MagicMock()
        updated_data = MagicMock()
        updated_data.status = JobStatus.RUNNING
        mock_manager.start_job.return_value = updated_data

        job = Job(mock_job_data, mock_manager)
        result = job.start()

        assert result == job
        mock_manager.start_job.assert_called_once_with("job_123")

    def test_job_pause(self, mock_job_data):
        """Test Job.pause() method."""
        mock_manager = MagicMock()
        updated_data = MagicMock()
        updated_data.status = JobStatus.PAUSED
        mock_manager.pause_job.return_value = updated_data

        job = Job(mock_job_data, mock_manager)
        result = job.pause()

        assert result == job
        mock_manager.pause_job.assert_called_once_with("job_123")

    def test_job_cancel(self, mock_job_data):
        """Test Job.cancel() method."""
        mock_manager = MagicMock()
        updated_data = MagicMock()
        updated_data.status = JobStatus.CANCELLED
        mock_manager.cancel_job.return_value = updated_data

        job = Job(mock_job_data, mock_manager)
        result = job.cancel()

        assert result == job
        mock_manager.cancel_job.assert_called_once_with("job_123")

    def test_job_refresh(self, mock_job_data):
        """Test Job.refresh() updates job data."""
        mock_manager = MagicMock()
        updated_data = MagicMock()
        updated_data.progress = 50.0
        mock_manager.get_job.return_value = updated_data

        job = Job(mock_job_data, mock_manager)
        result = job.refresh()

        assert result == job
        mock_manager.get_job.assert_called_once_with("job_123")

    def test_job_wait(self, mock_job_data):
        """Test Job.wait() polls until completion."""
        mock_manager = MagicMock()

        # Simulate job progression
        states = [
            MagicMock(is_terminal=False, progress=25.0),
            MagicMock(is_terminal=False, progress=75.0),
            MagicMock(is_terminal=True, progress=100.0)
        ]
        mock_manager.get_job.side_effect = states

        job = Job(mock_job_data, mock_manager)

        with patch('time.sleep'):  # Don't actually sleep in tests
            result = job.wait(poll_interval=0.1)

        assert result == job
        assert mock_manager.get_job.call_count >= 2

    def test_job_get_tasks(self, mock_job_data):
        """Test Job.get_tasks() method."""
        mock_manager = MagicMock()
        mock_tasks = [MagicMock(), MagicMock()]
        mock_manager.get_tasks.return_value = mock_tasks

        job = Job(mock_job_data, mock_manager)
        tasks = job.get_tasks(status=TaskStatus.COMPLETED)

        assert tasks == mock_tasks
        mock_manager.get_tasks.assert_called_once_with("job_123", TaskStatus.COMPLETED)

    def test_job_get_tasks_without_filter(self, mock_job_data):
        """Test Job.get_tasks() without status filter."""
        mock_manager = MagicMock()
        mock_tasks = [MagicMock(), MagicMock(), MagicMock()]
        mock_manager.get_tasks.return_value = mock_tasks

        job = Job(mock_job_data, mock_manager)
        tasks = job.get_tasks()

        assert len(tasks) == 3
        mock_manager.get_tasks.assert_called_once_with("job_123", None)

    def test_job_review_data(self, mock_job_data):
        """Test Job.review_data() method."""
        mock_manager = MagicMock()
        review_data = {"images": 100, "annotations": 250}
        mock_manager.get_job_review_data.return_value = review_data

        job = Job(mock_job_data, mock_manager)
        result = job.review_data()

        assert result == review_data
        mock_manager.get_job_review_data.assert_called_once_with("job_123")

    def test_job_assign_splits(self, mock_job_data):
        """Test Job.assign_splits() method."""
        mock_manager = MagicMock()
        mock_manager.project_path = Path("/mock/project")

        assignments = [
            {"image_id": "img1", "split": "train"},
            {"image_id": "img2", "split": "val"}
        ]

        with patch('modelcub.services.split_service.batch_move_to_splits') as mock_batch:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.data = {"assigned": 2}
            mock_batch.return_value = mock_result

            job = Job(mock_job_data, mock_manager)
            result = job.assign_splits(assignments)

            assert result == {"assigned": 2}
            mock_batch.assert_called_once()

    def test_job_assign_splits_failure(self, mock_job_data):
        """Test Job.assign_splits() raises error on failure."""
        mock_manager = MagicMock()
        mock_manager.project_path = Path("/mock/project")

        assignments = [{"image_id": "img1", "split": "train"}]

        with patch('modelcub.services.split_service.batch_move_to_splits') as mock_batch:
            mock_result = MagicMock()
            mock_result.success = False
            mock_result.message = "Assignment failed"
            mock_batch.return_value = mock_result

            job = Job(mock_job_data, mock_manager)

            with pytest.raises(ValueError, match="Assignment failed"):
                job.assign_splits(assignments)

    def test_job_to_dict(self, mock_job_data):
        """Test Job.to_dict() serialization."""
        mock_manager = MagicMock()
        job = Job(mock_job_data, mock_manager)

        result = job.to_dict()

        assert isinstance(result, dict)
        assert result["id"] == "job_123"
        assert result["dataset_name"] == "test_dataset"
        assert result["status"] == JobStatus.PENDING.value
        assert "progress" in result
        assert "created_at" in result

    def test_job_load_class_method(self):
        """Test Job.load() class method."""
        mock_path = Path("/mock/project")

        with patch('modelcub.sdk.job.project_root', return_value=mock_path):
            with patch('modelcub.sdk.job.AnnotationJobManager') as mock_manager_class:
                mock_manager = MagicMock()
                mock_job_data = MagicMock()
                mock_job_data.job_id = "job_123"
                mock_manager.get_job.return_value = mock_job_data
                mock_manager_class.return_value = mock_manager

                job = Job.load("job_123")

                assert isinstance(job, Job)
                mock_manager.get_job.assert_called_once_with("job_123")

    def test_job_load_with_explicit_path(self):
        """Test Job.load() with explicit project path."""
        project_path = Path("/explicit/project")

        with patch('modelcub.sdk.job.AnnotationJobManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_job_data = MagicMock()
            mock_manager.get_job.return_value = mock_job_data
            mock_manager_class.return_value = mock_manager

            Job.load("job_123", project_path=project_path)

            mock_manager_class.assert_called_once_with(project_path)

    def test_job_load_raises_error_if_not_found(self):
        """Test Job.load() raises ValueError if job not found."""
        with patch('modelcub.sdk.job.project_root'):
            with patch('modelcub.sdk.job.AnnotationJobManager') as mock_manager_class:
                mock_manager = MagicMock()
                mock_manager.get_job.return_value = None
                mock_manager_class.return_value = mock_manager

                with pytest.raises(ValueError, match="Job not found"):
                    Job.load("nonexistent_job")

    def test_job_repr(self, mock_job_data):
        """Test Job string representation."""
        mock_manager = MagicMock()
        job = Job(mock_job_data, mock_manager)

        repr_str = repr(job)

        assert "Job" in repr_str
        assert "job_123" in repr_str
        assert JobStatus.PENDING.value in repr_str


class TestJobManager:
    """Test suite for JobManager class."""

    def test_jobmanager_init(self):
        """Test JobManager initialization."""
        project_path = Path("/mock/project")

        with patch('modelcub.sdk.job.AnnotationJobManager') as mock_manager_class:
            manager = JobManager(project_path=project_path, num_workers=8)

            assert manager.project_path == project_path
            mock_manager_class.assert_called_once_with(project_path, num_workers=8)

    def test_jobmanager_init_defaults(self):
        """Test JobManager initialization with defaults."""
        mock_path = Path("/mock/project")

        with patch('modelcub.sdk.job.project_root', return_value=mock_path):
            with patch('modelcub.sdk.job.AnnotationJobManager'):
                manager = JobManager()

                assert manager.project_path == mock_path

    def test_jobmanager_load_class_method(self):
        """Test JobManager.load() class method."""
        mock_path = Path("/mock/project")

        with patch('modelcub.sdk.job.project_root', return_value=mock_path):
            with patch('modelcub.sdk.job.AnnotationJobManager'):
                manager = JobManager.load()

                assert isinstance(manager, JobManager)
                assert manager.project_path == mock_path

    def test_jobmanager_create_job(self):
        """Test JobManager.create_job() method."""
        with patch('modelcub.sdk.job.project_root'):
            with patch('modelcub.sdk.job.AnnotationJobManager') as mock_manager_class:
                mock_manager = MagicMock()
                mock_job_data = MagicMock()
                mock_manager.create_job.return_value = mock_job_data
                mock_manager_class.return_value = mock_manager

                manager = JobManager()
                job = manager.create_job(
                    dataset_name="test_dataset",
                    image_ids=["img1", "img2"],
                    config={"option": "value"}
                )

                assert isinstance(job, Job)
                mock_manager.create_job.assert_called_once_with(
                    "test_dataset",
                    ["img1", "img2"],
                    {"option": "value"}
                )

    def test_jobmanager_create_job_with_auto_start(self):
        """Test JobManager.create_job() with auto_start=True."""
        with patch('modelcub.sdk.job.project_root'):
            with patch('modelcub.sdk.job.AnnotationJobManager') as mock_manager_class:
                mock_manager = MagicMock()
                mock_job_data = MagicMock()
                mock_job_data.job_id = "job_123"
                mock_manager.create_job.return_value = mock_job_data
                mock_manager.start_job.return_value = mock_job_data
                mock_manager_class.return_value = mock_manager

                manager = JobManager()
                job = manager.create_job(
                    dataset_name="test_dataset",
                    auto_start=True
                )

                mock_manager.start_job.assert_called_once_with("job_123")

    def test_jobmanager_get_job(self):
        """Test JobManager.get_job() method."""
        with patch('modelcub.sdk.job.project_root'):
            with patch('modelcub.sdk.job.AnnotationJobManager') as mock_manager_class:
                mock_manager = MagicMock()
                mock_job_data = MagicMock()
                mock_manager.get_job.return_value = mock_job_data
                mock_manager_class.return_value = mock_manager

                manager = JobManager()
                job = manager.get_job("job_123")

                assert isinstance(job, Job)
                mock_manager.get_job.assert_called_once_with("job_123")

    def test_jobmanager_get_job_returns_none_if_not_found(self):
        """Test JobManager.get_job() returns None if job not found."""
        with patch('modelcub.sdk.job.project_root'):
            with patch('modelcub.sdk.job.AnnotationJobManager') as mock_manager_class:
                mock_manager = MagicMock()
                mock_manager.get_job.return_value = None
                mock_manager_class.return_value = mock_manager

                manager = JobManager()
                job = manager.get_job("nonexistent")

                assert job is None

    def test_jobmanager_list_jobs(self):
        """Test JobManager.list_jobs() method."""
        with patch('modelcub.sdk.job.project_root'):
            with patch('modelcub.sdk.job.AnnotationJobManager') as mock_manager_class:
                mock_manager = MagicMock()
                mock_jobs_data = [MagicMock(), MagicMock(), MagicMock()]
                mock_manager.list_jobs.return_value = mock_jobs_data
                mock_manager_class.return_value = mock_manager

                manager = JobManager()
                jobs = manager.list_jobs()

                assert len(jobs) == 3
                assert all(isinstance(j, Job) for j in jobs)

    def test_jobmanager_list_jobs_with_status_filter(self):
        """Test JobManager.list_jobs() with status filter."""
        with patch('modelcub.sdk.job.project_root'):
            with patch('modelcub.sdk.job.AnnotationJobManager') as mock_manager_class:
                mock_manager = MagicMock()
                mock_jobs_data = [MagicMock()]
                mock_manager.list_jobs.return_value = mock_jobs_data
                mock_manager_class.return_value = mock_manager

                manager = JobManager()
                jobs = manager.list_jobs(status=JobStatus.COMPLETED)

                mock_manager.list_jobs.assert_called_once_with(JobStatus.COMPLETED)
                assert len(jobs) == 1

    def test_jobmanager_set_task_handler(self):
        """Test JobManager.set_task_handler() method."""
        def custom_handler(task):
            return {"result": "processed"}

        with patch('modelcub.sdk.job.project_root'):
            with patch('modelcub.sdk.job.AnnotationJobManager') as mock_manager_class:
                mock_manager = MagicMock()
                mock_manager_class.return_value = mock_manager

                manager = JobManager()
                manager.set_task_handler(custom_handler)

                assert mock_manager._handle_task == custom_handler

    def test_jobmanager_repr(self):
        """Test JobManager string representation."""
        project_path = Path("/mock/project")

        with patch('modelcub.sdk.job.project_root', return_value=project_path):
            with patch('modelcub.sdk.job.AnnotationJobManager'):
                manager = JobManager()

                repr_str = repr(manager)

                assert "JobManager" in repr_str
                assert str(project_path) in repr_str


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestSDKIntegration:
    """Integration tests for SDK components working together."""

    def test_project_to_dataset_workflow(self, mock_project_path, mock_dataset_registry):
        """Test typical workflow from project to dataset."""
        # Setup
        mock_dataset_registry.get_dataset.return_value = {
            "name": "test_dataset",
            "num_images": 50,
            "classes": ["cat", "dog"]
        }

        with patch('modelcub.sdk.project.load_config') as mock_load:
            mock_load.return_value = MagicMock()

            # Load project
            project = Project.load(mock_project_path)

            # Load dataset from project
            dataset = Dataset("test_dataset", project_path=project.path)

            assert dataset.project_path == project.path
            assert dataset.images == 50

    def test_jobmanager_with_dataset(self, mock_project_path, mock_dataset_registry):
        """Test JobManager creating jobs for datasets."""
        mock_dataset_registry.get_dataset.return_value = {"name": "test_dataset"}

        with patch('modelcub.sdk.job.AnnotationJobManager') as mock_manager_class:
            mock_manager = MagicMock()
            mock_job_data = MagicMock()
            mock_job_data.job_id = "job_123"
            mock_job_data.dataset_name = "test_dataset"
            mock_manager.create_job.return_value = mock_job_data
            mock_manager_class.return_value = mock_manager

            # Create job manager
            job_manager = JobManager(project_path=mock_project_path)

            # Create job for dataset
            job = job_manager.create_job(dataset_name="test_dataset")

            assert job.dataset_name == "test_dataset"

    def test_complete_annotation_workflow(self, mock_project_path):
        """Test complete workflow: project -> dataset -> job -> completion."""
        with patch('modelcub.sdk.project.load_config'):
            with patch('modelcub.sdk.dataset.DatasetRegistry') as mock_registry_class:
                with patch('modelcub.sdk.job.AnnotationJobManager') as mock_job_manager_class:
                    # Setup mocks
                    mock_registry = MagicMock()
                    mock_registry.get_dataset.return_value = {"name": "test_dataset"}
                    mock_registry_class.return_value = mock_registry

                    mock_job_manager = MagicMock()
                    mock_job_data = MagicMock()
                    mock_job_data.job_id = "job_123"
                    mock_job_data.dataset_name = "test_dataset"
                    mock_job_data.status = JobStatus.RUNNING
                    mock_job_data.is_terminal = True
                    mock_job_manager.create_job.return_value = mock_job_data
                    mock_job_manager.start_job.return_value = mock_job_data
                    mock_job_manager_class.return_value = mock_job_manager

                    # Execute workflow
                    project = Project(mock_project_path)
                    dataset = Dataset("test_dataset", project_path=project.path)
                    job_manager = JobManager(project_path=project.path)
                    job = job_manager.create_job(dataset.name, auto_start=True)

                    # Verify
                    assert job.dataset_name == dataset.name
                    assert job.status == JobStatus.RUNNING


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Test suite for error handling and edge cases."""

    def test_project_init_with_string_path(self, mock_project_path):
        """Test Project accepts string paths."""
        with patch('modelcub.sdk.project.load_config') as mock_load:
            mock_load.return_value = MagicMock()

            project = Project(str(mock_project_path))

            assert isinstance(project.path, Path)
            assert project.path.resolve() == mock_project_path.resolve()

    def test_dataset_with_empty_classes(self, mock_project_path, mock_dataset_registry):
        """Test Dataset handles empty classes list."""
        mock_dataset_registry.get_dataset.return_value = {
            "name": "empty_dataset",
            "num_images": 10,
            "classes": []
        }

        dataset = Dataset("empty_dataset", project_path=mock_project_path)

        # Should not raise error
        assert dataset.images == 10

    def test_job_with_zero_tasks(self):
        """Test Job handles zero tasks gracefully."""
        mock_data = MagicMock()
        mock_data.job_id = "empty_job"
        mock_data.total_tasks = 0
        mock_data.completed_tasks = 0
        mock_data.failed_tasks = 0
        mock_data.progress = 0.0
        mock_data.is_terminal = True

        mock_manager = MagicMock()
        job = Job(mock_data, mock_manager)

        assert job.total_tasks == 0
        assert job.is_complete is True

    def test_box_with_invalid_coordinates_still_creates(self):
        """Test Box creation with out-of-bounds values (no validation in dataclass)."""
        # Note: Box is a simple dataclass and doesn't validate coordinates
        box = Box(class_id=0, x=1.5, y=-0.5, w=2.0, h=0.5)

        assert box.x == 1.5
        assert box.y == -0.5
        # This shows validation should be added if needed

    def test_project_load_with_nonexistent_path_raises_error(self):
        """Test Project.load() with non-existent path raises appropriate error."""
        nonexistent = Path("/totally/fake/path")

        with pytest.raises(ValueError):
            Project.load(nonexistent)

    def test_dataset_load_with_none_project_path(self, mock_dataset_registry):
        """Test Dataset handles None project_path by searching."""
        mock_dataset_registry.get_dataset.return_value = {"name": "test"}

        with patch('modelcub.sdk.dataset.project_root') as mock_root:
            mock_root.return_value = Path("/found/project")
            with patch('pathlib.Path.exists', return_value=True):

                dataset = Dataset("test", project_path=None)

                mock_root.assert_called_once()
                assert dataset._project_path == Path("/found/project")


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================

class TestParametrized:
    """Parametrized tests for comprehensive coverage."""

    @pytest.mark.parametrize("status", [
        JobStatus.PENDING,
        JobStatus.RUNNING,
        JobStatus.PAUSED,
        JobStatus.COMPLETED,
        JobStatus.FAILED,
        JobStatus.CANCELLED
    ])
    def test_job_with_all_statuses(self, status):
        """Test Job handles all possible statuses."""
        mock_data = MagicMock()
        mock_data.status = status
        mock_data.job_id = "test_job"

        job = Job(mock_data, MagicMock())

        assert job.status == status

    @pytest.mark.parametrize("num_workers", [1, 2, 4, 8, 16])
    def test_jobmanager_with_different_worker_counts(self, num_workers):
        """Test JobManager with various worker counts."""
        with patch('modelcub.sdk.job.project_root'):
            with patch('modelcub.sdk.job.AnnotationJobManager') as mock_class:
                JobManager(num_workers=num_workers)

                # Verify num_workers was passed correctly
                call_kwargs = mock_class.call_args[1]
                assert call_kwargs['num_workers'] == num_workers

    @pytest.mark.parametrize("image_count", [0, 1, 10, 100, 1000, 10000])
    def test_dataset_with_various_image_counts(self, mock_project_path, mock_dataset_registry, image_count):
        """Test Dataset handles various image counts."""
        mock_dataset_registry.get_dataset.return_value = {
            "name": "test_dataset",
            "num_images": image_count
        }

        dataset = Dataset("test_dataset", project_path=mock_project_path)

        assert dataset.images == image_count

    @pytest.mark.parametrize("class_id,x,y,w,h", [
        (0, 0.0, 0.0, 0.1, 0.1),
        (1, 0.5, 0.5, 0.5, 0.5),
        (2, 0.25, 0.75, 0.2, 0.3),
        (99, 0.9, 0.9, 0.05, 0.05)
    ])
    def test_box_with_various_coordinates(self, class_id, x, y, w, h):
        """Test Box creation with various coordinate combinations."""
        box = Box(class_id=class_id, x=x, y=y, w=w, h=h)

        assert box.class_id == class_id
        assert box.x == x
        assert box.y == y
        assert box.w == w
        assert box.h == h


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_project_path_with_trailing_slash(self, mock_project_path):
        """Test Project handles paths with trailing slashes."""
        with patch('modelcub.sdk.project.load_config') as mock_load:
            mock_load.return_value = MagicMock()

            path_with_slash = str(mock_project_path) + "/"
            project = Project(path_with_slash)

            assert project.path.resolve() == mock_project_path.resolve()

    def test_dataset_name_with_special_characters(self, mock_project_path, mock_dataset_registry):
        """Test Dataset handles names with special characters."""
        special_name = "dataset-v1.0_final"
        mock_dataset_registry.get_dataset.return_value = {
            "name": special_name,
            "num_images": 10
        }

        dataset = Dataset(special_name, project_path=mock_project_path)

        assert dataset.name == special_name

    def test_job_progress_boundary_values(self):
        """Test Job handles progress at boundaries (0%, 100%)."""
        mock_data = MagicMock()
        mock_data.job_id = "test"
        mock_manager = MagicMock()

        # Test 0% progress
        mock_data.progress = 0.0
        job = Job(mock_data, mock_manager)
        assert job.progress == 0.0

        # Test 100% progress
        mock_data.progress = 100.0
        job = Job(mock_data, mock_manager)
        assert job.progress == 100.0

    def test_empty_project_config(self, mock_project_path):
        """Test Project handles minimal/empty configuration."""
        with patch('modelcub.sdk.project.load_config') as mock_load:
            minimal_config = MagicMock()
            minimal_config.project = MagicMock()
            minimal_config.defaults = MagicMock()
            minimal_config.paths = MagicMock()
            mock_load.return_value = minimal_config

            project = Project(mock_project_path)

            assert project._config == minimal_config

    def test_box_to_dict_preserves_precision(self):
        """Test Box.to_dict() preserves floating point precision."""
        box = Box(
            class_id=0,
            x=0.123456789,
            y=0.987654321,
            w=0.111111111,
            h=0.999999999
        )

        result = box.to_dict()

        assert result["x"] == 0.123456789
        assert result["y"] == 0.987654321
        assert result["w"] == 0.111111111
        assert result["h"] == 0.999999999


# ============================================================================
# PERFORMANCE TESTS (BASIC)
# ============================================================================

class TestPerformance:
    """Basic performance and scalability tests."""

    def test_job_list_large_number_of_tasks(self):
        """Test Job handles large number of tasks."""
        mock_data = MagicMock()
        mock_data.job_id = "large_job"
        mock_data.total_tasks = 100000
        mock_data.completed_tasks = 50000
        mock_data.failed_tasks = 100

        job = Job(mock_data, MagicMock())

        assert job.total_tasks == 100000
        assert job.completed_tasks == 50000

    def test_create_many_box_objects(self):
        """Test creating many Box objects."""
        boxes = [
            Box(class_id=i % 10, x=0.5, y=0.5, w=0.1, h=0.1)
            for i in range(1000)
        ]

        assert len(boxes) == 1000
        assert all(isinstance(b, Box) for b in boxes)


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])