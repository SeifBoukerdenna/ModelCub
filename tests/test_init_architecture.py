"""
Test the new Timeline architecture for project initialization.
"""
from pathlib import Path
from modelcub.services.project_service import init_project, delete_project, InitProjectRequest, DeleteProjectRequest
from modelcub.core.config import load_config
from modelcub.core.registries import DatasetRegistry, RunRegistry


def test_new_architecture_init(tmp_path, monkeypatch):
    """Test that init creates the full Timeline architecture."""
    monkeypatch.chdir(tmp_path)

    # Initialize project
    code, msg = init_project(InitProjectRequest(path=".", name="test-project", force=False))
    assert code == 0
    assert "Initialized ModelCub project" in msg

    # Check .modelcub directory exists
    modelcub_dir = tmp_path / ".modelcub"
    assert modelcub_dir.exists()
    assert modelcub_dir.is_dir()

    # Check config.yaml
    config_file = modelcub_dir / "config.yaml"
    assert config_file.exists()

    config = load_config(tmp_path)
    assert config is not None
    assert config.project.name == "test-project"
    assert config.defaults.device == "cuda"
    assert config.defaults.batch_size == 16
    assert config.defaults.image_size == 640
    assert config.paths.data == "data"
    assert config.paths.runs == "runs"
    assert config.paths.reports == "reports"

    # Check registries
    datasets_registry = modelcub_dir / "datasets.yaml"
    runs_registry = modelcub_dir / "runs.yaml"
    assert datasets_registry.exists()
    assert runs_registry.exists()

    # Check history structure
    assert (modelcub_dir / "history" / "commits").is_dir()
    assert (modelcub_dir / "history" / "snapshots").is_dir()

    # Check cache
    assert (modelcub_dir / "cache").is_dir()

    # Check backups
    assert (modelcub_dir / "backups").is_dir()

    # Check data structure
    assert (tmp_path / "data" / "datasets").is_dir()
    assert (tmp_path / "data" / "datasets" / ".gitkeep").exists()

    # Check runs
    assert (tmp_path / "runs").is_dir()
    assert (tmp_path / "runs" / ".gitkeep").exists()

    # Check reports
    assert (tmp_path / "reports").is_dir()
    assert (tmp_path / "reports" / ".gitkeep").exists()

    # Check project files
    assert (tmp_path / "modelcub.yaml").exists()
    assert (tmp_path / ".gitignore").exists()
    assert (tmp_path / "README.md").exists()

    # Verify registries work
    ds_registry = DatasetRegistry(tmp_path)
    assert ds_registry.list_datasets() == []

    run_registry = RunRegistry(tmp_path)
    assert run_registry.list_runs() == []


def test_registry_operations(tmp_path, monkeypatch):
    """Test that registry operations work correctly."""
    monkeypatch.chdir(tmp_path)

    # Initialize
    init_project(InitProjectRequest(path=".", name="test", force=False))

    # Test dataset registry
    ds_registry = DatasetRegistry(tmp_path)

    # Add a dataset
    dataset_info = {
        "id": "test1234",
        "name": "my-dataset",
        "created": "2024-10-10T12:00:00Z",
        "classes": ["cat", "dog"],
        "num_classes": 2
    }
    ds_registry.add_dataset(dataset_info)

    # Verify it was added
    assert ds_registry.exists("my-dataset")
    retrieved = ds_registry.get_dataset("my-dataset")
    assert retrieved["id"] == "test1234"
    assert retrieved["classes"] == ["cat", "dog"]

    # List datasets
    all_datasets = ds_registry.list_datasets()
    assert len(all_datasets) == 1
    assert all_datasets[0]["name"] == "my-dataset"

    # Remove dataset
    ds_registry.remove_dataset("my-dataset")
    assert not ds_registry.exists("my-dataset")
    assert ds_registry.list_datasets() == []


def test_config_persistence(tmp_path, monkeypatch):
    """Test that config can be loaded and modified."""
    monkeypatch.chdir(tmp_path)

    # Initialize
    init_project(InitProjectRequest(path=".", name="test", force=False))

    # Load config
    config = load_config(tmp_path)
    assert config.defaults.batch_size == 16

    # Modify config
    config.defaults.batch_size = 32
    config.defaults.device = "cpu"

    # Save config
    from modelcub.core.config import save_config
    save_config(tmp_path, config)

    # Reload and verify
    config2 = load_config(tmp_path)
    assert config2.defaults.batch_size == 32
    assert config2.defaults.device == "cpu"


def test_project_delete_with_new_structure(tmp_path, monkeypatch):
    """Test that delete works with new .modelcub structure."""
    monkeypatch.chdir(tmp_path)

    # Initialize
    init_project(InitProjectRequest(path=".", name="test", force=False))
    assert (tmp_path / ".modelcub").exists()

    # Delete
    code, msg = delete_project(DeleteProjectRequest(target=".", yes=True))
    assert code == 0
    assert "Deleted project directory" in msg
    assert not tmp_path.exists()


def test_reinit_with_force(tmp_path, monkeypatch):
    """Test that --force allows reinitializing."""
    monkeypatch.chdir(tmp_path)

    # First init
    code, msg = init_project(InitProjectRequest(path=".", name="first", force=False))
    assert code == 0

    config = load_config(tmp_path)
    assert config.project.name == "first"

    # Try reinit without force
    code, msg = init_project(InitProjectRequest(path=".", name="second", force=False))
    assert code == 1
    assert "already initialized" in msg

    # Reinit with force
    code, msg = init_project(InitProjectRequest(path=".", name="second", force=True))
    assert code == 0

    config = load_config(tmp_path)
    assert config.project.name == "second"