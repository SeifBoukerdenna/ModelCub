# Python SDK Documentation

Complete API reference for ModelCub's Python SDK.

## Installation

```bash
pip install modelcub
```

## Quick Example

```python
from modelcub import Project, Dataset

# Initialize project
project = Project.init("my-project")

# Import dataset
dataset = Dataset.from_yolo("./data", name="v1")

# Get statistics
stats = dataset.stats()
print(f"Images: {dataset.num_images}")
print(f"Classes: {dataset.classes}")
```

## Project API

### `Project.init()`

Initialize a new project.

```python
Project.init(path: str, name: str = None, force: bool = False) -> Project
```

**Parameters:**
- `path` - Project directory path
- `name` - Project name (default: directory name)
- `force` - Overwrite existing project

**Returns:** Project instance

**Example:**
```python
from modelcub import Project

project = Project.init("my-cv-project")
project = Project.init(".", name="Pills Detection")
project = Project.init(".", force=True)  # Reinitialize
```

### `Project.load()`

Load existing project.

```python
Project.load(path: str = ".") -> Project
```

**Parameters:**
- `path` - Project directory (default: current)

**Returns:** Project instance

**Raises:** `ValueError` if not a ModelCub project

**Example:**
```python
project = Project.load()              # Current directory
project = Project.load("./my-project")
```

### Project Properties

```python
project.name           # str: Project name
project.path           # Path: Project directory
project.config         # Config: Configuration object
project.datasets       # List[str]: Dataset names
project.runs           # List[str]: Training run names
```

### `project.get_dataset()`

Get dataset by name.

```python
project.get_dataset(name: str) -> Dataset
```

**Parameters:**
- `name` - Dataset name

**Returns:** Dataset instance

**Raises:** `ValueError` if dataset not found

**Example:**
```python
dataset = project.get_dataset("production-v1")
```

### `project.delete()`

Delete project.

```python
project.delete(confirm: bool = False) -> None
```

**Parameters:**
- `confirm` - Must be True to delete (safety)

**Raises:** `ValueError` if confirm not True

**Example:**
```python
project.delete(confirm=True)
```

## Dataset API

### `Dataset.from_yolo()`

Import YOLO format dataset.

```python
Dataset.from_yolo(
    source: str,
    name: str,
    n: int = 200,
    train_frac: float = 0.8,
    imgsz: int = 640,
    seed: int = 123,
    force: bool = False
) -> Dataset
```

**Parameters:**
- `source` - Source directory path
- `name` - Dataset name
- `n` - Number of images to import
- `train_frac` - Train split fraction (0.0-1.0)
- `imgsz` - Image size
- `seed` - Random seed
- `force` - Overwrite existing

**Returns:** Dataset instance

**Example:**
```python
from modelcub import Dataset

ds = Dataset.from_yolo("./yolo-data", name="v1")
ds = Dataset.from_yolo("./data", name="v1", n=100, train_frac=0.9)
```

### `Dataset.from_roboflow()`

Import Roboflow export.

```python
Dataset.from_roboflow(
    source: str,
    name: str,
    **kwargs
) -> Dataset
```

**Parameters:**
- `source` - Path to Roboflow ZIP
- `name` - Dataset name
- `**kwargs` - Same as `from_yolo()`

**Example:**
```python
ds = Dataset.from_roboflow("./export.zip", name="roboflow-v1")
```

### `Dataset.from_images()`

Import unlabeled images.

```python
Dataset.from_images(
    source: str,
    name: str,
    **kwargs
) -> Dataset
```

**Parameters:**
- `source` - Directory of images
- `name` - Dataset name

**Example:**
```python
ds = Dataset.from_images("./images/", name="unlabeled-v1")
```

### `Dataset.load()`

Load existing dataset.

```python
Dataset.load(name: str) -> Dataset
```

**Parameters:**
- `name` - Dataset name

**Returns:** Dataset instance

**Raises:** `ValueError` if not found

**Example:**
```python
dataset = Dataset.load("production-v1")
```

### Dataset Properties

```python
dataset.name           # str: Dataset name
dataset.path           # Path: Dataset directory
dataset.classes        # List[str]: Class names
dataset.num_images     # int: Total image count
dataset.splits         # Dict: Split information
dataset.created        # datetime: Creation timestamp
```

### `dataset.stats()`

Get dataset statistics.

```python
dataset.stats() -> Dict[str, Any]
```

**Returns:** Dictionary with:
- `class_distribution` - Images per class
- `images_per_split` - Train/val/test counts
- `annotations_count` - Total annotations

**Example:**
```python
stats = dataset.stats()
print(stats['class_distribution'])
# {'pill': 450, 'bottle': 300, 'box': 97}

print(stats['images_per_split'])
# {'train': 677, 'val': 119, 'test': 51}
```

### `dataset.validate()`

Validate dataset (coming soon).

```python
dataset.validate() -> ValidationReport
```

**Returns:** Validation report with issues

### `dataset.fix()`

Auto-fix dataset issues (coming soon).

```python
dataset.fix(auto: bool = False) -> FixReport
```

**Parameters:**
- `auto` - Apply fixes automatically

**Returns:** Fix report

### `dataset.delete()`

Delete dataset.

```python
dataset.delete(confirm: bool = False) -> None
```

**Parameters:**
- `confirm` - Must be True (safety)

**Example:**
```python
dataset.delete(confirm=True)
```

### `dataset.reload()`

Reload dataset metadata.

```python
dataset.reload() -> None
```

Updates internal state from registry.

## Annotation API

### `dataset.get_annotation()`

Get annotation for image.

```python
dataset.get_annotation(image_id: str) -> Dict[str, Any]
```

**Parameters:**
- `image_id` - Image identifier

**Returns:** Dictionary with:
- `image_id` - Image ID
- `num_boxes` - Annotation count
- `boxes` - List of bounding boxes
- `classes` - Class IDs

**Example:**
```python
ann = dataset.get_annotation("img_001.jpg")
print(f"Boxes: {ann['num_boxes']}")
for box in ann['boxes']:
    print(f"Class: {box['class_id']}, bbox: {box['bbox']}")
```

### `dataset.get_annotations()`

Get all annotations.

```python
dataset.get_annotations() -> List[Dict[str, Any]]
```

**Returns:** List of annotation dicts

**Example:**
```python
annotations = dataset.get_annotations()
labeled = [a for a in annotations if a['num_boxes'] > 0]
print(f"Labeled: {len(labeled)}/{len(annotations)}")
```

### `dataset.annotation_stats()`

Get annotation statistics.

```python
dataset.annotation_stats() -> Dict[str, Any]
```

**Returns:** Dictionary with:
- `total_images` - Total image count
- `labeled` - Labeled image count
- `progress` - Completion percentage
- `total_boxes` - Total annotations

**Example:**
```python
stats = dataset.annotation_stats()
print(f"Progress: {stats['progress']:.1%}")
print(f"Boxes: {stats['total_boxes']}")
```

## Class Management

### `dataset.add_class()`

Add class (coming soon).

```python
dataset.add_class(name: str, id: int = None) -> None
```

### `dataset.remove_class()`

Remove class (coming soon).

```python
dataset.remove_class(name: str) -> None
```

### `dataset.rename_class()`

Rename class (coming soon).

```python
dataset.rename_class(old_name: str, new_name: str) -> None
```

## Version Control (Planned)

### `dataset.commit()`

Commit dataset state.

```python
dataset.commit(message: str) -> str
```

**Returns:** Commit ID

### `dataset.history()`

Get commit history.

```python
dataset.history() -> List[Commit]
```

### `dataset.diff()`

Compare versions.

```python
dataset.diff(v1: str, v2: str) -> DiffReport
```

### `dataset.checkout()`

Checkout version.

```python
dataset.checkout(version: str) -> None
```

## Error Handling

```python
from modelcub import Project, Dataset

try:
    project = Project.load("nonexistent")
except ValueError as e:
    print(f"Error: {e}")

try:
    dataset = Dataset.load("missing")
except ValueError as e:
    print(f"Dataset not found: {e}")
```

## Complete Example

```python
from modelcub import Project, Dataset

# Initialize project
project = Project.init("cv-pipeline")

# Import datasets
train_ds = Dataset.from_yolo("./train-data", name="train-v1")
val_ds = Dataset.from_yolo("./val-data", name="val-v1")

# Inspect
print(f"Training: {train_ds.num_images} images")
print(f"Classes: {train_ds.classes}")

stats = train_ds.stats()
print(f"Distribution: {stats['class_distribution']}")

# Get annotations
annotations = train_ds.get_annotations()
labeled = [a for a in annotations if a['num_boxes'] > 0]
print(f"Labeled: {len(labeled)}/{len(annotations)}")

# Annotation progress
ann_stats = train_ds.annotation_stats()
print(f"Progress: {ann_stats['progress']:.1%}")
```

## Type Hints

ModelCub uses type hints throughout:

```python
from modelcub import Project, Dataset
from typing import List, Dict, Any

project: Project = Project.load()
dataset: Dataset = Dataset.load("v1")
stats: Dict[str, Any] = dataset.stats()
```

## Async Support

Not currently supported. Use threading for concurrency:

```python
from concurrent.futures import ThreadPoolExecutor

datasets = ["ds1", "ds2", "ds3"]

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(Dataset.load(name).stats)
        for name in datasets
    ]

    for future in futures:
        stats = future.result()
        print(stats)
```