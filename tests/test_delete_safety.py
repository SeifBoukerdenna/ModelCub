# tests/test_delete_safety.py
from pathlib import Path
from modelcub.services.project_service import (
    init_project, delete_project,
    InitProjectRequest, DeleteProjectRequest
)

def test_delete_safety_prevents_repo_deletion(tmp_path, monkeypatch):
    """Safety check should prevent deleting directories that look like repos."""
    monkeypatch.chdir(tmp_path)

    # Create a project with repo-like files
    init_project(InitProjectRequest(path=".", name="test", force=False))

    # Add repo markers
    (tmp_path / ".git").mkdir()
    (tmp_path / "pyproject.toml").write_text("name = 'test'")
    (tmp_path / "src").mkdir()

    # Try to delete - should be blocked
    code, msg = delete_project(DeleteProjectRequest(target=".", yes=True))

    assert code == 2
    assert "SAFETY" in msg
    assert "development files" in msg or "repository" in msg.lower()
    assert tmp_path.exists()  # Directory still exists

def test_delete_works_for_normal_projects(tmp_path, monkeypatch):
    """Normal projects without repo markers should delete successfully."""
    monkeypatch.chdir(tmp_path)

    # Create a normal project (no repo markers)
    init_project(InitProjectRequest(path=".", name="test", force=False))

    # Should delete successfully
    code, msg = delete_project(DeleteProjectRequest(target=".", yes=True))

    assert code == 0
    assert "Deleted project directory" in msg
    assert not tmp_path.exists()

def test_delete_allows_single_repo_marker(tmp_path, monkeypatch):
    """Projects with just ONE repo marker (edge case) should still delete."""
    monkeypatch.chdir(tmp_path)

    init_project(InitProjectRequest(path=".", name="test", force=False))

    # Add just ONE repo marker (threshold is 2+)
    (tmp_path / ".git").mkdir()

    # Should delete (only 1 marker)
    code, msg = delete_project(DeleteProjectRequest(target=".", yes=True))

    assert code == 0
    assert "Deleted project directory" in msg
    assert not tmp_path.exists()