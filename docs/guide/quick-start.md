# Quick Start

Get started with ModelCub in 5 minutes. We'll create a project, add a dataset, fix issues, and train a model.

## Prerequisites

Make sure ModelCub is installed:

```bash
pip install "modelcub[ultra]"
```

See the [Installation Guide](/guide/installation) for details.

## Step 1: Create Project

Initialize a new ModelCub project:

```bash
modelcub init my-cv-project
cd my-cv-project
```

This creates the project structure:

```
my-cv-project/
├── .modelcub/      # Configuration and metadata
├── data/datasets/  # Your datasets
├── runs/           # Training outputs
├── reports/        # Generated reports
└── modelcub.yaml   # Project marker
```

## Step 2: Add a Dataset

Add a built-in demo dataset:

```bash
modelcub dataset add --source cub --name bears
```

This downloads and imports a small bears classification dataset.

::: tip Using Your Own Data
To import your own YOLO dataset:
```bash
modelcub dataset add --path ./my-yolo-data --name custom
```
:::

## Step 3: Validate Dataset

Check for issues:

```bash
modelcub dataset validate bears
```

Output shows:
- Dataset health score
- Number of images per split
- Detected issues (corrupt images, invalid labels, etc.)

## Step 4: Fix Issues

Automatically repair common problems:

```bash
modelcub dataset fix bears --auto
```

ModelCub will:
- Remove corrupt images
- Fix out-of-bounds boxes
- Remove duplicates
- Generate a detailed HTML report

## Step 5: Train a Model

Train with auto-optimization:

```bash
modelcub train --dataset bears --auto
```

Auto mode:
- Detects your GPU and picks optimal settings
- Sets batch size based on dataset size
- Enables early stopping
- Uses all available GPUs

Or customize:

```bash
modelcub train \
  --dataset bears \
  --model yolov11n \
  --epochs 50 \
  --batch-size 16
```

## Step 6: Evaluate Results

Check your model's performance:

```bash
modelcub evaluate <run-name>
```

Shows:
- mAP50 and mAP50-95
- Precision, Recall, F1 per class
- Confusion matrix
- Inference speed

## Step 7: Export Model

Export for deployment:

```bash
modelcub export <run-name> --format onnx
```

Supported formats:
- ONNX (cross-platform)
- TensorRT (NVIDIA)
- TorchScript (PyTorch)
- CoreML (Apple)

## Using the Python SDK

Prefer notebooks? Here's the same workflow in Python:

```python
from modelcub import Project, Dataset, Model

# Step 1: Create project
project = Project.init("my-cv-project")

# Step 2: Add dataset
dataset = Dataset.from_path("./data", name="bears")

# Step 3: Validate
report = dataset.validate()
print(f"Health Score: {report.health_score}/100")

# Step 4: Fix issues
fix_report = dataset.fix(auto=True)
print(f"Fixed {fix_report.total_fixed} issues")

# Step 5: Train
model = Model("yolov11n", task="detect")
run = model.train(dataset=dataset, auto=True)

# Step 6: Evaluate
results = run.evaluate(split="val")
print(f"mAP50: {results.map50:.3f}")

# Step 7: Export
run.export(format="onnx", output="model.onnx")
```

## Next Steps

### Explore Key Features

- **[Version Control](/guide/version-control)** - Git-like workflows for datasets
- **[Dataset Diff](/guide/dataset-diff)** - Visual comparisons between versions
- **[Auto-Fix](/guide/auto-fix)** - Deep dive into automatic repairs

### CLI Reference

- **[modelcub dataset](/cli/dataset)** - Dataset management commands
- **[modelcub train](/cli/train)** - Training options and flags
- **[modelcub export](/cli/export)** - Export formats and settings

### Python SDK

- **[Project API](/api/project)** - Project management
- **[Dataset API](/api/dataset)** - Dataset operations
- **[Model API](/api/model)** - Training and evaluation

## Common Tasks

### Import Your Own YOLO Dataset

```bash
modelcub dataset add --path ./yolo-data --name production-v1
```

### Import Roboflow Export

```bash
modelcub dataset add --path ./roboflow-export.zip --name roboflow-data
```

### Version Your Dataset

```bash
# Commit current state
modelcub commit -m "Initial import"

# Make changes, then commit
modelcub commit -m "Added 500 images"

# Compare versions
modelcub diff v1 v2 --visual
```

### Train on Multiple GPUs

```bash
# ModelCub automatically uses all available GPUs
modelcub train --dataset bears --auto

# Or specify devices
modelcub train --dataset bears --device cuda:0,1,2,3
```

## Tips

::: tip Start Small
Use a subset of your dataset first to verify the workflow. ModelCub makes it easy to add more data later and retrain.
:::

::: tip Use Auto Mode
The `--auto` flag is great for getting started. You can always customize later once you understand your dataset.
:::

::: tip Version Everything
Get in the habit of committing datasets after major changes. Future you will thank past you.
:::

## Need Help?

- **[GitHub Discussions](https://github.com/SeifBoukerdenna/ModelCub/discussions)** - Ask questions
- **[GitHub Issues](https://github.com/SeifBoukerdenna/ModelCub/issues)** - Report bugs
- **[Documentation](/guide/introduction)** - Full guides and references

---

**Congratulations!** 🎉 You've trained your first model with ModelCub.