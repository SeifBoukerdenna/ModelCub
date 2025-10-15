# API Overview

ModelCub provides a clean Python SDK for programmatic access to all functionality.

## Installation

```bash
pip install modelcub
```

## Quick Example

```python
from modelcub import Project, Dataset, Model

# Create project
project = Project.init("my-project", path="./path/to/init/project)

dataset = project.import_dataset(source="./photos", name="animals", classes=["bear1", "bear2", "bear3"], force=True, delete_existent=True)


# Validate and fix
dataset.validate()
dataset.fix(auto=True)

# Train model
model = Model("yolov11n", task="detect")
run = model.train(dataset=dataset, auto=True)

# Evaluate
results = run.evaluate(split="val")
print(f"mAP50: {results.map50:.3f}")
```

## Core Classes

### Project

Manage ModelCub projects, configurations, and metadata.

```python
from modelcub import Project

# Create/load projects
project = Project.init("my-project")
project = Project.load("my-project")

# Access configuration
project.config.defaults.batch_size = 32
project.save_config()
```

**[Read Project API Reference →](/api/project)**

### Dataset

Import, validate, fix, and version control datasets.

```python
from modelcub import Dataset

# Import dataset
dataset = Dataset.from_path("./yolo-data", name="v1")

# Validate and fix
report = dataset.validate()
dataset.fix(auto=True)

# Version control
dataset.commit(message="Initial import")
diff = dataset.diff("v1", "v2")
```

**[Read Dataset API Reference →](/api/dataset)**

### Model

Train, evaluate, and export models.

```python
from modelcub import Model

# Create model
model = Model("yolov11n", task="detect")

# Train
run = model.train(dataset=dataset, epochs=50, auto=True)

# Evaluate
results = run.evaluate(split="val")

# Export
run.export(format="onnx", output="model.onnx")
```

**[Read Model API Reference →](/api/model)**

## Design Principles

### Simple by Default

Most operations work with minimal configuration:

```python
# Just works
dataset.fix(auto=True)
model.train(dataset=dataset, auto=True)
```

### Explicit When Needed

Full control available when you need it:

```python
# Customize everything
model.train(
    dataset=dataset,
    epochs=50,
    batch_size=16,
    image_size=640,
    device="cuda:0",
    learning_rate=0.01,
    optimizer="adam"
)
```

### Pythonic API

Follows Python conventions and best practices:

```python
# Properties for data access
print(project.name)
print(project.created)

# Methods for actions
project.save_config()
dataset.fix(auto=True)

# Context managers for automatic cleanup
with Project.load("my-project") as project:
    project.config.defaults.batch_size = 32
```

### Type Hints

Full type annotations for better IDE support:

```python
from modelcub import Project
from pathlib import Path

def setup_project(name: str, path: Path) -> Project:
    project = Project.init(name, path=str(path))
    return project
```

## Common Patterns

### Project Setup

```python
from modelcub import Project

# Create and configure
project = Project.init("cv-pipeline")
project.config.defaults.device = "cuda"
project.config.defaults.batch_size = 32
project.save_config()
```

### Dataset Import and Validation

```python
from modelcub import Dataset

# Import dataset
dataset = Dataset.from_path("./data", name="production-v1")

# Validate
report = dataset.validate()
print(f"Health Score: {report.health_score}/100")

# Fix issues
if report.critical:
    dataset.fix(auto=True)
```

### Training Workflow

```python
from modelcub import Model

# Train with auto-optimization
model = Model("yolov11n", task="detect")
run = model.train(dataset=dataset, auto=True)

# Check results
if run.best_map50 > 0.85:
    run.export(format="onnx")
```

### Version Control

```python
from modelcub import Dataset

dataset = Dataset.load("production-v1")

# Commit current state
dataset.commit(message="Initial import")

# Make changes...

# Commit again
dataset.commit(message="Added 500 images")

# Compare versions
diff = dataset.diff("v1", "v2")
print(f"Images added: {len(diff.added_images)}")
```

## Error Handling

All methods raise descriptive exceptions:

```python
from modelcub import Project

try:
    project = Project.load("nonexistent")
except ValueError as e:
    print(f"Error: {e}")
    # Error: Not a valid ModelCub project: /path/to/nonexistent

try:
    project.delete(confirm=False)
except RuntimeError as e:
    print(f"Error: {e}")
    # Error: Must set confirm=True to delete project
```

## Async Support

ModelCub is currently synchronous. Async support may be added in future versions.

For now, use threading or multiprocessing for concurrent operations:

```python
from concurrent.futures import ThreadPoolExecutor
from modelcub import Dataset

datasets = ["ds1", "ds2", "ds3"]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(Dataset.load(name).validate)
        for name in datasets
    ]

    for future in futures:
        report = future.result()
        print(f"Health: {report.health_score}/100")
```

## API Reference

Detailed documentation for each class:

- **[Project](/api/project)** - Project management
- **[Dataset](/api/dataset)** - Dataset operations
- **[Model](/api/model)** - Training and evaluation
- **[Run](/api/run)** - Training run management
- **[Configuration](/api/configuration)** - Config objects

## Examples

See the **[Examples](/examples/)** section for complete workflows:

- Medical imaging pipeline
- Dataset versioning workflow
- Multi-GPU training
- Production deployment

## Need Help?

- **[GitHub Discussions](https://github.com/SeifBoukerdenna/ModelCub/discussions)** - Ask questions
- **[GitHub Issues](https://github.com/SeifBoukerdenna/ModelCub/issues)** - Report bugs
- **[CLI Reference](/cli/reference)** - Command-line interface