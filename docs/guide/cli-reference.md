# CLI Reference

Complete reference for all ModelCub commands.

## Global Options

```bash
modelcub --version              # Show version
modelcub --help                 # Show help
modelcub <command> --help       # Command-specific help
```

## Project Commands

### `project init`

Initialize a new ModelCub project.

```bash
modelcub project init [PATH] [OPTIONS]
```

**Arguments:**
- `PATH` - Project directory (default: current directory)

**Options:**
- `--name NAME` - Project name (default: directory name)
- `--force` - Overwrite existing project

**Examples:**
```bash
modelcub project init                    # Current directory
modelcub project init my-project         # New directory
modelcub project init . --name "Pills"   # Custom name
modelcub project init --force            # Reinitialize
```

### `project delete`

Delete a ModelCub project.

```bash
modelcub project delete [TARGET] [OPTIONS]
```

**Arguments:**
- `TARGET` - Path to project (default: current directory)

**Options:**
- `--yes` - Skip confirmation prompt

**Examples:**
```bash
modelcub project delete                  # Delete current project
modelcub project delete old-project      # Delete specific project
modelcub project delete --yes            # Force delete
```

**Safety:** Refuses to delete if directory looks like source code repository (has `.git`, `pyproject.toml`, etc.)

### `project info`

Show project information.

```bash
modelcub project info
```

Displays: name, created date, datasets, runs, configuration.

## Dataset Commands

### `dataset add`

Add/import a dataset.

```bash
modelcub dataset add --source PATH --name NAME [OPTIONS]
```

**Options:**
- `--source PATH` - Source directory or ZIP file (required)
- `--name NAME` - Dataset name (required)
- `--classes CLASSES` - Override classes (comma-separated)
- `--n N` - Number of images to import (default: 200)
- `--train-frac FRAC` - Train split fraction (default: 0.8)
- `--imgsz SIZE` - Image size (default: 640)
- `--seed SEED` - Random seed (default: 123)
- `--force` - Overwrite existing dataset

**Examples:**
```bash
# Import YOLO dataset
modelcub dataset add --source ./yolo-data --name production-v1

# Import Roboflow export
modelcub dataset add --source ./export.zip --name roboflow-v1

# Import 100 images only
modelcub dataset add --source ./data --name test-v1 --n 100

# Custom split ratio (90% train)
modelcub dataset add --source ./data --name v1 --train-frac 0.9

# Override classes
modelcub dataset add --source ./data --name v1 --classes "cat,dog,bird"

# Force overwrite
modelcub dataset add --source ./data --name v1 --force
```

**Supported Formats:**
- YOLO (directory with images/ and labels/)
- Roboflow exports (ZIP file)
- COCO (basic support)
- Unlabeled images (directory of images)

### `dataset list`

List all datasets in project.

```bash
modelcub dataset list
```

Shows: name, classes, image count, created date.

### `dataset info`

Show detailed dataset information.

```bash
modelcub dataset info NAME
```

**Arguments:**
- `NAME` - Dataset name

**Examples:**
```bash
modelcub dataset info production-v1
```

Displays:
- Classes and IDs
- Image counts per split
- Creation date and path
- Annotation statistics

### `dataset edit`

Edit dataset metadata.

```bash
modelcub dataset edit NAME [OPTIONS]
```

**Arguments:**
- `NAME` - Dataset name

**Options:**
- `--new-name NAME` - Rename dataset
- `--classes CLASSES` - Update classes (comma-separated)

**Examples:**
```bash
# Rename dataset
modelcub dataset edit old-name --new-name new-name

# Update classes
modelcub dataset edit production-v1 --classes "pill,bottle,box"
```

### `dataset delete`

Delete a dataset.

```bash
modelcub dataset delete NAME [OPTIONS]
```

**Arguments:**
- `NAME` - Dataset name

**Options:**
- `--yes` - Skip confirmation
- `--purge-cache` - Also delete cached files

**Examples:**
```bash
modelcub dataset delete old-dataset           # Requires confirmation
modelcub dataset delete old-dataset --yes     # Force delete
```

## Class Management

### `dataset classes list`

List classes in a dataset.

```bash
modelcub dataset classes list DATASET
```

**Arguments:**
- `DATASET` - Dataset name

**Examples:**
```bash
modelcub dataset classes list production-v1
```

Output:
```
Classes in production-v1:
  0: pill
  1: bottle
  2: box
```

### `dataset classes add`

Add a class to a dataset.

```bash
modelcub dataset classes add DATASET CLASS_NAME [OPTIONS]
```

**Arguments:**
- `DATASET` - Dataset name
- `CLASS_NAME` - Class name to add

**Options:**
- `--id ID` - Class ID (auto-assigned if not provided)

**Examples:**
```bash
modelcub dataset classes add production-v1 capsule
modelcub dataset classes add production-v1 tablet --id 3
```

### `dataset classes remove`

Remove a class from a dataset.

```bash
modelcub dataset classes remove DATASET CLASS_NAME [OPTIONS]
```

**Arguments:**
- `DATASET` - Dataset name
- `CLASS_NAME` - Class name to remove

**Options:**
- `--yes` - Skip confirmation

**Examples:**
```bash
modelcub dataset classes remove production-v1 box
modelcub dataset classes remove production-v1 box --yes
```

**Warning:** This removes the class definition but doesn't delete annotations. Annotations with removed class ID become invalid.

### `dataset classes rename`

Rename a class.

```bash
modelcub dataset classes rename DATASET OLD_NAME NEW_NAME
```

**Arguments:**
- `DATASET` - Dataset name
- `OLD_NAME` - Current class name
- `NEW_NAME` - New class name

**Examples:**
```bash
modelcub dataset classes rename production-v1 pill tablet
```

## Annotation Commands

### `annotate stats`

Show annotation statistics.

```bash
modelcub annotate stats DATASET
```

**Arguments:**
- `DATASET` - Dataset name

**Examples:**
```bash
modelcub annotate stats production-v1
```

Output:
```
📊 production-v1
   Total: 847
   Labeled: 623
   Progress: 73.6%
   Total boxes: 2,847
```

### `annotate list`

List annotated images.

```bash
modelcub annotate list DATASET
```

**Arguments:**
- `DATASET` - Dataset name

**Examples:**
```bash
modelcub annotate list production-v1
```

Shows: image ID, number of boxes per image.

## UI Commands

### `ui`

Launch web interface.

```bash
modelcub ui [OPTIONS]
```

**Options:**
- `--port PORT` - Port number (default: 8000)
- `--host HOST` - Host address (default: 127.0.0.1)

**Examples:**
```bash
modelcub ui                      # Default: http://localhost:8000
modelcub ui --port 3000          # Custom port
modelcub ui --host 0.0.0.0       # Allow external access
```

Press `Ctrl+C` to stop server.

## Configuration Commands

### `config show`

Show all configuration.

```bash
modelcub config show
```

Displays entire `.modelcub/config.yaml` contents.

### `config get`

Get specific config value.

```bash
modelcub config get KEY
```

**Arguments:**
- `KEY` - Config key (dot-separated path)

**Examples:**
```bash
modelcub config get defaults.device
modelcub config get defaults.batch_size
modelcub config get project.name
```

### `config set`

Set config value.

```bash
modelcub config set KEY VALUE
```

**Arguments:**
- `KEY` - Config key (dot-separated path)
- `VALUE` - New value

**Examples:**
```bash
modelcub config set defaults.batch_size 32
modelcub config set defaults.device cpu
modelcub config set defaults.image_size 1024
```

**Common Keys:**
- `defaults.device` - cuda, cpu, mps
- `defaults.batch_size` - Integer
- `defaults.image_size` - Integer
- `defaults.format` - yolo, coco
- `paths.data` - Data directory path
- `paths.runs` - Runs directory path

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments or not found
- `130` - Interrupted (Ctrl+C)

## Environment Variables

None currently. All configuration via `.modelcub/config.yaml`.

## Shell Completion

Coming soon: auto-completion for bash/zsh.

## Examples Workflow

```bash
# Initialize project
modelcub project init cv-project
cd cv-project

# Import dataset
modelcub dataset add --source ./data --name prod-v1

# Check what we have
modelcub dataset info prod-v1

# Add missing class
modelcub dataset classes add prod-v1 new-class

# Check annotation progress
modelcub annotate stats prod-v1

# Launch UI to annotate
modelcub ui

# Configure batch size
modelcub config set defaults.batch_size 32
```