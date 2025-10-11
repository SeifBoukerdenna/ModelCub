# Installation

ModelCub is lightweight and modular. The core works with minimal dependencies—add extras only when you need them.

## Requirements

- **Python**: 3.9 or higher
- **OS**: Linux, macOS, or Windows
- **GPU**: Optional (CUDA 11.8+ recommended for training)

## Quick Install

### Basic Installation

For dataset management and project setup:

```bash
pip install modelcub
```

This installs the core CLI and Python SDK.

### With Training Support

For model training with Ultralytics YOLO:

```bash
pip install "modelcub[ultra]"
```

### Full Installation

Everything including ONNX export and OpenCV:

```bash
pip install "modelcub[all]"
```

## Installation Options

| Extra | Description | Install |
|-------|-------------|---------|
| `ultra` | Ultralytics YOLO for training | `pip install "modelcub[ultra]"` |
| `onnx` | ONNX export support | `pip install "modelcub[onnx]"` |
| `opencv` | OpenCV for image processing | `pip install "modelcub[opencv]"` |
| `all` | Everything | `pip install "modelcub[all]"` |

## Platform-Specific Setup

### Linux (Ubuntu/Debian)

```bash
# Install Python 3.9+ if needed
sudo apt update
sudo apt install python3.9 python3.9-pip

# Install ModelCub
pip install "modelcub[all]"
```

#### GPU Setup (NVIDIA)

```bash
# Check CUDA version
nvidia-smi

# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install ModelCub
pip install "modelcub[ultra]"
```

### macOS

```bash
# Install via pip
pip3 install "modelcub[all]"
```

::: tip Apple Silicon (M1/M2/M3)
ModelCub works great on Apple Silicon! PyTorch automatically uses Metal Performance Shaders (MPS) for acceleration.
:::

### Windows

```powershell
pip install "modelcub[all]"
```

::: warning Windows PATH
Make sure Python's Scripts folder is in your PATH:
`C:\Users\YourName\AppData\Local\Programs\Python\Python39\Scripts\`
:::

## Verify Installation

```bash
# Check version
modelcub --version

# Show environment info
modelcub about
```

Expected output:

```
ModelCub 1.0.0
Python 3.9.7 on Linux 5.15.0
ultralytics: 8.0.200
torch: 2.0.1
numpy: 1.24.3
opencv-python: 4.8.0
```

## GPU Setup

### NVIDIA CUDA

For GPU-accelerated training:

1. **Check GPU**:
```bash
nvidia-smi
```

2. **Install CUDA PyTorch**:
```bash
# CUDA 11.8
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

3. **Verify GPU access**:
```bash
python -c "import torch; print(torch.cuda.is_available())"
# Should print: True
```

### Apple Silicon (MPS)

PyTorch automatically uses Metal Performance Shaders:

```bash
python -c "import torch; print(torch.backends.mps.is_available())"
# Should print: True
```

### CPU-Only

ModelCub works perfectly on CPU! Training will be slower but all features work:

```bash
pip install "modelcub[all]"
```

ModelCub automatically detects and uses your CPU.

## Virtual Environments

We strongly recommend using virtual environments:

```bash
# Create virtual environment
python -m venv modelcub-env

# Activate (Linux/macOS)
source modelcub-env/bin/activate

# Activate (Windows)
modelcub-env\Scripts\activate

# Install ModelCub
pip install "modelcub[all]"

# When done
deactivate
```

## Development Installation

For contributing or using the latest development version:

```bash
# Clone repository
git clone https://github.com/SeifBoukerdenna/ModelCub.git
cd ModelCub

# Install in editable mode with dev dependencies
pip install -e ".[dev,all]"

# Run tests
pytest
```

## Troubleshooting

### ImportError: No module named 'modelcub'

Check Python and pip versions:

```bash
python --version
pip --version

# Reinstall
pip install --upgrade modelcub
```

### CUDA not detected

If PyTorch doesn't detect your GPU:

1. **Verify CUDA drivers**:
```bash
nvidia-smi
```

2. **Reinstall PyTorch** with correct CUDA version:
```bash
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

3. **Test detection**:
```bash
modelcub about
```

### Permission errors

Use `--user` flag or virtual environments:

```bash
# Install for current user
pip install --user modelcub

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install modelcub
```

## Next Steps

Now that ModelCub is installed:

1. **[Quick Start](/guide/quick-start)** - Create your first project
2. **[CLI Reference](/cli/reference)** - Explore all commands
3. **[Python SDK](/api/overview)** - Learn the programmatic API

::: tip Need Help?
- [GitHub Discussions](https://github.com/SeifBoukerdenna/ModelCub/discussions)
- [Report Issues](https://github.com/SeifBoukerdenna/ModelCub/issues)
:::