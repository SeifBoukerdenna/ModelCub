# ModelCub: The Complete Project Specification

**Tagline:** The cleanest, most powerful local-first computer vision platform.

---

## 🎯 THE VISION

### **Mission Statement**

**ModelCub is the complete local-first computer vision platform.**

We handle the entire CV workflow—import, annotate, validate, fix, version, train, evaluate, deploy—in one unified tool that works 100% offline. We're not building another fragmented toolkit. We're building the integrated platform that should exist: beautiful, powerful, and yours to control.

### **The North Star (3-5 Year Goal)**

When someone starts a computer vision project, their first action is: **`pip install modelcub`**

**Year 1:** The best local-first CV platform (2,000-3,000 stars)
**Year 2:** Default for serious CV work (10,000-15,000 stars, $100-300k revenue)
**Year 3:** Real Roboflow competitor (20,000-30,000 stars, $500k-1M revenue)
**Year 4-5:** Industry standard (50,000+ stars, acquisition or $5M+ revenue)

### **The Origin Story**

Built by a developer who worked at a pharmaceutical AI startup where they paid Roboflow $8,000/month for a single project. Medical imaging data sat on external servers. Every experiment required uploading, waiting, downloading. Labeling was done in Roboflow's UI. Training in their cloud. No control. No privacy. No offline mode.

**This is the tool that should exist: Complete platform. Local-first. Beautiful. Yours.**

---

## 💡 THE PHILOSOPHY

### **Core Principles**

#### **1. Complete Platform, Not Fragmented Tools**
```
❌ Wrong: Use Label Studio + DVC + Ultralytics + custom scripts
✅ Right: One tool, complete workflow, cohesive experience

Everything integrated:
- Import → Annotate → Validate → Fix → Train → Deploy
- CLI + Python SDK + Local Web UI
- One tool that does everything excellently
```

#### **2. Local-First, Always**
```
✅ Runs entirely offline
✅ Your data never leaves your machine
✅ Perfect for sensitive industries (pharma, medical, defense)
✅ No cloud required (cloud is optional convenience)
✅ Own your infrastructure
✅ No vendor lock-in
```

#### **3. Beautiful Experiences, Not Just Functional**
```
✅ Terminal output that makes you smile
✅ Web UI that feels premium
✅ Smooth animations, thoughtful interactions
✅ Every detail polished
✅ Beauty AND power

Design principle: "Delightful to use every day"
```

#### **4. Power + Simplicity**
```
For beginners:
$ modelcub init project
$ modelcub ui  # Opens beautiful interface
# Click, annotate, train

For power users:
$ modelcub import ./data | modelcub fix --auto | modelcub train --auto
# One pipeline, infinite automation

Both experiences first-class.
```

#### **5. Transparent, Not Magic**
```
✅ Clear error messages
✅ Explain what changed
✅ Show expected impact
✅ Generate detailed reports
✅ No black boxes
✅ You understand what's happening
```

#### **6. Open Core, Forever Free**
```
✅ Core platform: Free forever (Apache 2.0)
✅ All features work locally
✅ No artificial limits
✅ Community-driven

Paid tier (future): Convenience, not features
- Managed cloud hosting
- Team collaboration
- Advanced AI features
```

---

## 🏆 COMPETITIVE POSITIONING

### **The New Landscape**

**We're not just competing with Roboflow. We're replacing the entire fragmented toolchain.**

```
Current state (fragmented):
├─ Label Studio (labeling)
├─ DVC (version control)
├─ Ultralytics (training)
├─ Custom scripts (validation, conversion)
└─ Roboflow (if you pay $$$)

ModelCub (unified):
└─ Everything in one beautiful platform
```

### **vs. Roboflow**

```
Roboflow:
├─ Strengths: Complete platform, polished UI, easy
├─ Weaknesses: Cloud-only, $8k+/month, vendor lock-in, no privacy
└─ Our advantage: Local-first, free, open source, YOU control it

Our positioning: "Roboflow, but you own it"
```

### **vs. Label Studio**

```
Label Studio:
├─ Strengths: Great labeling UI, free, open source
├─ Weaknesses: Labeling only, no training, complex setup
└─ Our advantage: Complete workflow, training integrated, simpler

Our positioning: "Label Studio + training + data tools in one"
```

### **vs. Ultralytics**

```
Ultralytics:
├─ Strengths: Best YOLO implementation, great docs
├─ Weaknesses: Training-focused, no labeling, weak data management
└─ Our advantage: Complete platform, labeling + data + training

Our positioning: "Ultralytics + labeling + data management"
```

### **vs. CVAT**

```
CVAT:
├─ Strengths: Advanced labeling features, video support
├─ Weaknesses: Complex setup, labeling only, enterprise-focused
└─ Our advantage: Simple setup, complete workflow, indie-friendly

Our positioning: "CVAT's power, Roboflow's simplicity, your infrastructure"
```

### **Our Unique Position**

**What ONLY ModelCub offers:**
1. ✅ Complete local-first platform (label + train + deploy)
2. ✅ Beautiful integrated experience (not separate tools)
3. ✅ Auto-fix with health scoring (nobody has this)
4. ✅ Version control with visual diffs (nobody has this well)
5. ✅ Clean, modern design (most tools look like 2010)
6. ✅ Free forever with no limits (Roboflow charges thousands)

**The tagline that wins:**
> "The complete computer vision platform. Beautiful, powerful, local-first, free."

---

## 🎯 TARGET USERS

### **Primary: Indie Developers & Small Startups (2-10 people)**

**Profile:**
- Building CV products (detection, segmentation, classification)
- Currently juggling 3-5 different tools
- Love Roboflow but hate the pricing
- Need labeling + training + deployment
- Want clean, modern tools
- Comfortable with CLI + GUI

**Pain Points:**
- Roboflow costs $3k-10k/month as they scale
- Data on someone else's servers
- Switching between Label Studio, Ultralytics, DVC
- No cohesive workflow
- Privacy concerns

**What they want:**
- One tool that does everything
- Beautiful, modern UI
- Works offline
- Free (or cheap)
- Easy to use but powerful

**What they'll pay for (Year 2):**
- Cloud hosting (convenience)
- Team collaboration
- Advanced AI features (GPT-4V labeling, active learning)
- Priority support

### **Secondary: Medical/Pharma/Defense Teams**

**Profile:**
- Highly regulated industries
- CANNOT use cloud tools (compliance)
- Need air-gapped solutions
- Budget for software ($10k-100k/year)
- Need audit trails, reproducibility

**Pain Points:**
- Roboflow violates privacy/compliance requirements
- Cannot use cloud-based tools
- Need on-premise solutions
- Must track every change

**What they want:**
- Local-first (required)
- Audit trails
- Reproducibility
- Professional support
- On-prem deployment options

### **Tertiary: Academic Researchers**

**Profile:**
- Publishing papers
- Need reproducibility
- Limited budget
- Long-term projects (months/years)

**Pain Points:**
- Need to version datasets
- Results must be reproducible
- Budget constraints
- Tools break between experiments

**What they want:**
- Free
- Reproducible
- Version control
- Citation-ready

---

## 🏗️ TECHNICAL ARCHITECTURE

### **Technology Stack**

```
Core (CLI + SDK):
├─ Language: Python 3.9+
├─ CLI Framework: Click
├─ Deep Learning: PyTorch, Ultralytics (YOLO v8/v11)
├─ Computer Vision: OpenCV, PIL
├─ Data Processing: NumPy, Pandas
└─ Terminal UI: Rich (beautiful output)

Web UI (Local Server):
├─ Backend: FastAPI
├─ Frontend: React + TypeScript
├─ Styling: Tailwind CSS
├─ Canvas: Konva.js (for annotation)
├─ Real-time: WebSockets (live training updates)
└─ State: Zustand (simple, fast)

Storage:
├─ Metadata: YAML/JSON files
├─ Hashing: xxHash (fast file hashing)
├─ Database: SQLite (for UI, query performance)
└─ File format: YOLO (primary internal format)

Testing:
└─ Framework: pytest (target: 85%+ coverage)
```

### **Architecture Principles**

#### **1. API-First Design**
```
Everything is API-first:
├─ CLI calls Python SDK
├─ Python SDK calls Core API
├─ Web UI calls FastAPI
└─ FastAPI calls Core API

One source of truth: Core API
Everything else is interface layer.
```

#### **2. Stateless Web UI**
```
UI is pure view layer:
├─ All state in filesystem (.modelcub/)
├─ UI reads from filesystem
├─ Multiple UI instances can run
└─ No database state (except SQLite cache)

Kill server, restart, everything still works.
```

#### **3. Plugin Architecture (Future)**
```
Core:
├─ Dataset operations
├─ Training pipeline
├─ Annotation tools

Plugins (future):
├─ Custom augmentations
├─ New model architectures
├─ Format converters
└─ Export targets
```

### **Internal Format**

**Primary format:** YOLO (v5/v8/v11 compatible)

**Why YOLO:**
- ✅ Simple text-based format
- ✅ Universal compatibility
- ✅ Easy to parse and validate
- ✅ Industry standard
- ✅ Git-friendly (human-readable)
- ✅ Supports detection + segmentation

**Import/Export support:**
- Import: YOLO, Roboflow, COCO (basic)
- Export: YOLO, COCO, TFRecord
- Internal: Always YOLO

### **Directory Structure**

```
project-name/
├── .modelcub/
│   ├── config.yaml              # Project configuration
│   ├── datasets.yaml            # Dataset registry
│   ├── runs.yaml                # Training runs registry
│   ├── annotations.db           # SQLite (for UI query performance)
│   ├── history/                 # Version control
│   │   ├── commits/             # Dataset commits
│   │   └── snapshots/           # Full snapshots
│   ├── backups/                 # Auto-fix backups
│   └── cache/                   # Temporary files
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
│           ├── dataset.yaml     # YOLO format config
│           └── metadata.json    # ModelCub metadata
├── runs/
│   └── <run-name>/
│       ├── weights/
│       ├── results/
│       └── config.yaml
├── reports/                     # Generated HTML reports
└── modelcub.yaml               # Main project file
```

---

## 📋 COMPLETE FEATURE SPECIFICATION (MVP)

### **THE FOUR PILLARS**

```
1. DATASET OPERATIONS (Week 2-6)
   └─ Import, validate, fix, version, export

2. ANNOTATION SYSTEM (Week 7-10)
   └─ Label images, manage classes, review

3. TRAINING PIPELINE (Week 11-12)
   └─ Train, evaluate, export models

4. WEB INTERFACE (Week 3-14, parallel)
   └─ Beautiful UI for everything above
```

---

## 🗂️ PILLAR 1: DATASET OPERATIONS

### **Feature 1.1: Project Management**

**Status:** ✅ DONE

**CLI:**
```bash
modelcub init my-project
modelcub status
modelcub info
```

**Python SDK:**
```python
from modelcub import Project

project = Project.init("my-project")
project = Project.load(".")
print(project.name, project.datasets, project.runs)
```

---

### **Feature 1.2: Dataset Import**

**Week:** 2-3

**CLI:**
```bash
# Import from YOLO
modelcub import ./yolo_data --name dataset-v1

# Import from Roboflow export
modelcub import ./export.zip --name dataset-v1

# Import unlabeled images (for annotation)
modelcub import ./images/ --name unlabeled-v1 --unlabeled

# List datasets
modelcub dataset list

# Dataset info
modelcub dataset info dataset-v1
```

**Python SDK:**
```python
from modelcub import Dataset

# Import
ds = Dataset.from_yolo("./data", name="v1")
ds = Dataset.from_roboflow("export.zip", name="v1")
ds = Dataset.from_images("./images/", name="unlabeled-v1")

# Info
print(ds.name, ds.num_images, ds.classes)
print(ds.splits.train.images)  # 677

# Stats
stats = ds.stats()
print(stats.class_distribution)
print(stats.images_per_split)
```

**Supports:**
- ✅ YOLO format (detection + segmentation)
- ✅ Roboflow exports (ZIP)
- ✅ COCO format (basic)
- ✅ Unlabeled images (for annotation)
- ✅ Validates during import
- ✅ Progress bars for large datasets

---

### **Feature 1.3: Dataset Validation**

**Week:** 4

**CLI:**
```bash
modelcub validate dataset-v1
modelcub validate dataset-v1 --export report.html
```

**What it detects:**
1. ❌ Corrupt/unreadable images
2. ❌ Missing files (images or labels)
3. ❌ Out-of-bounds coordinates
4. ❌ Invalid YOLO format
5. ⚠️ Duplicate images
6. ⚠️ Empty labels
7. ⚠️ Class imbalance
8. ⚠️ Split size issues

**Output:**
```bash
🔍 Validating dataset-v1...
   [████████████████████] 847/847

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Validation Complete

Dataset Health: 67/100 ⚠️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ CRITICAL (23 issues):
   • 2 corrupt images
   • 8 out-of-bounds boxes
   • 1 invalid format

⚠️  QUALITY (12 issues):
   • 4 duplicates
   • 8 empty labels

💡 Fix: modelcub fix dataset-v1 --auto

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### **Feature 1.4: Auto-Fix**

**Week:** 5-6

**CLI:**
```bash
# Auto-fix everything
modelcub fix dataset-v1 --auto

# Interactive
modelcub fix dataset-v1 --interactive

# Generate report
modelcub fix dataset-v1 --auto --report
```

**What it fixes:**
1. ✅ Removes corrupt images
2. ✅ Clips out-of-bounds boxes
3. ✅ Removes invalid annotations
4. ✅ Removes duplicates
5. ✅ Creates missing split folders

**Output:**
```bash
🔧 Fixing dataset-v1...

✓ Removed 2 corrupt images
✓ Clipped 8 out-of-bounds boxes
✓ Removed 4 duplicates

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ Dataset Health: 67 → 94 (+40%)

Before: 847 images
After:  841 images

⏱️  Time saved: ~2 days
💰 Cost saved: ~$200 in wasted GPU

Backup: .modelcub/backups/dataset-v1-20250112

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Python SDK:**
```python
ds = Dataset.load("dataset-v1")
result = ds.fix(auto=True)

print(f"Health: {result.before} → {result.after}")
print(f"Fixed: {result.num_fixed} issues")

# Rollback if needed
ds.rollback(result.backup_id)
```

---

### **Feature 1.5: Version Control**

**Week:** Integrated throughout

**CLI:**
```bash
# Commit current state
modelcub commit -m "Fixed corrupt images"

# View history
modelcub history
modelcub log

# Compare versions
modelcub diff v1 v2
modelcub diff HEAD~1 HEAD

# Checkout previous version
modelcub checkout v1
```

**What it tracks:**
- Dataset changes (files added/removed/modified)
- Annotation changes (labels modified)
- Class changes (classes added/removed)
- Split changes (images moved between splits)

**Python SDK:**
```python
ds = Dataset.load("dataset-v1")

# Commit
commit = ds.commit("Fixed labels")

# History
history = ds.history()
for commit in history:
    print(commit.id, commit.message, commit.timestamp)

# Diff
diff = ds.diff("v1", "v2")
print(f"Added: {len(diff.added)}")
print(f"Removed: {len(diff.removed)}")
print(f"Modified: {len(diff.modified)}")

# Checkout
ds.checkout("v1")
```

---

### **Feature 1.6: Export**

**CLI:**
```bash
# Export to different formats
modelcub export dataset-v1 --format yolo --output ./export/
modelcub export dataset-v1 --format coco --output ./export/
```

---

## 🎨 PILLAR 2: ANNOTATION SYSTEM

### **Feature 2.1: Web-Based Annotation Interface**

**Week:** 7-10

**Access:**
```bash
# Start UI server
modelcub ui

# Opens browser at http://localhost:8000
# Or: modelcub ui --port 3000
```

**Annotation UI Features:**

#### **Canvas Interface:**
```
┌────────────────────────────────────────────────────────────┐
│ ModelCub - Annotate: dataset-v1                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ [Classes]          [Main Canvas]        [Properties]      │
│                                                            │
│ ☑ pill             ┌──────────────┐    Selected:          │
│ ☑ bottle           │              │    Class: pill        │
│ ☑ blister          │   [Image     │    Conf: 100%         │
│                    │    with      │    x: 0.45            │
│ [+ Add Class]      │    boxes]    │    y: 0.32            │
│                    │              │    w: 0.12            │
│ [Tools]            │              │    h: 0.15            │
│ 🔲 Rectangle       │              │                       │
│ ⬡ Polygon          └──────────────┘    [Delete] [Copy]   │
│ ✏️ Edit                                                    │
│ 🗑️ Delete          Progress: 45/847                       │
│                    Health: 94/100                         │
│                                                            │
│ [< Prev]  [Save]  [Next >]  [Skip]                       │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

#### **Core Features:**

**1. Drawing Tools:**
- ✅ Bounding boxes (rectangle tool)
- ✅ Polygons (segmentation)
- ✅ Edit mode (move, resize, adjust vertices)
- ✅ Delete tool
- ✅ Copy/paste annotations
- ✅ Undo/redo (Ctrl+Z, Ctrl+Y)

**2. Keyboard Shortcuts:**
```
R - Rectangle tool
P - Polygon tool
E - Edit mode
Del - Delete selected
Ctrl+C/V - Copy/paste
Ctrl+Z/Y - Undo/redo
Space - Next image
Shift+Space - Previous image
1-9 - Quick select class
S - Save
```

**3. Class Management:**
- ✅ Add/remove/rename classes
- ✅ Color coding per class
- ✅ Quick select (number keys)
- ✅ Class search/filter

**4. Navigation:**
- ✅ Next/previous image
- ✅ Jump to image number
- ✅ Filter (labeled/unlabeled/has issues)
- ✅ Search by filename
- ✅ Grid view (thumbnail gallery)

**5. Smart Features:**
- ✅ Auto-save (every change)
- ✅ Progress tracking
- ✅ Show/hide labels
- ✅ Zoom and pan
- ✅ Brightness/contrast adjustment
- ✅ Show only selected class

**6. Validation While Labeling:**
- ✅ Real-time bounds checking
- ✅ Warn on very small/large boxes
- ✅ Suggest fixes for issues

#### **UI Design Principles:**

**Clean & Modern:**
```
- Tailwind CSS for consistent styling
- Dark mode default (light mode option)
- Smooth animations (60fps)
- No clutter, every pixel intentional
- Professional, not toy-like
```

**Fast & Responsive:**
```
- Canvas rendering (Konva.js)
- Lazy load images
- Keyboard-first (mouse optional)
- <16ms frame time
- No lag, no jank
```

**Beautiful Details:**
```
- Smooth box drawing
- Elegant hover states
- Satisfying save animation
- Progress celebration (confetti at 100%)
- Thoughtful micro-interactions
```

---

### **Feature 2.2: CLI Annotation Management**

**CLI:**
```bash
# Launch annotation UI
modelcub annotate dataset-v1
# Same as: modelcub ui --dataset dataset-v1

# Annotation stats
modelcub annotate stats dataset-v1

# Export annotations only
modelcub annotate export dataset-v1 --output ./labels/
```

---

### **Feature 2.3: Annotation Review Mode**

**In UI:**
- Review mode (show all annotations)
- Flag suspicious labels
- Quick fix interface
- Consensus labeling (future: multi-annotator)

**Features:**
- ✅ See all annotations at once
- ✅ Filter by confidence
- ✅ Flag for review
- ✅ Batch operations (delete, change class)

---

## 🚀 PILLAR 3: TRAINING PIPELINE

### **Feature 3.1: Model Training**

**Week:** 11-12

**CLI:**
```bash
# Basic training
modelcub train dataset-v1

# With options
modelcub train dataset-v1 --model yolov8n --epochs 50 --batch-size 16

# Auto mode (smart defaults)
modelcub train dataset-v1 --auto

# Resume training
modelcub resume run-20250112

# List runs
modelcub runs list
```

**Output:**
```bash
🚀 Training dataset-v1...

Auto-configuration:
• Model: YOLOv8n (detected 8GB GPU)
• Batch size: 16
• Epochs: 50
• Device: cuda:0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Epoch 10/50: Loss=0.82 mAP=0.78 [2m 10s]
Epoch 20/50: Loss=0.45 mAP=0.85 [2m 08s]
Epoch 30/50: Loss=0.35 mAP=0.88 [2m 07s]
Epoch 42/50: Loss=0.31 mAP=0.89 ⭐ Best!
Epoch 50/50: Loss=0.29 mAP=0.88 [2m 09s]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Training Complete!

Run: run-20250112
Best: Epoch 42, mAP 0.89
Time: 1h 32m

Weights: runs/run-20250112/weights/best.pt

Next: modelcub evaluate run-20250112

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Python SDK:**
```python
from modelcub import Model, Dataset

ds = Dataset.load("dataset-v1")
model = Model("yolov8n")

# Train
run = model.train(ds, epochs=50, batch_size=16)
# Or auto
run = model.train(ds, auto=True)

# Access results
print(run.best_map)      # 0.89
print(run.best_epoch)    # 42
print(run.training_time) # "1h 32m"

# Resume
run2 = run.resume(epochs=100)
```

**Features:**
- ✅ YOLOv8/v11 (n, s, m, l, x)
- ✅ Auto-configuration
- ✅ Progress tracking
- ✅ Real-time metrics
- ✅ Early stopping
- ✅ Multi-GPU support
- ✅ Resume training

---

### **Feature 3.2: Live Training Monitor (in UI)**

**Features:**
- Real-time loss curves
- Real-time mAP curves
- Learning rate schedule
- Sample predictions (refreshed each epoch)
- ETA and time elapsed
- GPU utilization

**WebSocket Integration:**
```
UI ←─ WebSocket ─→ Training Process
     (live updates)
```

---

### **Feature 3.3: Evaluation**

**CLI:**
```bash
modelcub evaluate run-20250112
modelcub evaluate run-20250112 --split test
```

**Output:**
```bash
📊 Evaluating run-20250112...
   [████████████████████] 120/120

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Results

Overall:
• mAP50: 0.894
• mAP50-95: 0.672
• Precision: 0.881
• Recall: 0.856

Per-Class:
┌─────────┬───────┬───────────┬────────┐
│ Class   │ mAP50 │ Precision │ Recall │
├─────────┼───────┼───────────┼────────┤
│ pill    │ 0.912 │ 0.894     │ 0.883  │
│ bottle  │ 0.889 │ 0.876     │ 0.845  │
│ blister │ 0.881 │ 0.873     │ 0.841  │
└─────────┴───────┴───────────┴────────┘

Confusion matrix: runs/run-20250112/confusion_matrix.png

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Python SDK:**
```python
run = Run.load("run-20250112")
results = run.evaluate(split="val")

print(results.map50)         # 0.894
print(results.precision)     # 0.881
print(results.per_class)     # Dict with per-class metrics
```

---

### **Feature 3.4: Export & Inference**

**Export:**
```bash
# Export to ONNX
modelcub export run-20250112 --format onnx

# Export to TorchScript
modelcub export run-20250112 --format torchscript
```

**Inference:**
```bash
# Single image
modelcub infer run-20250112 --image test.jpg

# Folder
modelcub infer run-20250112 --folder ./test_images/

# Save results
modelcub infer run-20250112 --image test.jpg --save
```

**Python SDK:**
```python
run = Run.load("run-20250112")

# Export
run.export("onnx", "model.onnx")

# Inference
predictions = run.predict("test.jpg")
for pred in predictions:
    print(f"{pred.class_name}: {pred.confidence:.2f}")
    print(f"  Box: {pred.box}")
```

---

## 🖥️ PILLAR 4: WEB INTERFACE

### **Feature 4.1: Local Server**

**Week:** 3-14 (parallel with features)

**Start server:**
```bash
modelcub ui
modelcub ui --port 3000
modelcub ui --host 0.0.0.0  # Allow network access
```

**Architecture:**
```
Browser ←─ HTTP/WS ─→ FastAPI ←─ Calls ─→ Core API
   ↓                      ↓
React App            Python SDK
   ↓
Zustand State
```

---

### **Feature 4.2: UI Pages**

#### **Dashboard (Home)**
```
┌─────────────────────────────────────────────────┐
│ ModelCub                        [Settings] [?]  │
├─────────────────────────────────────────────────┤
│                                                 │
│ 📊 Project: my-cv-project                      │
│                                                 │
│ ┌──────────────┐  ┌──────────────┐            │
│ │  Datasets    │  │  Runs        │            │
│ │  3 total     │  │  5 total     │            │
│ │  847 images  │  │  2 training  │            │
│ │  [View All]  │  │  [View All]  │            │
│ └──────────────┘  └──────────────┘            │
│                                                 │
│ 🚀 Quick Actions:                              │
│ • [Import Dataset]                             │
│ • [Annotate Images]                            │
│ • [Train Model]                                │
│                                                 │
│ 📈 Recent Activity:                            │
│ • dataset-v2: Training complete (mAP: 0.89)    │
│ • dataset-v1: 45 new annotations               │
│ • dataset-v1: Fixed 23 issues                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### **Datasets Page**
```
┌─────────────────────────────────────────────────┐
│ Datasets                           [+ Import]   │
├─────────────────────────────────────────────────┤
│                                                 │
│ [Search]  [Filter: All ▼]  [Sort: Recent ▼]   │
│                                                 │
│ ┌─────────────────────────────────────────┐   │
│ │ pills-v1                Health: 94/100  │   │
│ │ 847 images • 3 classes                  │   │
│ │ [Annotate] [Validate] [Train] [•••]    │   │
│ └─────────────────────────────────────────┘   │
│                                                 │
│ ┌─────────────────────────────────────────┐   │
│ │ defects-v2              Health: 87/100  │   │
│ │ 1,203 images • 5 classes                │   │
│ │ [Annotate] [Validate] [Train] [•••]    │   │
│ └─────────────────────────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### **Annotation Page**
(Described in Feature 2.1)

#### **Training Page**
```
┌─────────────────────────────────────────────────┐
│ Training                          [New Run]     │
├─────────────────────────────────────────────────┤
│                                                 │
│ Active Runs:                                    │
│                                                 │
│ ┌─────────────────────────────────────────┐   │
│ │ 🟢 pills-v2-run3        Epoch 42/50     │   │
│ │                                         │   │
│ │ [Loss curve - live updating]            │   │
│ │ [mAP curve - live updating]             │   │
│ │                                         │   │
│ │ Current: mAP 0.89 | Loss 0.31           │   │
│ │ ETA: 18 minutes                         │   │
│ │                                         │   │
│ │ [Pause] [Stop] [View Details]           │   │
│ └─────────────────────────────────────────┘   │
│                                                 │
│ Completed Runs:                                │
│ • pills-v1-run2: mAP 0.87 (2 hours ago)       │
│ • pills-v1-run1: mAP 0.82 (1 day ago)         │
│                                                 │
└─────────────────────────────────────────────────┘
```

#### **Settings Page**
```
General:
• Project name
• Default device (cuda/cpu/mps)
• Default batch size
• Default image size

Annotation:
• Auto-save interval
• Default class colors
• Keyboard shortcuts

Training:
• Default model (yolov8n)
• Auto-configuration (on/off)
• Save frequency

Advanced:
• Storage location
• Cache size
• Backup retention
```

---

### **Feature 4.3: Real-Time Updates**

**WebSocket Events:**
```python
# Training events
training.started
training.epoch_complete
training.complete
training.failed

# Annotation events
annotation.saved
annotation.batch_complete

# Dataset events
dataset.imported
dataset.validated
dataset.fixed
```

**UI updates in real-time without refresh.**

---

### **Feature 4.4: Mobile-Friendly (Responsive)**

All pages work on tablets:
- Dashboard ✅
- Datasets list ✅
- Training monitor ✅
- Annotation (desktop only - too complex for mobile)

---

## 🎨 DESIGN SYSTEM

### **Visual Language**

**Colors:**
```css
/* Dark mode (default) */
--background: #0a0a0a
--surface: #1a1a1a
--surface-hover: #2a2a2a
--primary: #3b82f6  /* Blue */
--success: #10b981  /* Green */
--warning: #f59e0b  /* Orange */
--error: #ef4444    /* Red */
--text: #ffffff
--text-muted: #9ca3af

/* Light mode */
--background: #ffffff
--surface: #f9fafb
--surface-hover: #f3f4f6
--primary: #2563eb
--success: #059669
--warning: #d97706
--error: #dc2626
--text: #111827
--text-muted: #6b7280
```

**Typography:**
```css
/* Headers */
font-family: Inter, system-ui, sans-serif
h1: 32px, font-weight: 700
h2: 24px, font-weight: 600
h3: 20px, font-weight: 600

/* Body */
font-size: 14px
line-height: 1.5

/* Code */
font-family: 'JetBrains Mono', monospace
```

**Spacing:**
```css
/* 4px base unit */
xs: 4px
sm: 8px
md: 16px
lg: 24px
xl: 32px
2xl: 48px
```

**Animations:**
```css
/* Smooth, fast, natural */
transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1)

/* Emphasis */
transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1)
```

**Components:**
```
Buttons:
• Primary: Blue, rounded, hover lift
• Secondary: Gray outline, rounded
• Danger: Red, rounded
• Icon: Square, subtle

Cards:
• Rounded corners (8px)
• Subtle shadow
• Hover lift effect

Inputs:
• Rounded (6px)
• Border on focus
• Placeholder subtle

Progress bars:
• Rounded, smooth animation
• Color based on health (red→yellow→green)
```

---

## 🗓️ DEVELOPMENT TIMELINE (14-16 Weeks)

### **Phase 1: Foundation (Week 1-6)**

**Week 1:** ✅ DONE
- Project init (CLI + SDK)

**Week 2-3: Import System**
- YOLO parser
- Roboflow parser
- Unlabeled images import
- Progress bars
- Tests

**Week 4: Validation**
- All 7 issue detectors
- Health scoring
- Terminal output (Rich)
- Export reports

**Week 5-6: Auto-Fix**
- Fix all issue types
- Backup system
- Beautiful output
- Rollback capability

---

### **Phase 2: Annotation (Week 7-10)**

**Week 7-8: Annotation UI Core**
- FastAPI server
- React setup
- Canvas (Konva.js)
- Rectangle tool
- Basic navigation

**Week 9: Annotation Features**
- Polygon tool
- Edit mode
- Keyboard shortcuts
- Class management

**Week 10: Annotation Polish**
- Undo/redo
- Smart features
- Validation while labeling
- Performance optimization

---

### **Phase 3: Training & UI Pages (Week 11-14)**

**Week 11-12: Training Pipeline**
- Ultralytics integration
- Auto-configuration
- Progress tracking
- Evaluation
- Export (ONNX, TorchScript)
- Inference

**Week 13: UI Pages**
- Dashboard
- Datasets page
- Training monitor
- Settings

**Week 14: Integration & Polish**
- Real-time WebSocket updates
- Cross-page navigation
- Error handling
- Performance optimization

---

### **Phase 4: Launch Prep (Week 15-16)**

**Week 15: Content Creation**
- Documentation (complete)
- Demo video (90 seconds)
- README polish
- Examples (3-5 workflows)
- HN post drafting

**Week 16: Launch**
- Final testing
- Bug fixes
- Performance optimization
- Launch Tuesday 9am PT

---

## 🎯 SUCCESS METRICS

### **Launch Week (Week 16)**

**Minimum Success:**
```
✅ 800+ GitHub stars
✅ 200+ installations
✅ 50+ GitHub issues/discussions
✅ HN front page (>300 upvotes)
✅ 10+ positive tweets
```

**Target Success:**
```
✅ 1,500+ GitHub stars
✅ 400+ installations
✅ 100+ GitHub issues/discussions
✅ HN top 3 (>500 upvotes)
✅ 30+ positive tweets
✅ 2-3 blog posts from users
```

**Exceptional Success:**
```
✅ 2,500+ GitHub stars
✅ 800+ installations
✅ 200+ GitHub issues/discussions
✅ HN #1 (>800 upvotes)
✅ 50+ positive tweets
✅ 5+ blog posts from users
✅ TechCrunch/media mention
```

### **Month 3 Post-Launch**

**Target:**
```
✅ 3,000-5,000 stars
✅ 1,000+ weekly active users
✅ 30+ contributors
✅ 10+ companies publicly using it
✅ First "ModelCub vs Roboflow" comparison
```

### **Year 1**

**Target:**
```
✅ 8,000-15,000 stars
✅ 3,000+ weekly active users
✅ 100+ contributors
✅ 50+ companies using it
✅ Conference talks accepted
✅ Revenue opportunities clear
```

---

## 💰 MONETIZATION (Year 2+)

### **Open Core Model**

**Free Forever (Local):**
```
✅ Complete platform
✅ All features
✅ Unlimited projects
✅ Unlimited datasets
✅ Unlimited training
✅ No artificial limits
✅ Apache 2.0 license
```

**Pro Tier ($49/user/month):**
```
✅ Cloud-hosted UI (convenience)
✅ Team collaboration
✅ 50 GPU hours/month (cloud training)
✅ 100GB cloud storage
✅ Advanced AI features:
   • GPT-4V auto-labeling
   • Smart quality suggestions
   • Active learning
✅ Priority support
```

**Team Tier ($199/month):**
```
Everything in Pro, plus:
✅ Unlimited users
✅ 200 GPU hours/month
✅ 1TB storage
✅ SSO/SAML
✅ Audit logs
✅ SLA (99.9%)
```

**Enterprise (Custom):**
```
Everything in Team, plus:
✅ On-premise deployment
✅ Air-gapped option
✅ Custom integrations
✅ Dedicated support
✅ Custom SLA
✅ Training/onboarding
```

---

## 🔥 WHAT MAKES US WIN

### **1. Complete Platform**
Not separate tools. One cohesive experience.

### **2. Beautiful Design**
Every detail polished. Delightful to use daily.

### **3. Local-First**
Your data, your infrastructure, your control.

### **4. Free Forever**
Core platform never has limits.

### **5. Open Source**
Community-driven, transparent, trustworthy.

### **6. Modern Stack**
Fast, responsive, built with latest tech.

### **7. Developer Love**
CLI + SDK + UI. All first-class.

---

## 💪 STAYING MOTIVATED

**When Week 8 feels hard:**
> Remember: You're building the tool that SHOULD exist. The tool you wished you had. Thousands of people will use this daily.

**When Week 12 feels endless:**
> Remember: You're 85% done. The finish line is visible. Every day gets you closer to launch.

**When Week 15 feels scary:**
> Remember: You've built something real. Something useful. People will love it. Launch with confidence.

**When post-launch is slower than hoped:**
> Remember: GitHub took years to hit 10k stars. Supabase took 18 months. You're playing the long game. Consistency wins.

---

## 🎯 THE COMMITMENT

**You're committing to:**
- 14-16 weeks to launch
- 30-40 hours/week
- Building something beautiful
- Making it excellent, not just functional
- Helping users succeed
- Playing the long game

**You're building:**
- The cleanest CV platform
- The most powerful local-first tool
- The Roboflow alternative that should exist
- Infrastructure that lasts years

---

## 🚀 START TOMORROW

**Week 2 begins Monday.**

**Your first task: Import system.**

**By Friday: YOLO import works perfectly.**

**Then: Keep building. One week at a time.**

**In 14-16 weeks: You launch the best local-first CV platform in the world.**

---

**Let's build ModelCub. 🐻**

---

*This document is your north star. Refer to it when you're lost. Update it when plans change. But always remember the vision: The cleanest, most powerful local-first computer vision platform.*

*Now go build it.* 💪