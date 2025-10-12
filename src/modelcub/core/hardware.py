"""Hardware detection and configuration."""
from __future__ import annotations
import sys
import os
from pathlib import Path


def detect_device() -> str:
    """
    Detect the best available device for training/inference.

    Priority:
    1. CUDA (NVIDIA GPU) - Best performance for most cases
    2. MPS (Apple Silicon) - Good performance on M1/M2/M3
    3. CPU - Always available fallback

    Returns:
        str: Device string ("cuda", "mps", or "cpu")
    """
    try:
        import torch

        # Check for CUDA (NVIDIA GPU)
        if torch.cuda.is_available():
            return "cuda"

        # Check for MPS (Apple Silicon)
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"

        # Fallback to CPU
        return "cpu"

    except ImportError:
        # PyTorch not installed, default to CPU
        return "cpu"
    except Exception:
        # Any other error, default to CPU
        return "cpu"


def check_gpu_availability() -> tuple[bool, str]:
    """
    Check if GPU/CUDA is available for training.

    Returns:
        tuple: (has_gpu: bool, message: str)
    """
    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            return True, f"GPU detected: {device_name}"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return True, "Apple Silicon GPU (MPS) detected"
        else:
            return False, "No GPU detected (CUDA or MPS)"
    except ImportError:
        return False, "PyTorch not installed"
    except Exception as e:
        return False, f"GPU check failed: {e}"


def is_warning_suppressed() -> bool:
    """Check if GPU warning has been suppressed for this session."""
    return os.environ.get("MODELCUB_SUPPRESS_GPU_WARNING") == "1"


def suppress_warning() -> None:
    """Suppress GPU warning for the current terminal session."""
    os.environ["MODELCUB_SUPPRESS_GPU_WARNING"] = "1"


def warn_cpu_mode() -> None:
    """
    Print a warning that operations will run on CPU.
    Only shown when inside a ModelCub project and not suppressed.
    """
    if is_warning_suppressed():
        return

    has_gpu, msg = check_gpu_availability()

    if not has_gpu:
        # Yellow warning text using ANSI codes (cross-platform)
        warning = (
            f"\n⚠️  WARNING: {msg}\n"
            f"   Training and inference will run on CPU, which may be slow.\n"
            f"   Install CUDA-enabled PyTorch for GPU acceleration.\n"
            f"   To suppress this warning: modelcub --suppress-absent-gpu\n"
        )
        # Use stderr for warnings to not interfere with command output
        print(warning, file=sys.stderr)


def is_inside_project() -> bool:
    """Check if current working directory is inside a ModelCub project."""
    cwd = Path.cwd().resolve()
    for p in [cwd] + list(cwd.parents):
        if (p / "modelcub.yaml").exists():
            return True
    return False