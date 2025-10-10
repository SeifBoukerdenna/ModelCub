# ModelCub: Master Timeline & Project Vision

**Last Updated:** October 10, 2025  
**Version:** 1.0 Planning Document  
**Target Launch:** Week 16 (April 2026)

---

## 🎯 PROJECT VISION

### Core Mission
ModelCub is the open-source, local-first MLOps toolkit for computer vision. We eliminate the 70-80% of time CV teams waste on data wrangling, format conversion, and debugging broken datasets. Think "Homebrew for CV workflows" — you type one command and the chaos just works.

### Origin Story
Built by a developer who worked at a pharmaceutical AI startup where they paid Roboflow $8,000/month for a single project. Medical imaging data sat on external servers. Local experimentation required painful export/convert/sync cycles. This tool is what we wish we had.

### Core Philosophy
1. **Local-first**: Runs entirely offline, perfect for sensitive industries (pharma, medtech, defense)
2. **Composable**: Works as CLI or SDK, integrates with existing workflows
3. **Transparent**: No magic backends, clean YAML reports for everything
4. **Reproducible**: Datasets, configs, checkpoints versioned like code
5. **Developer-focused**: Built by engineers who felt the pain, not by SaaS sales teams

### Market Position
**Against Roboflow:**
- They: Cloud-locked, expensive at scale ($96k/year examples), opaque pricing
- Us: Local-first, free OSS, transparent, reproducible

**Against Ultralytics:**
- They: Model-specific (YOLO-centric), light on data management
- Us: Format-agnostic, data management focused, reproducibility core

**Sweet Spot:**
- Teams needing on-premise solutions (pharma, medical, defense)
- Privacy-sensitive applications
- Academia requiring reproducibility
- Indie developers avoiding vendor lock-in
- Anyone hit by Roboflow's pricing wall

### Success Metrics (1.0 Launch)
- 5,000+ GitHub stars (Week 1)
- 500+ active users (Month 1)
- 10+ community contributors (Month 2)
- Featured on Hacker News front page
- Mentioned as "Roboflow alternative" in discussions

---

## 🏗️ TECHNICAL ARCHITECTURE

### Internal Format Decision
**Primary format:** YOLO (v5/v8/v11 compatible)
- Simple text-based format
- Universal compatibility
- Easy to parse and validate
- Industry standard for detection/segmentation

### Directory Structure
```
project-name/
├── .modelcub/
│   ├── config.yaml          # Project configuration
│   ├── datasets.yaml        # Dataset registry
│   ├── runs.yaml            # Training runs registry
│   ├── history/             # Version control data
│   │   ├── commits/         # Dataset commits
│   │   └── snapshots/       # Full snapshots
│   └── cache/               # Temporary files
├── data/
│   └── datasets/
│       └── <dataset-name>/
│           ├── images/
│           │   ├── train/
│           │   ├── val/
│           │   └── test/
│           ├── labels/
│           │   ├── train/
│           │   ├── val/
│           │   └── test/
│           ├── dataset.yaml      # YOLO config
│           └── metadata.json     # ModelCub metadata
├── runs/
│   └── <run-name>/
│       ├── weights/
│       ├── results/
│       └── config.yaml
├── reports/                 # Generated HTML reports
└── modelcub.yaml           # Main project file
```

### Metadata Schema

**Dataset Metadata (.modelcub/datasets.yaml):**
```yaml
datasets:
  pills-v1:
    id: "7a3f9b2e"
    name: "pills-v1"
    created: "2024-10-10T14:30:00Z"
    modified: "2024-10-10T14:30:00Z"
    format: "yolo"
    task: "detect"  # detect, segment, classify
    classes: ["pill", "bottle", "blister"]
    num_classes: 3
    splits:
      train: 
        images: 677
        labels: 677
        path: "data/datasets/pills-v1/images/train"
      val:
        images: 120
        labels: 120
        path: "data/datasets/pills-v1/images/val"
      test:
        images: 50
        labels: 50
        path: "data/datasets/pills-v1/images/test"
    path: "data/datasets/pills-v1"
    health_score: 94
    version: 1
    parent: null  # ID of parent dataset if this is modified version
    git_commit: "a3f9b2e1"  # Git commit when created
    source: "roboflow-export"  # import source
```

**Run Metadata (.modelcub/runs.yaml):**
```yaml
runs:
  pills-detect-20241010:
    id: "1f8e3c4a"
    name: "pills-detect-20241010"
    created: "2024-10-10T15:22:00Z"
    status: "completed"  # running, completed, failed, stopped
    dataset: "pills-v1"
    dataset_version: 1
    model: "yolov11n"
    task: "detect"
    config:
      epochs: 50
      batch_size: 16
      image_size: 640
      device: "cuda"
      optimizer: "adam"
      lr: 0.01
      # ... full hyperparameters
    results:
      best_epoch: 42
      best_map50: 0.89
      final_map50: 0.87
      training_time: "2h 15m"
    weights:
      best: "runs/pills-detect-20241010/weights/best.pt"
      last: "runs/pills-detect-20241010/weights/last.pt"
    environment:
      python: "3.10.8"
      cuda: "11.8"
      pytorch: "2.0.1"
      modelcub: "1.0.0"
```

### Technology Stack
- **Language:** Python 3.9+
- **CLI Framework:** Click or Typer
- **Deep Learning:** PyTorch, Ultralytics (YOLO)
- **Computer Vision:** OpenCV, PIL
- **Data Processing:** NumPy, Pandas
- **Visualization:** Matplotlib, Plotly
- **Web UI:** Flask/FastAPI + basic HTML/CSS (no React complexity)
- **Reports:** Jinja2 templates for HTML generation
- **Hashing:** xxHash for fast file hashing
- **Testing:** pytest with >80% coverage

---

## 📅 DETAILED DEVELOPMENT TIMELINE

---

### **PHASE 1: FOUNDATION (Weeks 1-4)**

#### **WEEK 1: Core Infrastructure**

**Feature: `modelcub init` - Project Initialization**

**Description:**
The foundation of the entire system. Creates project structure, initializes config files, and sets up the data model that everything else depends on.

**Commands:**
```bash
modelcub init <project-name>
modelcub init <project-name> --template detection|segmentation|classification
```

**Implementation Requirements:**
1. Create directory structure (see Architecture section)
2. Initialize `.modelcub/config.yaml` with defaults
3. Create empty `datasets.yaml` and `runs.yaml`
4. Generate `modelcub.yaml` project file
5. Optional: Initialize git repo

**Config Defaults:**
```yaml
# .modelcub/config.yaml
project:
  name: "pills-detection"
  created: "2024-10-10T14:30:00Z"
  version: "1.0.0"

defaults:
  device: "cuda"  # cuda, cpu, mps
  batch_size: 16
  image_size: 640
  workers: 8
  format: "yolo"

paths:
  data: "data"
  runs: "runs"
  reports: "reports"
```

**Python SDK:**
```python
from modelcub import Project

# Create new project
project = Project.init("pills-detection")

# Load existing project
project = Project.load(".")  # or path to project

# Access config
project.config.get("defaults.device")
project.config.set("defaults.device", "cpu")
project.config.save()

# Project info
print(project.name)
print(project.path)
print(project.created)
```

**Success Criteria:**
- ✅ Creates all required directories
- ✅ Generates valid config files
- ✅ Works on Windows, Mac, Linux
- ✅ Handles existing directory gracefully
- ✅ Config is read/writable
- ✅ Python SDK works
- ✅ Unit tests cover 80%+

**Time Estimate:** 4-5 days

---

#### **WEEKS 2-3: Data Import Pipeline**

**Feature: `modelcub dataset add` - Dataset Import**

**Description:**
Import datasets from various sources into ModelCub's internal format. Start with YOLO (simplest), then add Roboflow export support for migration story.

**Commands:**
```bash
# Import from local YOLO dataset
modelcub dataset add --path ./yolo_data --name pills-v1
modelcub dataset add --path ./yolo_data  # auto-generate name
modelcub dataset add --path ./yolo_data --format yolo

# Import from Roboflow export (ZIP file)
modelcub dataset add --from roboflow-export --path ./export.zip --name pills-rf

# List datasets
modelcub dataset list
modelcub dataset list --verbose
modelcub dataset list --format json

# Dataset info
modelcub dataset info pills-v1
modelcub dataset info pills-v1 --stats
```

**Implementation Requirements:**

**1. YOLO Format Parser:**
- Detect YOLO format automatically:
  - Look for `data.yaml` or `dataset.yaml`
  - Look for `images/` and `labels/` folders
  - Validate structure matches YOLO conventions
- Parse dataset YAML to extract classes
- Handle both detection and segmentation formats
- Support relative and absolute paths

**2. File Validation:**
- Verify all images are readable (PIL/OpenCV)
- Verify all label files are valid YOLO format
- Check image/label file pairs match
- Validate label format:
  - Detection: `class_id x_center y_center width height`
  - Segmentation: `class_id x1 y1 x2 y2 ... xn yn`
  - All values are numeric
  - Coordinates in [0, 1] range
  - Class IDs are valid integers

**3. Import Process:**
- Copy or symlink files to `data/datasets/<name>/`
- Preserve directory structure (train/val/test)
- Generate unique dataset ID (8-char hash)
- Calculate statistics:
  - Total images per split
  - Total labels per split
  - Class distribution
  - Average objects per image
  - Image size distribution
- Initial health score calculation

**4. Roboflow Export Support:**
- Unzip Roboflow export
- Detect format (usually YOLO)
- Convert if necessary
- Import like normal YOLO dataset
- Preserve original metadata if available

**5. Registry Management:**
- Add entry to `.modelcub/datasets.yaml`
- Store all metadata
- Handle name conflicts (auto-increment)
- Track import source

**Python SDK:**
```python
from modelcub import Dataset

# Import from path
ds = Dataset.from_path("./yolo_data", name="pills-v1")

# Import Roboflow export
ds = Dataset.from_roboflow_export("./export.zip", name="pills-rf")

# Access dataset info
print(ds.name)           # "pills-v1"
print(ds.id)             # "7a3f9b2e"
print(ds.classes)        # ["pill", "bottle", "blister"]
print(ds.num_classes)    # 3
print(ds.num_images)     # 847
print(ds.task)           # "detect"

# Split info
print(ds.splits.train.images)  # 677
print(ds.splits.val.images)    # 120
print(ds.splits.test.images)   # 50

# Statistics
stats = ds.stats()
print(stats.class_distribution)
print(stats.avg_objects_per_image)
print(stats.image_sizes)

# List all datasets
datasets = Dataset.list()
for ds in datasets:
    print(f"{ds.name}: {ds.num_images} images")
```

**Success Criteria:**
- ✅ Successfully imports clean YOLO dataset
- ✅ Handles train/val/test splits correctly
- ✅ Validates all files and labels
- ✅ Extracts correct class names and counts
- ✅ Imports Roboflow YOLO export
- ✅ Gracefully handles corrupted files
- ✅ Processes 1000 images in <10 seconds
- ✅ Generates accurate metadata
- ✅ Python SDK fully functional
- ✅ Unit tests cover edge cases

**Test Datasets:**
1. Clean YOLO dataset (create reference dataset)
2. Roboflow export (download real example)
3. Messy dataset with issues (missing files, bad labels)
4. Large dataset (10k+ images, performance test)
5. Dataset without splits (should create default split)

**Time Estimate:** 10-12 days

---

#### **WEEK 4: Data Quality Analysis**

**Feature: `modelcub dataset validate` - Basic Validation**

**Description:**
Validate dataset integrity and detect common issues. This is preparation for the `fix` command but provides read-only analysis first.

**Commands:**
```bash
modelcub dataset validate pills-v1
modelcub dataset validate pills-v1 --strict
modelcub dataset validate pills-v1 --report
```

**Implementation Requirements:**

**Issue Detection Categories:**

**1. Critical Issues (block training):**
- Corrupt/unreadable images
- Missing image files (referenced in labels)
- Missing label files (images without labels)
- Invalid YOLO format (syntax errors)
- Out-of-bounds coordinates
- Invalid class IDs (>= num_classes)

**2. Quality Issues (reduce performance):**
- Exact duplicate images (file hash)
- Empty label files (no annotations)
- Very small objects (<1% of image area)
- Very large objects (>90% of image area)

**3. Warnings (potential issues):**
- Class imbalance (some classes <5% of dataset)
- Split size imbalance (test split >30% of data)
- Missing splits (no val or test set)

**Output Format:**
```bash
$ modelcub dataset validate pills-v1

🔍 Validating pills-v1 (847 images)...
   [████████████████████] 100%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Dataset Structure: PASSED
   • All required directories present
   • dataset.yaml is valid

⚠️  Found 23 issues:

❌ CRITICAL (will block training):
   • 2 corrupt images
     → data/datasets/pills-v1/images/train/img_0234.jpg
     → data/datasets/pills-v1/images/train/img_0891.jpg
   
   • 8 out-of-bounds coordinates
     → 8 label files affected (see details)
   
   • 1 invalid YOLO format
     → data/datasets/pills-v1/labels/train/img_0445.txt
       Line 3: Expected 5 values, got 4

⚠️  QUALITY (reduces performance):
   • 4 exact duplicates
     → img_0123.jpg == img_0456.jpg
     → img_0234.jpg == img_0567.jpg
     → (2 more pairs)
   
   • 8 empty label files
     → Images with no annotations

💡 WARNINGS:
   • Class imbalance detected
     → "blister": 12% of dataset
     → Consider balancing or weighted loss

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Dataset Health Score: 67/100

   Recommendations:
   1. Fix critical issues with 'modelcub dataset fix --auto'
   2. Review and remove duplicate images
   3. Consider augmenting "blister" class

Detailed report: modelcub dataset validate pills-v1 --report
```

**Health Score Calculation:**
```python
# Base score: 100
# Deductions:
- 10 points per corrupt image
- 5 points per missing file
- 3 points per out-of-bounds box
- 2 points per invalid format
- 1 point per duplicate
- 1 point per empty label
# Minimum: 0, Maximum: 100
```

**Python SDK:**
```python
from modelcub import Dataset

ds = Dataset.load("pills-v1")

# Run validation
report = ds.validate()

# Access results
print(f"Health Score: {report.health_score}/100")
print(f"Critical Issues: {len(report.critical)}")
print(f"Quality Issues: {len(report.quality)}")
print(f"Warnings: {len(report.warnings)}")

# Iterate through issues
for issue in report.critical:
    print(f"{issue.type}: {issue.file} - {issue.description}")

# Export report
report.export_json("validation_report.json")
report.export_html("validation_report.html")
```

**Success Criteria:**
- ✅ Detects all critical issue types
- ✅ Accurate health score calculation
- ✅ Clear, actionable output
- ✅ Fast validation (<30 seconds for 10k images)
- ✅ Handles large datasets efficiently
- ✅ Export to JSON/HTML works
- ✅ Python SDK complete

**Time Estimate:** 5-6 days

---

### **PHASE 2: KILLER FEATURES (Weeks 5-8)**

#### **WEEKS 5-6: Auto-Fix - The Viral Feature**

**Feature: `modelcub dataset fix` - Automated Dataset Repair**

**Description:**
The headline feature that gets you stars. Automatically detect and fix common dataset issues with beautiful before/after reports. This is what people will screenshot and share.

**Commands:**
```bash
# Auto-fix all fixable issues
modelcub dataset fix pills-v1 --auto

# Interactive mode (ask before each fix)
modelcub dataset fix pills-v1 --interactive

# Generate HTML report
modelcub dataset fix pills-v1 --auto --report

# Create backup before fixing
modelcub dataset fix pills-v1 --auto --backup

# Fix specific issue types only
modelcub dataset fix pills-v1 --issues corrupt,duplicates,bounds

# Dry run (show what would be fixed)
modelcub dataset fix pills-v1 --dry-run
```

**Implementation Requirements:**

**1. Fixable Issues:**

**Automatic Fixes:**
- **Corrupt images:** Remove from dataset
- **Missing images:** Remove corresponding label file
- **Missing labels:** Create empty label file or remove image
- **Out-of-bounds boxes:** Clip to [0, 1] range
- **Invalid format:** Remove invalid annotation lines
- **Invalid class IDs:** Remove invalid annotations
- **Exact duplicates:** Keep first occurrence, remove duplicates

**Manual Review Required:**
- **Near-duplicates:** Flag for user review (>95% similar)
- **Empty annotations:** Flag (user decides if intentional)
- **Suspicious labels:** Flag likely mislabels
- **Extreme sizes:** Flag very small/large objects

**2. Fix Process:**
- Create backup in `.modelcub/backups/` (unless --no-backup)
- Apply fixes in order of safety
- Log every change made
- Update metadata after fixes
- Recalculate health score
- Generate detailed report

**3. Backup System:**
```
.modelcub/backups/
└── pills-v1-20241010-143022/
    ├── metadata.json
    ├── changed_files.json
    └── files/
        └── [only files that were modified]
```

**4. Change Tracking:**
```json
{
  "backup_id": "pills-v1-20241010-143022",
  "timestamp": "2024-10-10T14:30:22Z",
  "changes": [
    {
      "type": "removed",
      "reason": "corrupt_image",
      "file": "images/train/img_0234.jpg",
      "label": "labels/train/img_0234.txt"
    },
    {
      "type": "modified",
      "reason": "out_of_bounds",
      "file": "labels/train/img_0445.txt",
      "before": "0 0.5 0.5 1.2 0.8",
      "after": "0 0.5 0.5 1.0 0.8"
    }
  ]
}
```

**5. HTML Report Generation:**

Must be visually stunning and screenshot-worthy. Use these sections:

**Executive Summary:**
```html
<!-- Big, bold numbers -->
<div class="summary">
  <h1>Dataset Fixed</h1>
  <div class="stat-grid">
    <div class="stat">
      <span class="number">23</span>
      <span class="label">Issues Fixed</span>
    </div>
    <div class="stat">
      <span class="number">67 → 94</span>
      <span class="label">Health Score</span>
    </div>
    <div class="stat">
      <span class="number">~2 days</span>
      <span class="label">Time Saved</span>
    </div>
  </div>
</div>
```

**Issues Fixed Gallery:**
- Show 2-3 example images per issue type
- Side-by-side before/after
- Visual diffs for label changes
- Highlight what changed

**Action Items:**
- Things needing manual review
- Prioritized by impact
- One-click links to files

**Dataset Statistics:**
- Class distribution charts (before/after)
- Image quality metrics
- Size distributions

**Python SDK:**
```python
from modelcub import Dataset

ds = Dataset.load("pills-v1")

# Run fixes
report = ds.fix(
    auto=True,
    backup=True,
    issues=["corrupt", "bounds", "duplicates"]
)

# Access report
print(f"Issues found: {report.total_issues}")
print(f"Issues fixed: {report.fixed}")
print(f"Needs review: {report.review_needed}")
print(f"Health: {report.health_before} → {report.health_after}")

# Detailed breakdown
print(f"Corrupt images removed: {len(report.corrupt_images)}")
print(f"Out-of-bounds clipped: {len(report.out_of_bounds)}")
print(f"Duplicates removed: {len(report.duplicates)}")

# Export report
report.export_html("fix_report.html")

# Rollback if needed
ds.rollback(backup_id="pills-v1-20241010-143022")
```

**Terminal Output:**
```bash
$ modelcub dataset fix pills-v1 --auto --report

🔍 Scanning pills-v1...
   Found 847 images, 847 labels

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  Found 23 issues:

❌ Critical (will break training):
   • 2 corrupt images
   • 8 out-of-bounds bounding boxes
   • 1 invalid YOLO format

⚠️  Quality issues (reduces performance):
   • 4 exact duplicates
   • 8 empty label files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾 Creating backup...
   Saved to .modelcub/backups/pills-v1-20241010-143022

🔧 Applying fixes...
   [✓] Removed 2 corrupt images
   [✓] Clipped 8 out-of-bounds boxes
   [✓] Removed 1 invalid annotation
   [✓] Removed 4 duplicate images
   [✓] Flagged 8 empty annotations for review

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Dataset Health: 67/100 → 94/100

   Before: 847 images, 2,847 labels
   After:  841 images, 2,832 labels (-6 images, -15 labels)
   
📊 Detailed report: reports/pills-v1-fix-20241010-143022.html

⏱️  Estimated time saved: ~2 days of debugging
💰 Estimated cost saved: ~$240 in wasted training

To undo: modelcub dataset rollback pills-v1-20241010-143022
```

**Success Criteria:**
- ✅ Fixes all 7 critical issue types correctly
- ✅ Creates reliable backups
- ✅ Doesn't break working datasets
- ✅ HTML report is beautiful and shareable
- ✅ Terminal output is clear and satisfying
- ✅ Fast (processes 10k images in <60 seconds)
- ✅ Rollback works perfectly
- ✅ Report is screenshot-worthy (this is critical!)
- ✅ Python SDK complete
- ✅ Comprehensive tests

**Time Estimate:** 10-12 days

---

#### **WEEKS 7-8: Dataset Versioning & Diff**

**Feature: `modelcub diff` - Git Diff for Datasets**

**Description:**
The second viral feature. Show exactly what changed between dataset versions with beautiful visual diffs. Solves the "dataset versioning hell" problem.

**Commands:**
```bash
# Commit current state
modelcub commit -m "Fixed corrupt images"
modelcub commit --dataset pills-v1 -m "Added 200 new samples"

# View history
modelcub history
modelcub history --dataset pills-v1

# Compare versions
modelcub diff v1 v2
modelcub diff pills-v1@v1 pills-v1@v2
modelcub diff pills-v1@2024-10-10 pills-v1@2024-10-15

# Visual diff (web UI)
modelcub diff v1 v2 --visual

# Export diff report
modelcub diff v1 v2 --export html
modelcub diff v1 v2 --export json

# Stats only (no file-by-file)
modelcub diff v1 v2 --stats-only

# Checkout previous version
modelcub checkout v1
modelcub checkout pills-v1@v1
```

**Implementation Requirements:**

**1. Version Control System:**

**Commit Structure:**
```
.modelcub/history/commits/
└── <commit-hash>/
    ├── metadata.json
    ├── dataset_snapshot.yaml
    └── file_hashes.json
```

**Metadata:**
```json
{
  "commit_id": "a3f9b2e1",
  "dataset": "pills-v1",
  "timestamp": "2024-10-10T14:30:00Z",
  "message": "Fixed corrupt images and added samples",
  "parent": "7c4d8f3a",
  "author": "user@example.com",
  "changes_summary": {
    "images_added": 200,
    "images_removed": 6,
    "images_modified": 0,
    "labels_modified": 89
  },
  "dataset_state": {
    "total_images": 1041,
    "total_labels": 3412,
    "health_score": 94,
    "classes": ["pill", "bottle", "blister"]
  }
}
```

**File Hashes (for efficient diffing):**
```json
{
  "images/train/img_0001.jpg": "xxhash:7a3f9b2e",
  "labels/train/img_0001.txt": "xxhash:1f8e3c4a",
  ...
}
```

**2. Diff Algorithm:**

Compare two commits by:
1. Load file hashes for both versions
2. Find added files (in v2, not in v1)
3. Find removed files (in v1, not in v2)
4. Find modified files (different hashes)
5. For modified labels, parse and compare annotations
6. Generate statistics and impact analysis

**3. Diff Output:**

**Terminal Output:**
```bash
$ modelcub diff pills-v1@v1 pills-v1@v2

📊 Dataset Diff: pills-v1 (v1 → v2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 Summary:
   Images:      847 → 1,041  (+200, -6)
   Labels:      2,847 → 3,412  (+580, -15)
   Classes:     3 → 4  (+1: "capsule")

🔄 Changed Annotations: 89 images

   Top Changes:
   
   img_0234.jpg:
   [-] pill  [x:0.50, y:0.60, w:0.05, h:0.08]  ← removed
   [+] bottle [x:0.48, y:0.58, w:0.06, h:0.09]  ← relabeled
   
   img_0445.jpg:
   [~] pill  [x:0.30, y:0.25, w:0.04, h:0.05]
          → [x:0.32, y:0.27, w:0.04, h:0.05]  (adjusted)
   
   ... (87 more changes)

➕ New Images: 200
   Distribution:
   • train: +150 images
   • val: +30 images
   • test: +20 images
   
   New class "capsule": 145 samples
   Lighting diversity: +22% outdoor scenes

➖ Removed Images: 6
   Reasons (from fix command):
   • 2 corrupt images
   • 4 duplicates

⚠️  Potential Issues:
   [!] Train/val split ratio changed
       Was: 80/14/6
       Now: 82/12/6
       → 23 images moved from val to train
   
   [!] Class distribution shifted
       "pill": 45% → 38% (relative decrease)
       → May impact performance on pill detection

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 Impact Analysis:
   Retraining recommended: YES
   Expected mAP change: +0.08 to +0.12
   Dataset quality: 67/100 → 94/100 (improved)

View details:
  Visual diff: modelcub diff v1 v2 --visual
  Full report: modelcub diff v1 v2 --export html
```

**4. Visual Diff (Web UI):**

Launch localhost web app showing:

**Features:**
- **Side-by-side image comparison**
  - Left: v1 with bounding boxes
  - Right: v2 with bounding boxes
  - Slider to toggle between versions
  
- **Color coding:**
  - 🟢 Green boxes: New annotations
  - 🔴 Red boxes: Removed annotations
  - 🟡 Yellow boxes: Modified annotations
  - ⚪ White boxes: Unchanged
  
- **Filters:**
  - Show only changed images
  - Show only added images
  - Show only removed images
  - Filter by class
  - Filter by split

- **Navigation:**
  - Keyboard shortcuts (arrows)
  - Thumbnail gallery
  - Jump to image by ID

**Tech stack for visual diff:**
- Flask/FastAPI backend
- Simple HTML/CSS/JS frontend (no React needed)
- Tailwind CSS for styling
- Image overlays with canvas or SVG

**5. Python SDK:**
```python
from modelcub import Dataset

ds = Dataset.load("pills-v1")

# Commit current state
commit = ds.commit(message="Fixed labels and added samples")
print(commit.id)  # "a3f9b2e1"

# View history
history = ds.history()
for commit in history:
    print(f"{commit.id}: {commit.message} ({commit.timestamp})")

# Diff between commits
diff = ds.diff("v1", "v2")

# Access diff data
print(f"Images added: {len(diff.added_images)}")
print(f"Images removed: {len(diff.removed_images)}")
print(f"Labels modified: {len(diff.modified_labels)}")

# Detailed changes
for change in diff.label_changes:
    print(f"{change.image}: {change.type}")
    print(f"  Before: {change.before}")
    print(f"  After: {change.after}")

# Impact analysis
print(f"Retraining needed: {diff.retraining_recommended}")
print(f"Expected mAP change: {diff.expected_map_change}")

# Export
diff.export_html("diff_report.html")
diff.export_json("diff_report.json")

# Checkout previous version
ds.checkout("v1")
```

**Success Criteria:**
- ✅ Accurate diffing of image and label changes
- ✅ Fast comparison (10k images in <10 seconds)
- ✅ Beautiful visual diff UI
- ✅ Clear terminal output
- ✅ Impact analysis is useful
- ✅ HTML reports are shareable
- ✅ Commit/history system works reliably
- ✅ Checkout restores exact state
- ✅ Python SDK complete
- ✅ Visual diff is demo-worthy

**Time Estimate:** 12-14 days

---

### **PHASE 3: TRAINING & EVALUATION (Weeks 9-12)**

#### **WEEK 9-10: Basic Training**

**Feature: `modelcub train` - Model Training**

**Description:**
Train YOLO models with sane defaults. Start with basic functionality, add auto-optimization later.

**Commands:**
```bash
# Basic training
modelcub train --dataset pills-v1

# Specify model
modelcub train --dataset pills-v1 --model yolov11n
modelcub train --dataset pills-v1 --model yolov11s

# Common parameters
modelcub train --dataset pills-v1 --epochs 50 --batch-size 16
modelcub train --dataset pills-v1 --image-size 640 --device cuda

# Auto mode (detect best settings)
modelcub train --dataset pills-v1 --auto

# Resume training
modelcub train --resume pills-detect-run1

# Name your run
modelcub train --dataset pills-v1 --name pills-experiment-1

# List runs
modelcub train list
modelcub train list --running
```

**Implementation Requirements:**

**1. Training Pipeline:**
- Use Ultralytics YOLO as backend
- Support YOLOv11 (n, s, m, l, x)
- Support detection and segmentation tasks
- Default hyperparameters that work well
- Multi-GPU support (automatic if available)
- Graceful CPU fallback

**2. Auto Mode:**
When `--auto` flag is used:
- Detect GPU memory → choose best model size
- Analyze dataset size → choose batch size
- Set image size based on dataset
- Enable early stopping (patience=10)
- Auto-select optimizer (AdamW for small, SGD for large)
- Smart learning rate based on batch size

**3. Progress Monitoring:**
```bash
$ modelcub train --dataset pills-v1 --auto

🚀 ModelCub Training Pipeline
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Dataset: pills-v1
   • 841 training images
   • 120 validation images
   • 3 classes: pill, bottle, blister

🤖 Auto-Configuration:
   • Model: YOLOv11n (detected 8GB GPU)
   • Batch size: 16
   • Image size: 640
   • Device: cuda:0
   • Optimizer: AdamW
   • Learning rate: 0.01

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Training started: pills-detect-20241010-153022

Epoch 1/50:
  [████████████████████] 100% | Loss: 2.34 | mAP50: 0.23 | 2m 15s

Epoch 5/50:
  [████████████████████] 100% | Loss: 1.47 | mAP50: 0.56 | 2m 12s

Epoch 10/50:
  [████████████████████] 100% | Loss: 0.82 | mAP50: 0.78 | 2m 10s

...

Epoch 42/50:
  [████████████████████] 100% | Loss: 0.31 | mAP50: 0.89 | 2m 08s
  ✨ New best! Saved to weights/best.pt

Epoch 45/50:
  [████████████████████] 100% | Loss: 0.30 | mAP50: 0.88 | 2m 09s

🛑 Early stopping (patience=10, no improvement)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Training Complete!

   Run: pills-detect-20241010-153022
   Best epoch: 42/50
   Best mAP50: 0.89
   Training time: 1h 32m
   
   Weights:
   • Best: runs/pills-detect-20241010-153022/weights/best.pt
   • Last: runs/pills-detect-20241010-153022/weights/last.pt

Next steps:
  Evaluate: modelcub evaluate pills-detect-20241010-153022
  Export: modelcub export pills-detect-20241010-153022 --format onnx
```

**4. Run Management:**
- Save to `runs/<run-name>/`
- Store config, weights, logs, results
- Add to `.modelcub/runs.yaml` registry
- Track all hyperparameters
- Link to dataset version
- Save environment info (Python, CUDA, PyTorch versions)

**5. Python SDK:**
```python
from modelcub import Model, Dataset

# Load dataset
ds = Dataset.load("pills-v1")

# Create model
model = Model("yolov11n", task="detect")

# Train
run = model.train(
    dataset=ds,
    epochs=50,
    batch_size=16,
    image_size=640,
    device="cuda",
    name="pills-experiment-1"
)

# Or auto mode
run = model.train(dataset=ds, auto=True)

# Access run info
print(run.id)
print(run.best_epoch)
print(run.best_map50)
print(run.training_time)

# Resume training
run2 = run.resume(epochs=100)
```

**Success Criteria:**
- ✅ Successfully trains YOLO models
- ✅ Auto mode works well
- ✅ Reasonable default hyperparameters
- ✅ Progress bar is clear
- ✅ Early stopping works
- ✅ Multi-GPU utilizes all GPUs
- ✅ CPU fallback works
- ✅ Run registry tracks everything
- ✅ Can resume training
- ✅ Python SDK complete

**Time Estimate:** 10-12 days

---

#### **WEEK 11: Evaluation**

**Feature: `modelcub evaluate` - Model Evaluation**

**Description:**
Evaluate trained models and generate detailed metrics reports.

**Commands:**
```bash
# Evaluate on validation set
modelcub evaluate pills-detect-20241010

# Evaluate on test set
modelcub evaluate pills-detect-20241010 --split test

# Custom thresholds
modelcub evaluate pills-detect-20241010 --confidence 0.25 --iou 0.5

# Save predictions
modelcub evaluate pills-detect-20241010 --save-predictions

# Export results
modelcub evaluate pills-detect-20241010 --export json
modelcub evaluate pills-detect-20241010 --export html

# View results
modelcub results pills-detect-20241010
modelcub results pills-detect-20241010 --detailed

# Compare multiple runs
modelcub compare run1 run2 run3
modelcub compare --all
```

**Implementation Requirements:**

**1. Metrics Calculation:**
- mAP50, mAP50-95
- Precision, Recall, F1 per class
- Confusion matrix
- Inference speed (ms per image)
- Per-class breakdown

**2. Results Display:**
```bash
$ modelcub evaluate pills-detect-20241010 --split val

📊 Evaluating pills-detect-20241010 on validation set...
   [████████████████████] 100% | 120 images

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Evaluation Complete

📈 Overall Metrics:
   • mAP50: 0.894
   • mAP50-95: 0.672
   • Precision: 0.881
   • Recall: 0.856
   • F1: 0.868
   • Inference: 12.3ms/image

📊 Per-Class Breakdown:
   
   Class      mAP50    Precision  Recall    F1
   ────────────────────────────────────────────
   pill       0.912    0.894      0.883    0.888
   bottle     0.889    0.876      0.845    0.860
   blister    0.881    0.873      0.841    0.857

🔄 Confusion Matrix:
            pill   bottle  blister  background
   pill     245      3        2         8
   bottle     4    198        1         5
   blister    2      2      156         4

💾 Results saved to:
   • runs/pills-detect-20241010/results/val_results.json
   • runs/pills-detect-20241010/results/confusion_matrix.png

View detailed report:
  modelcub results pills-detect-20241010 --detailed
```

**3. Comparison:**
```bash
$ modelcub compare run1 run2 run3

📊 Run Comparison
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run                      mAP50   Precision  Recall   Time
──────────────────────────────────────────────────────────
pills-detect-v1 (run1)   0.876   0.862      0.834    1h 32m
pills-detect-v2 (run2)   0.894   0.881      0.856    1h 28m  ⭐ Best
pills-detect-v3 (run3)   0.889   0.873      0.851    1h 45m

Key Differences:
• run2 used --batch-size 16 (vs 8)
• run2 trained on pills-v2 (200 more samples)
• run3 used YOLOv11s (larger model)
```

**4. Python SDK:**
```python
from modelcub import Run

# Load run
run = Run.load("pills-detect-20241010")

# Evaluate
results = run.evaluate(split="val")

# Access metrics
print(results.map50)
print(results.map50_95)
print(results.precision)
print(results.recall)

# Per-class metrics
for cls, metrics in results.per_class.items():
    print(f"{cls}: mAP50={metrics.map50}")

# Confusion matrix
print(results.confusion_matrix)

# Export
results.export_json("results.json")
results.export_html("results.html")

# Compare runs
from modelcub import compare_runs
comparison = compare_runs(["run1", "run2", "run3"])
print(comparison.best_run)
print(comparison.leaderboard)
```

**Success Criteria:**
- ✅ Accurate metric calculations
- ✅ Clear results display
- ✅ Per-class breakdowns
- ✅ Confusion matrix generation
- ✅ Run comparison works
- ✅ Export formats work
- ✅ Python SDK complete

**Time Estimate:** 5-6 days

---

#### **WEEK 12: Export & Inference**

**Feature: `modelcub export` & `modelcub infer` - Deployment**

**Description:**
Export trained models to deployment formats and run inference.

**Commands:**
```bash
# Export to ONNX
modelcub export pills-detect-20241010 --format onnx

# Export to TensorRT
modelcub export pills-detect-20241010 --format tensorrt

# Other formats
modelcub export pills-detect-20241010 --format torchscript
modelcub export pills-detect-20241010 --format coreml

# Inference
modelcub infer pills-detect-20241010 --image test.jpg
modelcub infer pills-detect-20241010 --images ./test_folder/
modelcub infer pills-detect-20241010 --video video.mp4

# Save results
modelcub infer pills-detect-20241010 --image test.jpg --save
modelcub infer pills-detect-20241010 --image test.jpg --save-txt
```

**Implementation Requirements:**

**1. Export Formats:**
- ONNX (priority 1)
- TensorRT (priority 2)
- TorchScript (priority 3)
- CoreML (nice to have)

**2. Inference:**
- Support images, folders, videos
- Visualize predictions
- Save results in various formats
- Batch processing for efficiency

**3. Python SDK:**
```python
from modelcub import Run

run = Run.load("pills-detect-20241010")

# Export
run.export(format="onnx", output="model.onnx")

# Inference
predictions = run.predict("test.jpg")
for pred in predictions:
    print(f"{pred.class_name}: {pred.confidence}")

# Batch inference
results = run.predict_batch(["img1.jpg", "img2.jpg"])
```

**Success Criteria:**
- ✅ ONNX export works
- ✅ TensorRT export works (with CUDA)
- ✅ Inference is fast and accurate
- ✅ Visualizations are clear
- ✅ Python SDK complete

**Time Estimate:** 5-6 days

---

### **PHASE 4: POLISH & LAUNCH (Weeks 13-16)**

#### **WEEK 13: Documentation & Examples**

**Deliverables:**
1. **README.md** - Beautiful, comprehensive
2. **docs/** - Full documentation site
3. **examples/** - 5+ working examples
4. **CONTRIBUTING.md** - Clear guidelines
5. **Installation guide** - All platforms
6. **Quickstart tutorial** - 5-minute guide
7. **API reference** - Complete SDK docs

**Time Estimate:** 7 days

---

#### **WEEK 14: Testing & Bug Fixes**

**Deliverables:**
1. Comprehensive test suite (>80% coverage)
2. Integration tests
3. Performance benchmarks
4. Bug fixes from dogfooding
5. Edge case handling
6. Cross-platform testing

**Time Estimate:** 7 days

---

#### **WEEK 15: Demo Content Creation**

**Deliverables:**
1. **Hero demo video** (90 seconds)
2. **Feature demos** (30 seconds each)
3. **Screenshots** for README
4. **GIFs** for key features
5. **Launch blog post**
6. **HN post** draft
7. **Social media content**

**Time Estimate:** 7 days

---

#### **WEEK 16: Launch Week**

**Monday:** Soft launch to friends/beta users
**Tuesday:** Fix critical feedback
**Wednesday:** HN launch (8-10am PT)
**Thursday:** Reddit launches (r/MachineLearning, r/computervision)
**Friday:** Product Hunt launch
**Weekend:** Community engagement, bug fixes

---

## 🎯 MINIMUM VIABLE 1.0 FEATURE LIST

For reference, these are the MUST-HAVE features for 1.0 launch:

### ✅ Core (Blocks Launch):
1. `modelcub init` - Project initialization
2. `modelcub dataset add` - Import YOLO + Roboflow
3. `modelcub dataset list/info` - Dataset management
4. `modelcub dataset validate` - Validation
5. `modelcub dataset fix` - Auto-fix with reports
6. `modelcub commit/history` - Version control
7. `modelcub diff` - Visual diffs
8. `modelcub train` - Basic training + auto mode
9. `modelcub evaluate` - Evaluation
10. `modelcub export` - ONNX/TensorRT
11. `modelcub infer` - Inference
12. Python SDK - All core features
13. Documentation - Complete
14. Tests - >80% coverage

### 🟡 Nice to Have (1.1):
- Auto-labeling
- Dashboard UI
- More formats (COCO, VOC)
- Advanced analytics
- Integrations (W&B, etc.)

---

## 📈 SUCCESS METRICS

### Week 1 (Launch):
- 5,000+ GitHub stars
- Hacker News front page (>300 points)
- 50+ Reddit upvotes on r/MachineLearning
- 10+ blog mentions/tweets

### Month 1:
- 500+ active users
- 10+ GitHub contributors
- 50+ GitHub issues/discussions
- 1,000+ PyPI downloads

### Month 3:
- 10,000+ stars
- 2,000+ active users
- 50+ contributors
- First consulting client

---

## 🚀 LAUNCH STRATEGY

### Pre-Launch (Week 15):
- Build in public (tweet progress)
- Soft launch to beta users
- Gather testimonials
- Prepare demo content

### Launch Day (Week 16, Wednesday):
1. **8:00 AM PT** - Post to Hacker News
2. **9:00 AM PT** - Tweet announcement
3. **10:00 AM PT** - Post to Reddit
4. **All day** - Engage in comments
5. **Evening** - Respond to issues/questions

### Post-Launch (Week 17+):
- Daily engagement with community
- Weekly updates
- Bug fixes based on feedback
- Plan 1.1 features

---

## 💬 POSITIONING & MESSAGING

### Taglines:
- "Roboflow without the rent. Your data. Your GPU. Your rules."
- "Open-source, local-first MLOps for computer vision"
- "Git for CV datasets + Training automation"

### Key Messages:
1. **Privacy-first**: Your medical/pharma data never leaves your machine
2. **Cost savings**: $0 vs $8k+/month for Roboflow
3. **Reproducible**: Version everything like code
4. **No vendor lock-in**: Open source, your infrastructure

### Target Audiences:
1. **Primary**: Pharma/medical AI teams (privacy-sensitive)
2. **Secondary**: Academic researchers (need reproducibility)
3. **Tertiary**: Indie developers (hit Roboflow pricing wall)

---

## 🛠️ TECHNICAL DECISIONS SUMMARY

### Languages & Frameworks:
- **Python 3.9+** (CLI + SDK)
- **Click/Typer** (CLI framework)
- **PyTorch + Ultralytics** (Deep learning)
- **Flask/FastAPI** (Web UI)
- **pytest** (Testing)

### Internal Format:
- **YOLO format** as standard
- Text-based for git compatibility
- Easy to parse and validate

### Version Control:
- Commit-based system (git-inspired)
- Store hashes for efficient diffs
- Lightweight snapshots

### File Organization:
```
.modelcub/        # Hidden, like .git
data/             # All datasets
runs/             # All training runs
reports/          # Generated reports
modelcub.yaml     # Main config
```

---

## ⚠️ RISKS & MITIGATION

### Risk 1: Scope Creep
**Mitigation:** Strict feature freeze at Week 12. Everything else is 1.1+.

### Risk 2: Performance Issues
**Mitigation:** Benchmark early. Optimize hot paths. Use efficient hashing (xxHash).

### Risk 3: Complex Edge Cases
**Mitigation:** Start with clean datasets. Add edge cases in 1.1. Document limitations.

### Risk 4: Launch Timing
**Mitigation:** Launch Tuesday-Thursday 8-10am PT. Avoid holidays/big tech news.

### Risk 5: Competition Response
**Mitigation:** Open source moat. Community focus. Speed of iteration.

---

## 📝 NOTES FOR CONTEXT TRANSFER

When starting a new conversation with an AI assistant, provide:

1. This entire document
2. Current week number
3. What's been completed
4. What you're currently working on
5. Any blockers or questions

The assistant should be able to:
- Understand the full project vision
- Know what features exist and what's planned
- Provide advice aligned with the timeline
- Help debug issues
- Suggest optimizations

---

## 🎉 THE GOAL

By Week 16, we have:
- A working, polished product
- 5k+ stars proving market validation
- Happy users providing testimonials
- A clear roadmap to 1.1
- Foundation for building a business

ModelCub becomes the de facto OSS tool for local-first CV workflows.

---

**This is your north star. Everything else is negotiable.**