# tests/test_core_hardware.py
import sys
from pathlib import Path
from modelcub.core.hardware import check_gpu_availability, warn_cpu_mode, is_inside_project

def test_check_gpu_without_torch(monkeypatch):
    """Test GPU check when PyTorch is not installed."""
    # Remove torch from sys.modules to simulate not installed
    sys.modules.pop("torch", None)

    # Force import to fail
    import builtins
    real_import = builtins.__import__

    def mock_import(name, *args, **kwargs):
        if name == "torch":
            raise ImportError("No module named 'torch'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", mock_import)

    has_gpu, msg = check_gpu_availability()
    assert has_gpu is False
    assert "PyTorch not installed" in msg

def test_check_gpu_with_fake_torch_no_cuda(monkeypatch):
    """Test GPU check with PyTorch installed but no CUDA."""
    class FakeTorch:
        @staticmethod
        def cuda_is_available():
            return False

        class cuda:
            @staticmethod
            def is_available():
                return False

    sys.modules["torch"] = FakeTorch()

    try:
        has_gpu, msg = check_gpu_availability()
        assert has_gpu is False
        assert "No CUDA-capable GPU" in msg
    finally:
        sys.modules.pop("torch", None)

def test_check_gpu_with_fake_torch_with_cuda(monkeypatch):
    """Test GPU check with PyTorch and CUDA available."""
    class FakeTorch:
        class cuda:
            @staticmethod
            def is_available():
                return True

            @staticmethod
            def get_device_name(idx):
                return "NVIDIA GeForce RTX 3090"

    sys.modules["torch"] = FakeTorch()

    try:
        has_gpu, msg = check_gpu_availability()
        assert has_gpu is True
        assert "GPU detected" in msg
        assert "RTX 3090" in msg
    finally:
        sys.modules.pop("torch", None)

def test_is_inside_project(tmp_path, monkeypatch):
    """Test project detection."""
    monkeypatch.chdir(tmp_path)

    # Not in a project
    assert is_inside_project() is False

    # Create modelcub.yaml
    (tmp_path / "modelcub.yaml").write_text("project: test\n")
    assert is_inside_project() is True

    # Also works in subdirectories
    subdir = tmp_path / "data" / "raw"
    subdir.mkdir(parents=True)
    monkeypatch.chdir(subdir)
    assert is_inside_project() is True


def test_warn_cpu_mode_with_gpu(monkeypatch, capsys):
    """No warning when GPU is available."""
    class FakeTorch:
        class cuda:
            @staticmethod
            def is_available():
                return True

            @staticmethod
            def get_device_name(idx):
                return "NVIDIA GPU"

    sys.modules["torch"] = FakeTorch()

    try:
        warn_cpu_mode()
        captured = capsys.readouterr()
        # No warning should be printed when GPU is available
        assert "WARNING" not in captured.err
    finally:
        sys.modules.pop("torch", None)