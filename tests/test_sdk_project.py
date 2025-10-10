"""
Tests for ModelCub Project SDK.
"""
import pytest
from pathlib import Path
from modelcub import Project
from modelcub.core.config import load_config


def test_project_init(tmp_path, monkeypatch):
    """Test Project.init() creates project."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")

    assert project.name == "test-sdk"
    assert project.path == (tmp_path / "test-sdk").resolve()
    assert project.path.exists()
    assert (project.path / ".modelcub").exists()


def test_project_init_with_force(tmp_path, monkeypatch):
    """Test Project.init() with force flag."""
    monkeypatch.chdir(tmp_path)

    # First init
    project1 = Project.init("test-sdk")
    assert project1.name == "test-sdk"

    # Second init without force should fail
    with pytest.raises(RuntimeError, match="Failed to initialize"):
        Project.init("test-sdk", force=False)

    # With force should succeed
    project2 = Project.init("test-sdk", force=True)
    assert project2.name == "test-sdk"


def test_project_load(tmp_path, monkeypatch):
    """Test Project.load() loads existing project."""
    monkeypatch.chdir(tmp_path)

    # Create project
    project1 = Project.init("test-sdk")
    original_name = project1.name

    # Load it
    project2 = Project.load("test-sdk")

    assert project2.name == original_name
    assert project2.path == project1.path


def test_project_load_invalid_raises(tmp_path, monkeypatch):
    """Test Project.load() raises on invalid project."""
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ValueError, match="Not a valid ModelCub project"):
        Project.load("nonexistent")


def test_project_exists(tmp_path, monkeypatch):
    """Test Project.exists() checks validity."""
    monkeypatch.chdir(tmp_path)

    assert not Project.exists("test-sdk")

    Project.init("test-sdk")

    assert Project.exists("test-sdk")


def test_project_properties(tmp_path, monkeypatch):
    """Test project property accessors."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")

    assert project.name == "test-sdk"
    assert isinstance(project.created, str)
    assert project.version == "1.0.0"


def test_config_access(tmp_path, monkeypatch):
    """Test config access through project."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")

    # Access config
    assert project.config.defaults.device == "cuda"
    assert project.config.defaults.batch_size == 16
    assert project.config.defaults.image_size == 640


def test_config_modification(tmp_path, monkeypatch):
    """Test modifying and saving config."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")

    # Modify
    project.config.defaults.batch_size = 32
    project.config.defaults.device = "cpu"

    # Save
    project.save_config()

    # Reload and verify
    project2 = Project.load("test-sdk")
    assert project2.config.defaults.batch_size == 32
    assert project2.config.defaults.device == "cpu"


def test_get_config_helper(tmp_path, monkeypatch):
    """Test get_config helper method."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")

    assert project.get_config("defaults.device") == "cuda"
    assert project.get_config("defaults.batch_size") == 16
    assert project.get_config("project.name") == "test-sdk"
    assert project.get_config("nonexistent.key", "default") == "default"


def test_set_config_helper(tmp_path, monkeypatch):
    """Test set_config helper method."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")

    project.set_config("defaults.batch_size", 64)
    project.save_config()

    project2 = Project.load("test-sdk")
    assert project2.get_config("defaults.batch_size") == 64


def test_set_config_invalid_path_raises(tmp_path, monkeypatch):
    """Test set_config with invalid path raises."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")

    with pytest.raises(ValueError, match="Invalid config path"):
        project.set_config("nonexistent.path", "value")


def test_registry_access(tmp_path, monkeypatch):
    """Test accessing registries through project."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")

    # Access dataset registry
    datasets = project.datasets.list_datasets()
    assert isinstance(datasets, list)
    assert len(datasets) == 0

    # Access run registry
    runs = project.runs.list_runs()
    assert isinstance(runs, list)
    assert len(runs) == 0


def test_path_properties(tmp_path, monkeypatch):
    """Test path property accessors."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")

    assert project.modelcub_dir == project.path / ".modelcub"
    assert project.data_dir == project.path / "data"
    assert project.datasets_dir == project.path / "data" / "datasets"
    assert project.runs_dir == project.path / "runs"
    assert project.reports_dir == project.path / "reports"
    assert project.cache_dir == project.path / ".modelcub" / "cache"
    assert project.backups_dir == project.path / ".modelcub" / "backups"
    assert project.history_dir == project.path / ".modelcub" / "history"

    # Verify they exist
    assert project.modelcub_dir.exists()
    assert project.datasets_dir.exists()
    assert project.runs_dir.exists()
    assert project.reports_dir.exists()


def test_project_delete(tmp_path, monkeypatch):
    """Test project.delete() removes project."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")
    project_path = project.path

    assert project_path.exists()

    project.delete(confirm=True)

    assert not project_path.exists()


def test_project_delete_requires_confirm(tmp_path, monkeypatch):
    """Test project.delete() requires confirmation."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")

    with pytest.raises(RuntimeError, match="Must set confirm=True"):
        project.delete(confirm=False)

    # Project should still exist
    assert project.path.exists()


def test_context_manager_saves_config(tmp_path, monkeypatch):
    """Test using project as context manager auto-saves."""
    monkeypatch.chdir(tmp_path)

    Project.init("test-sdk")

    # Use as context manager
    with Project.load("test-sdk") as project:
        project.config.defaults.workers = 99

    # Load again and verify it was saved
    project2 = Project.load("test-sdk")
    assert project2.config.defaults.workers == 99


def test_repr_and_str(tmp_path, monkeypatch):
    """Test string representations."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")

    repr_str = repr(project)
    assert "test-sdk" in repr_str
    assert "Project" in repr_str

    str_str = str(project)
    assert "test-sdk" in str_str
    assert "ModelCub" in str_str


def test_reload_config(tmp_path, monkeypatch):
    """Test reload_config() refreshes from disk."""
    monkeypatch.chdir(tmp_path)

    project = Project.init("test-sdk")

    # Modify in memory
    project.config.defaults.batch_size = 999

    # Don't save, just reload
    project.reload_config()

    # Should be back to default
    assert project.config.defaults.batch_size == 16


def test_integration_workflow(tmp_path, monkeypatch):
    """Test complete workflow with SDK."""
    monkeypatch.chdir(tmp_path)

    # 1. Create project
    project = Project.init("my-project")
    assert project.name == "my-project"

    # 2. Modify config
    project.config.defaults.batch_size = 32
    project.config.defaults.device = "cpu"
    project.save_config()

    # 3. Check paths
    assert project.datasets_dir.exists()
    assert project.runs_dir.exists()

    # 4. Load project again
    project2 = Project.load("my-project")
    assert project2.config.defaults.batch_size == 32
    assert project2.config.defaults.device == "cpu"

    # 5. Use context manager
    with Project.load("my-project") as p:
        p.config.defaults.image_size = 1024

    # 6. Verify changes persisted
    project3 = Project.load("my-project")
    assert project3.config.defaults.image_size == 1024

    # 7. Clean up
    project3.delete(confirm=True)
    assert not Project.exists("my-project")