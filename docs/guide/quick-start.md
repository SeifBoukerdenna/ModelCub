# Quick Start Guide

Get started with ModelCub in 5 minutes.

## 1. Install

```bash
pip install modelcub
```

## 2. Initialize Project

```bash
modelcub project init my-cv-project
cd my-cv-project
```

Creates this structure:
```
my-cv-project/
├── .modelcub/        # Config, registries, history
├── data/datasets/    # Your datasets
├── runs/             # Training outputs
├── reports/          # Generated reports
└── modelcub.yaml     # Project marker
```

## 3. Add a Dataset

### From YOLO Format

```bash
modelcub dataset add --source ./yolo-data --name production-v1
```

### From Roboflow Export

```bash
modelcub dataset add --source ./roboflow-export.zip --name roboflow-v1
```

### Unlabeled Images (for annotation)

```bash
modelcub dataset add --source ./images/ --name unlabeled-v1
```

## 4. Inspect Dataset

```bash
# List datasets
modelcub dataset list

# Detailed info
modelcub dataset info production-v1
```

Output:
```
📦 Dataset: production-v1

Classes: pill, bottle, box (3 classes)
Images: 847 total
  • train: 677 (80%)
  • val: 119 (14%)
  • test: 51 (6%)

Created: 2025-01-15 14:30:22
Path: data/datasets/production-v1
```

## 5. Manage Classes

```bash
# List classes
modelcub dataset classes list production-v1

# Add class
modelcub dataset classes add production-v1 capsule

# Rename class
modelcub dataset classes rename production-v1 pill tablet

# Remove class
modelcub dataset classes remove production-v1 box --yes
```

## 6. Launch Web UI

```bash
modelcub ui
```

Opens at `http://localhost:8000`

View datasets, browse images, manage classes through the web interface.

## Python SDK Usage

Same workflow in Python:

```python
from modelcub import Project, Dataset

# 1. Initialize project
project = Project.init("my-cv-project")

# 2. Add dataset
dataset = project.import_dataset(source="./photos", name="animals", classes=["bear1", "bear2", "bear3"])

# 3. Inspect
print(f"Dataset: {dataset.name}")
print(f"Classes: {dataset.classes}")
print(f"Images: {dataset.num_images}")
print(f"Splits: train={len(dataset.splits['train'].images)}")

# 4. Get statistics
stats = dataset.stats()
print(f"Class distribution: {stats['class_distribution']}")
print(f"Images per split: {stats['images_per_split']}")

# 5. Manage classes
dataset.add_class("capsule")
dataset.rename_class("pill", "tablet")
dataset.remove_class("box")
```

## Common Workflows

### Import and Inspect

```bash
# Import
modelcub dataset add --source ./data --name bears-v1

# Check what you got
modelcub dataset info bears-v1

# Launch UI to browse
modelcub ui
```

### Multiple Datasets

```bash
# Add multiple datasets
modelcub dataset add --source ./pills --name pills-v1
modelcub dataset add --source ./bottles --name bottles-v1

# List all
modelcub dataset list

# Compare
modelcub dataset info pills-v1
modelcub dataset info bottles-v1
```

### Edit Metadata

```bash
# Rename dataset
modelcub dataset edit pills-v1 --new-name pills-production

# Update classes
modelcub dataset edit pills-v1 --classes "pill,tablet,capsule"
```

### Delete Dataset

```bash
# Safe delete (requires confirmation)
modelcub dataset delete old-dataset

# Force delete
modelcub dataset delete old-dataset --yes
```

## Configuration

View/edit project config:

```bash
# Show all config
modelcub config show

# Get specific value
modelcub config get defaults.batch_size

# Set value
modelcub config set defaults.batch_size 32
```

Config stored in `.modelcub/config.yaml`:
```yaml
project:
  name: my-cv-project

defaults:
  device: cuda
  batch_size: 16
  image_size: 640
  format: yolo

paths:
  data: data
  runs: runs
  reports: reports
```

## Tips

**Start Small**: Import a subset first to verify workflow, then add full dataset.

**Use UI**: Easier to browse images and manage classes visually.

**Check Config**: Run `modelcub config show` to see device, batch size, etc.

**Version Everything**: (Coming soon) Commit datasets after major changes.

## Next Steps

- **[CLI Reference](cli-reference.md)** - All commands
- **[Python SDK](python-sdk.md)** - Programmatic API
- **[Architecture](architecture.md)** - How it works

## Troubleshooting

**"Not a ModelCub project"**: Run `modelcub project init` first.

**Import fails**: Check source path exists and format is correct (YOLO/Roboflow).

**UI won't start**: Port 8000 in use? Try `modelcub ui --port 3000`.

**Permission errors**: Use virtual environment or `pip install --user`.