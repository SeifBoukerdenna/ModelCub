# Architecture Overview

ModelCub's design philosophy and technical architecture.

## Design Philosophy

### 1. Local-First, Always

**Your data stays on your machine.**

- Zero cloud dependencies
- Works 100% offline
- No telemetry, no tracking
- Perfect for HIPAA/GDPR compliance
- Medical, pharma, defense applications

### 2. API-First Design

**One source of truth: the Core API.**

```
Everything flows through Core API:

CLI → Python SDK → Core API
Web UI → FastAPI → Core API

Each layer is optional and replaceable.
```

**Benefits:**
- Composable: Use CLI, SDK, or UI interchangeably
- Testable: Core logic isolated from interfaces
- Extensible: Add new interfaces without touching core
- Maintainable: Changes in one layer don't break others

### 3. Stateless Web UI

**UI is pure view layer.**

```
State lives in filesystem (.modelcub/):
├── config.yaml         # Configuration
├── datasets.yaml       # Dataset registry
├── runs.yaml           # Training runs
└── annotations.db      # SQLite cache (read-only)

No hidden databases, no session state.
Kill server, restart, everything intact.
```

**Benefits:**
- Multiple UI instances can run simultaneously
- No state synchronization issues
- Easy to backup (copy directory)
- Version control friendly (Git can track everything)

### 4. Format Agnostic

**YOLO internally, import/export anything.**

```
Import:                  Internal:          Export:
YOLO                     ↘                 ↗ YOLO
Roboflow  ────────────>  YOLO  ────────>  COCO
COCO                     ↗                 ↘ TFRecord
Images                                       CoreML
```

**Why YOLO as internal format:**
- Simple text-based (easy parsing)
- Universal compatibility
- Git-friendly (human-readable)
- Industry standard
- Supports detection + segmentation

## System Architecture

### Directory Structure

```
project-name/
├── .modelcub/                    # Core configuration
│   ├── config.yaml               # Project settings
│   ├── datasets.yaml             # Dataset registry
│   ├── runs.yaml                 # Training runs registry
│   ├── annotations.db            # SQLite cache (UI only)
│   ├── history/                  # Version control
│   │   ├── commits/              # Dataset commits
│   │   └── snapshots/            # Full snapshots
│   ├── backups/                  # Auto-fix backups
│   └── cache/                    # Temporary files
│
├── data/datasets/                # Datasets storage
│   └── <dataset-name>/
│       ├── images/               # Images
│       │   ├── train/
│       │   ├── val/
│       │   └── test/
│       ├── labels/               # YOLO labels
│       │   ├── train/
│       │   ├── val/
│       │   └── test/
│       ├── dataset.yaml          # YOLO config
│       └── metadata.json         # ModelCub metadata
│
├── runs/                         # Training outputs
│   └── <run-name>/
│       ├── weights/              # Model checkpoints
│       ├── results/              # Metrics, plots
│       └── config.yaml           # Run configuration
│
├── reports/                      # Generated reports
│   ├── validation_*.html
│   ├── fix_report_*.html
│   └── diff_*.html
│
└── modelcub.yaml                 # Project marker
```

### Component Diagram

```
┌─────────────────────────────────────────────────────┐
│                  User Interfaces                     │
├─────────────┬─────────────┬──────────────┬──────────┤
│     CLI     │  Python SDK │   Web UI     │  Future  │
│   (Click)   │   (Public)  │   (React)    │  (API)   │
└──────┬──────┴──────┬──────┴───────┬──────┴──────────┘
       │             │              │
       └─────────────┼──────────────┘
                     │
       ┌─────────────▼─────────────┐
       │       FastAPI Layer       │
       │    (REST + WebSocket)     │
       └─────────────┬─────────────┘
                     │
       ┌─────────────▼─────────────┐
       │      Core API Layer       │
       │  (Services + Registries)  │
       └─────────────┬─────────────┘
                     │
       ┌─────────────▼─────────────┐
       │      File System          │
       │  (.modelcub/ + data/)     │
       └───────────────────────────┘
```

## Core Components

### 1. Configuration System

**File:** `src/modelcub/core/config.py`

Pydantic models for type-safe configuration:

```python
ProjectConfig
├── project: ProjectInfo
├── defaults: DefaultSettings
│   ├── device (cuda/cpu/mps)
│   ├── batch_size
│   ├── image_size
│   └── format
└── paths: PathSettings
```

### 2. Registry System

**File:** `src/modelcub/core/registries.py`

**DatasetRegistry:**
- Stores dataset metadata in `datasets.yaml`
- CRUD operations for datasets
- Validates dataset consistency

**RunRegistry:**
- Stores training runs in `runs.yaml`
- Tracks experiments and checkpoints
- Links runs to datasets

**Design:**
- YAML for human readability
- Atomic writes (write temp → rename)
- No database dependencies

### 3. Service Layer

**Files:** `src/modelcub/services/*.py`

**Responsibilities:**
- Business logic
- Validation
- Error handling
- Event publishing

**Services:**
- `project_service.py` - Project lifecycle
- `dataset_service.py` - Dataset operations
- `annotation_service.py` - Annotation management
- `class_service.py` - Class operations

**Pattern:**
```python
def service_function(request: RequestModel) -> tuple[int, str]:
    """
    Returns: (exit_code, message)
    - 0: Success
    - 1: Error
    - 2: Invalid input
    """
```

### 4. Event Bus

**File:** `src/modelcub/core/events.py`

Simple pub/sub for cross-component communication:

```python
@dataclass
class ProjectInitialized:
    path: str
    name: str

bus.publish(ProjectInitialized(...))
bus.subscribe(ProjectInitialized, handler)
```

**Use cases:**
- Logging
- Notifications
- Cache invalidation
- Future: webhooks, integrations

## Web Stack

### Backend (FastAPI)

**File:** `src/modelcub/ui/backend/main.py`

```
FastAPI Application
├── Routes (/api/v1/)
│   ├── /projects
│   ├── /datasets
│   └── /models
├── Middleware
│   ├── CORS
│   ├── Error handling
│   ├── Project context
│   └── Response formatting
└── WebSocket (/ws)
    └── Real-time updates
```

**Design:**
- RESTful endpoints
- JSON responses
- WebSocket for live updates (training progress)
- Static file serving (React build)

### Frontend (React)

**File:** `src/modelcub/ui/frontend/`

```
React Application
├── Pages
│   ├── Dashboard
│   ├── Datasets
│   ├── DatasetViewer
│   ├── Models
│   └── Settings
├── Components
│   ├── Layout (sidebar, header)
│   ├── ProjectSelector
│   ├── Toast notifications
│   └── ClassManagerModal
└── API Client
    └── Typed requests
```

**Tech:**
- React 18 + TypeScript
- Vite for builds
- Tailwind CSS
- Custom CSS variables for theming
- Lucide icons

**State Management:**
- Local state (useState)
- API sync via custom hooks
- No Redux/MobX (keeping it simple)
- Future: Zustand for complex state

## Data Flow Examples

### Dataset Import

```
1. User: modelcub dataset add --source ./data --name v1

2. CLI parses args → calls SDK

3. SDK: Dataset.from_yolo("./data", name="v1")
   - Validates source directory
   - Parses YOLO format
   - Copies to project structure

4. Service: add_dataset(request)
   - Validates request
   - Creates dataset directory
   - Registers in datasets.yaml
   - Publishes DatasetAdded event

5. Returns success message to user
```

### UI Dataset Viewing

```
1. User opens browser → http://localhost:8000

2. React app loads
   - Fetches project info (GET /api/v1/projects)
   - Fetches dataset list (GET /api/v1/datasets)

3. User clicks dataset
   - Navigates to /datasets/:name
   - Fetches images (GET /api/v1/datasets/:name/images?limit=50)

4. FastAPI reads from filesystem
   - Scans images/ directory
   - Returns image paths + metadata
   - Pagination for large datasets

5. React renders image grid
   - Lazy loading
   - Virtual scrolling
   - Click to view full size
```

## Technology Stack

### Core
- **Python 3.9+** - Primary language
- **PyTorch** - Deep learning backend
- **Ultralytics** - YOLO implementation
- **OpenCV** - Image processing
- **PIL/Pillow** - Image handling
- **Pydantic** - Data validation

### CLI
- **Click** - Command framework
- **Rich** - Terminal formatting

### Backend
- **FastAPI** - REST API
- **Uvicorn** - ASGI server
- **WebSockets** - Real-time communication

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Konva.js** - Canvas (planned)

### Storage
- **YAML** - Configuration, registries
- **JSON** - Metadata
- **SQLite** - UI cache (optional)
- **Text files** - YOLO labels

### Testing
- **pytest** - Test framework
- **Coverage.py** - Code coverage
- Target: 85%+ coverage

## Security

### No Remote Code Execution

All imports validated:
- Check file extensions
- Validate paths (no directory traversal)
- Scan for malicious content

### No Network Access

- Zero outbound connections
- No telemetry
- No updates check
- No analytics

### Safe Deletion

Project deletion safety:
- Confirms before delete
- Refuses if looks like source repo
- Backs up on auto-fix

## Performance Considerations

### Large Datasets

**Pagination:**
- Web UI: 50 images per page
- Lazy loading
- Virtual scrolling

**Caching:**
- SQLite for annotation queries (UI only)
- File hash caching
- Thumbnail generation (future)

### Training

**Multi-GPU:**
- Automatic detection
- PyTorch DataParallel
- Distributed training (future)

**Memory:**
- Batch size auto-tuning
- Gradient accumulation
- Mixed precision (AMP)

## Extensibility

### Plugin System (Future)

```
plugins/
├── augmentations/
│   └── custom_aug.py
├── formats/
│   └── custom_format.py
└── models/
    └── custom_model.py
```

**Hook points:**
- Custom augmentations
- Format converters
- Model architectures
- Training callbacks

### API Extensions

FastAPI makes it easy:
```python
# Custom route
@app.get("/api/v1/custom")
async def custom_endpoint():
    return {"message": "Custom"}
```

## Version Control Design (In Progress)

### Commit System

```
.modelcub/history/
├── commits/
│   ├── abc123.yaml         # Commit metadata
│   └── abc123_manifest.json # File hashes
└── snapshots/
    └── abc123/             # Optional full snapshot
```

### Diff Algorithm

1. Load file hashes for both versions
2. Find added/removed/modified files
3. For modified labels: parse and compare
4. Generate statistics and impact analysis

### Visual Diff

Web UI showing:
- Side-by-side comparison
- Color-coded changes
- Filter by change type
- Annotation overlays

## Future Architecture

### Cloud Sync (Optional)

```
Local ModelCub ↔ S3/GCS/Azure
              ↕
         Cloud Sync Service
```

**Design:**
- Optional, not required
- E2E encryption
- Differential sync
- Conflict resolution

### Team Collaboration

```
User A ─┐
User B ─┼─> Shared Project
User C ─┘
```

**Features:**
- Multi-annotator mode
- Consensus labeling
- Review workflows
- User permissions

**Implementation:**
- Git-like branching
- Merge strategies
- Conflict resolution
- Change attribution