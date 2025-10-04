# tests/test_cli_hardware_warning.py
import os
from pathlib import Path
from modelcub.core.hardware import is_inside_project, check_gpu_availability, suppress_warning, is_warning_suppressed

def test_is_inside_project_detection(tmp_path, monkeypatch):
    """Test that we can detect if we're inside a project."""
    monkeypatch.chdir(tmp_path)
    assert not is_inside_project()

    (tmp_path / "modelcub.yaml").write_text("project: test")
    assert is_inside_project()

def test_check_gpu_returns_tuple():
    """Test GPU check returns the right format."""
    has_gpu, msg = check_gpu_availability()
    assert isinstance(has_gpu, bool)
    assert isinstance(msg, str)

def test_suppress_warning_sets_env(monkeypatch):
    """Test that suppress_warning sets environment variable."""
    # Clean env
    monkeypatch.delenv("MODELCUB_SUPPRESS_GPU_WARNING", raising=False)

    assert not is_warning_suppressed()

    suppress_warning()
    assert is_warning_suppressed()
    assert os.environ.get("MODELCUB_SUPPRESS_GPU_WARNING") == "1"