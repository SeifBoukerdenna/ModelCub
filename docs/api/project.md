# Project API

The `Project` class is the main entry point for working with ModelCub projects programmatically.

## Overview

```python
from modelcub import Project

# Create new project
project = Project.init("my-project")

# Load existing project
project = Project.load("my-project")

# Access properties
print(project.name)
print(project.config.defaults.device)

# Use as context manager (auto-saves)
with Project.load("my-project") as project:
    project.config.defaults.batch_size = 32
```

## Static Methods

### `Project.init(name, force=False, path=None)`

Create a new ModelCub project.

**Parameters:**
- `name` (str): Project name (also used as directory name if path not specified)
- `force` (bool, optional): Overwrite existing project. Default: `False`
- `path` (str, optional): Custom directory path. Default: `./<name>/`

**Returns:**
- `Project`: Initialized project instance

**Raises:**
- `RuntimeError`: If project initialization fails

**Example:**

```python
from modelcub import Project

# Create project in ./my-project/
project = Project.init("my-project")

# Create in custom location
project = Project.init("my-project", path="/path/to/project")

# Overwrite existing project
project = Project.init("my-project", force=True)
```

---

### `Project.load(path='.')`

Load an existing ModelCub project.

**Parameters:**
- `path` (str, optional): Path to project directory. Default: `"."` (current directory)

**Returns:**
- `Project`: Loaded project instance

**Raises:**
- `ValueError`: If path is not a valid ModelCub project

**Example:**

```python
from modelcub import Project

# Load from current directory
project = Project.load()

# Load from specific path
project = Project.load("./my-project")
project = Project.load("/absolute/path/to/project")
```

---

### `Project.exists(path)`

Check if a ModelCub project exists at the given path.

**Parameters:**
- `path` (str): Path to check

**Returns:**
- `bool`: `True` if valid project exists

**Example:**

```python
from modelcub import Project

if Project.exists("my-project"):
    project = Project.load("my-project")
else:
    project = Project.init("my-project")
```

## Properties

### Project Information

#### `project.name`

Project name from configuration.

**Type:** `str`

```python
project = Project.load()
print(project.name)  # "my-project"
```

---

#### `project.created`

Project creation timestamp (ISO 8601 format).

**Type:** `str`

```python
project = Project.load()
print(project.created)  # "2024-10-10T14:30:00Z"
```

---

#### `project.version`

Project version.

**Type:** `str`

```python
project = Project.load()
print(project.version)  # "1.0.0"
```

---

#### `project.path`

Project root directory path.

**Type:** `Path`

```python
project = Project.load()
print(project.path)  # PosixPath('/path/to/my-project')
```

### Configuration

#### `project.config`

Access project configuration object.

**Type:** `Config`

**Example:**

```python
project = Project.load()

# Read config
print(project.config.defaults.device)      # "cuda"
print(project.config.defaults.batch_size)  # 16
print(project.config.defaults.image_size)  # 640

# Modify config
project.config.defaults.device = "cpu"
project.config.defaults.batch_size = 32

# Save changes
project.save_config()
```

### Registries

#### `project.datasets`

Access dataset registry.

**Type:** `DatasetRegistry`

**Example:**

```python
project = Project.load()

# List all datasets
datasets = project.datasets.list_datasets()

# Get specific dataset
dataset_info = project.datasets.get_dataset("my-dataset")

# Check if dataset exists
if project.datasets.exists("my-dataset"):
    print("Dataset found")
```

---

#### `project.runs`

Access training runs registry.

**Type:** `RunRegistry`

**Example:**

```python
project = Project.load()

# List all runs
runs = project.runs.list_runs()

# Get specific run
run_info = project.runs.get_run("run-id-123")
```

### Directory Paths

#### `project.modelcub_dir`

Path to `.modelcub/` directory.

**Type:** `Path`

```python
project = Project.load()
print(project.modelcub_dir)  # /path/to/project/.modelcub
```

---

#### `project.data_dir`

Path to data directory.

**Type:** `Path`

```python
print(project.data_dir)  # /path/to/project/data
```

---

#### `project.datasets_dir`

Path to datasets directory.

**Type:** `Path`

```python
print(project.datasets_dir)  # /path/to/project/data/datasets
```

---

#### `project.runs_dir`

Path to training runs directory.

**Type:** `Path`

```python
print(project.runs_dir)  # /path/to/project/runs
```

---

#### `project.reports_dir`

Path to reports directory.

**Type:** `Path`

```python
print(project.reports_dir)  # /path/to/project/reports
```

---

#### `project.cache_dir`

Path to cache directory.

**Type:** `Path`

```python
print(project.cache_dir)  # /path/to/project/.modelcub/cache
```

---

#### `project.backups_dir`

Path to backups directory.

**Type:** `Path`

```python
print(project.backups_dir)  # /path/to/project/.modelcub/backups
```

---

#### `project.history_dir`

Path to version control history directory.

**Type:** `Path`

```python
print(project.history_dir)  # /path/to/project/.modelcub/history
```

## Methods

### Configuration Management

#### `project.save_config()`

Save configuration to disk.

**Returns:** `None`

**Example:**

```python
project = Project.load()

# Modify settings
project.config.defaults.batch_size = 32
project.config.defaults.device = "cpu"

# Save changes
project.save_config()
```

---

#### `project.reload_config()`

Reload configuration from disk.

**Returns:** `None`

**Example:**

```python
project = Project.load()

# Config was modified externally
project.reload_config()

# Now has latest values from disk
print(project.config.defaults.batch_size)
```

---

#### `project.get_config(key, default=None)`

Get configuration value by dot-notation key.

**Parameters:**
- `key` (str): Dot-notation key (e.g., `"defaults.device"`)
- `default` (any, optional): Default value if key not found

**Returns:**
- Configuration value or default

**Example:**

```python
project = Project.load()

# Get nested config values
device = project.get_config("defaults.device")
batch_size = project.get_config("defaults.batch_size")

# With default value
workers = project.get_config("defaults.workers", default=8)
```

---

#### `project.set_config(key, value)`

Set configuration value by dot-notation key.

**Parameters:**
- `key` (str): Dot-notation key (e.g., `"defaults.device"`)
- `value` (any): Value to set

**Returns:** `None`

**Raises:**
- `ValueError`: If key path is invalid

**Example:**

```python
project = Project.load()

# Set config values
project.set_config("defaults.device", "cuda")
project.set_config("defaults.batch_size", 32)
project.set_config("defaults.image_size", 1024)

# Don't forget to save!
project.save_config()
```

### Project Management

#### `project.delete(confirm=False)`

Delete the project directory.

**Parameters:**
- `confirm` (bool): Must be `True` to actually delete

**Returns:** `None`

**Raises:**
- `RuntimeError`: If confirm is not `True` or deletion fails

**Example:**

```python
project = Project.load("my-project")

# Delete project (requires explicit confirmation)
project.delete(confirm=True)

# Check it's gone
assert not Project.exists("my-project")
```

## Context Manager

The `Project` class supports context manager protocol for automatic config saving.

**Example:**

```python
from modelcub import Project

# Auto-saves config on context exit
with Project.load("my-project") as project:
    project.config.defaults.batch_size = 32
    project.config.defaults.workers = 16
    # Config automatically saved here

# Verify changes persisted
project = Project.load("my-project")
assert project.config.defaults.batch_size == 32
```

## Complete Examples

### Creating and Configuring a Project

```python
from modelcub import Project

# Create new project
project = Project.init("cv-pipeline")

# Configure defaults
project.config.defaults.device = "cuda"
project.config.defaults.batch_size = 32
project.config.defaults.image_size = 640
project.config.defaults.workers = 8

# Save configuration
project.save_config()

print(f"Project created at: {project.path}")
```

### Loading and Inspecting a Project

```python
from modelcub import Project

# Load existing project
project = Project.load("cv-pipeline")

# Print project info
print(f"Name: {project.name}")
print(f"Created: {project.created}")
print(f"Version: {project.version}")
print(f"Path: {project.path}")

# Print config
print("\nConfiguration:")
print(f"  Device: {project.config.defaults.device}")
print(f"  Batch Size: {project.config.defaults.batch_size}")
print(f"  Image Size: {project.config.defaults.image_size}")

# List datasets
datasets = project.datasets.list_datasets()
print(f"\nDatasets: {len(datasets)}")
for ds in datasets:
    print(f"  - {ds['name']}: {len(ds.get('classes', []))} classes")
```

### Using Dot-Notation Config Access

```python
from modelcub import Project

project = Project.load()

# Get multiple config values
device = project.get_config("defaults.device")
batch_size = project.get_config("defaults.batch_size")
data_path = project.get_config("paths.data")

# Set multiple config values
project.set_config("defaults.device", "cpu")
project.set_config("defaults.batch_size", 64)
project.set_config("defaults.workers", 16)

# Save all changes
project.save_config()
```

### Safe Project Deletion

```python
from modelcub import Project

# Load project
project = Project.load("old-project")

# Confirm before deletion
if input(f"Delete {project.name}? [y/N]: ").lower() == 'y':
    project.delete(confirm=True)
    print("Project deleted")
else:
    print("Deletion cancelled")
```

## See Also

- **[Dataset API](/api/dataset)** - Dataset operations
- **[Model API](/api/model)** - Model training
- **[CLI Reference](/cli/reference)** - Command-line interface