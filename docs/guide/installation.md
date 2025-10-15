# Installation Guide

## System Requirements

- **Python**: 3.9 or higher
- **OS**: Linux, macOS, or Windows
- **GPU**: Optional (CUDA 11.8+ for NVIDIA, MPS for Apple Silicon)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 2GB for installation, more for datasets

## Quick Install

```bash
pip install modelcub
```

That's it. ModelCub and all dependencies are installed.

## Install Options

### Full Installation (Recommended)

Includes all optional dependencies for UI, training, and exports:

```bash
pip install "modelcub[all]"
```

### Minimal Installation

Core CLI and SDK only (no UI, no training):

```bash
pip install modelcub
```

### Development Installation

For contributing or using latest features:

```bash
git clone https://github.com/SeifBoukerdenna/ModelCub.git
cd ModelCub
pip install -e ".[dev,all]"
```

## GPU Setup

### NVIDIA CUDA

ModelCub automatically detects CUDA. Verify:

```bash
python -c "import torch; print(torch.cuda.is_available())"
# Should print: True
```

If False, install PyTorch with CUDA:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Apple Silicon (MPS)

Automatic on M Macs. Verify:

```bash
python -c "import torch; print(torch.backends.mps.is_available())"
# Should print: True
```

### CPU Only

Works perfectly, just slower for training:

```bash
pip install modelcub
```

## Virtual Environment (Recommended)

Isolate ModelCub from system Python:

```bash
# Create environment
python -m venv modelcub-env

# Activate (Linux/macOS)
source modelcub-env/bin/activate

# Activate (Windows)
modelcub-env\Scripts\activate

# Install
pip install "modelcub[all]"

# When done
deactivate
```

## Verify Installation

```bash
# Check version
modelcub --version

# Check system info
modelcub config show

# Should show:
# - Python version
# - PyTorch version
# - CUDA/MPS availability
# - Device selection
```

## Troubleshooting

### Command Not Found

If `modelcub` command not found:

```bash
# Find Python scripts directory
python -c "import site; print(site.USER_BASE + '/bin')"

# Add to PATH (Linux/macOS, add to ~/.bashrc or ~/.zshrc)
export PATH="$PATH:/path/from/above"

# Or use python -m
python -m modelcub --version
```

### Import Errors

```bash
# Reinstall
pip uninstall modelcub
pip install --upgrade "modelcub[all]"

# Or use --force-reinstall
pip install --force-reinstall modelcub
```

### CUDA Not Detected

```bash
# Verify CUDA drivers
nvidia-smi

# Reinstall PyTorch with correct CUDA version
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Permission Errors

```bash
# Install for user only
pip install --user modelcub

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install modelcub
```

## Next Steps

- [Quick Start](quick-start.md) - Create your first project
- [CLI Reference](cli-reference.md) - Learn all commands
- [Python SDK](python-sdk.md) - Use programmatically

## Updating

```bash
# Update to latest version
pip install --upgrade modelcub

# Check current version
modelcub --version
```

## Uninstall

```bash
pip uninstall modelcub
```

Projects and data are not removed. Delete manually if needed.