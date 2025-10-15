# Introduction

ModelCub is an open-source MLOps toolkit for computer vision. Train models locally, version datasets like code, and deploy anywhere—without cloud bills or vendor lock-in.

## What is ModelCub?

**The simple answer**: ModelCub handles the boring parts of computer vision so you can focus on building models.

It manages datasets, fixes common issues automatically, versions everything for reproducibility, and trains models with sensible defaults. All on your machine, with zero cloud costs.

## The Problem

If you've built a CV product, you know the pain:

**Dataset Hell**
Corrupt images, invalid YOLO labels, duplicate files. Hours spent debugging instead of training.

**Cloud Costs**
Roboflow wants $8k/month just to manage datasets. Costs add up fast for startups and research labs.

**Privacy Walls**
Medical imaging, pharma data, manufacturing datasets—can't touch external servers.

**Reproducibility**
"It worked on my machine" because datasets aren't versioned and experiments aren't tracked.

## The Solution

ModelCub gives you:

**🩹 Auto-Fix**: One command detects and repairs corrupt images, invalid labels, duplicates, and format issues.

**🔄 Version Control**: Git-like workflows for datasets. Commit, diff, rollback—with visual comparisons.

**🚀 Smart Training**: Auto-optimize settings based on your GPU. Multi-GPU support and early stopping included.

**💰 Zero Cost**: Run 100% locally. No subscriptions, no surprises.

**🔒 Privacy**: Your data never leaves your machine. Perfect for HIPAA, GDPR, and air-gapped environments.

## The Workflow

```bash
# Install
pip install modelcub

# Create project
modelcub init my-project
cd my-project

# Add dataset
modelcub dataset add --path ./data --name v1

# Fix issues
modelcub dataset fix v1 --auto

# Train
modelcub train --dataset v1 --auto

# Export
modelcub export my-run --format onnx
```

That's it. No cloud accounts, no credit cards, no complexity.

## Python SDK

Prefer notebooks? The Python SDK gives you full programmatic control:

```python
from modelcub import Project, Dataset, Model

# Initialize
project = Project.init("my-project")
dataset = project.import_dataset("./data", name="v1")

# Fix and validate
dataset.fix(auto=True)

# Train
model = Model("yolov11n", task="detect")
run = project.train(model=model, dataset=dataset, auto=True)

# Results
print(f"mAP50: {run.evaluate().map50:.3f}")
```

## Who Uses ModelCub?

**Medical Imaging Teams**
HIPAA-compliant, on-premise training without cloud platforms.

**Startups**
Save $8k+/month on Roboflow and use the budget for engineers.

**Research Labs**
Reproducible experiments with versioned datasets and full audit trails.

**Enterprise ML**
Privacy-sensitive applications that can't use cloud services.

## Key Features

- **Auto-Fix Datasets**: Detect and repair issues automatically
- **Dataset Version Control**: Git-like workflows with visual diffs
- **Smart Training**: Auto-optimization based on GPU and dataset
- **Export Anywhere**: ONNX, TensorRT, TorchScript, CoreML
- **CLI + SDK**: Powerful terminal commands and clean Python API
- **100% Local**: Zero cloud dependencies or telemetry

## Next Steps

Ready to get started?

1. **[Installation](/guide/installation)** - Install ModelCub on your system
2. **[Quick Start](/guide/quick-start)** - Create your first project in 5 minutes
3. **[CLI Reference](/cli/reference)** - Explore all commands

::: tip Questions?
Check out our [GitHub Discussions](https://github.com/SeifBoukerdenna/ModelCub/discussions) or [open an issue](https://github.com/SeifBoukerdenna/ModelCub/issues).
:::