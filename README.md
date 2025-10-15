# ModelCub

<div align="center">

**The complete computer vision platform. Beautiful, powerful, local-first, free.**

[![PyPI version](https://badge.fury.io/py/modelcub.svg)](https://badge.fury.io/py/modelcub)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Quick Start](#-quick-start) • [Features](#-features) • [Roadmap](#-roadmap) • [Documentation](#-documentation) • [Discord](#-community)

</div>

---

## 🎯 Why ModelCub?

**You're tired of:**
- Roboflow charging $8,000+/year as you scale
- Sending your medical/pharma data to someone else's servers
- Juggling Label Studio + DVC + Ultralytics + custom scripts
- Datasets breaking between experiments
- Annotation tools that feel like they're from 2010

**You want:**
- ✅ Complete platform (label → train → deploy)
- ✅ Beautiful, modern interface
- ✅ 100% local, zero cloud dependencies
- ✅ Free forever, no limits
- ✅ Git-like version control for datasets
- ✅ Auto-fix broken datasets with one command

> ModelCub is what we wish we had when building computer vision systems for medical imaging. No cloud lock-in, no pricing tiers, just a powerful tool that works offline and respects your privacy.

## ✨ Features

### Dataset Operations
- **Smart Import**: YOLO, Roboflow exports, COCO, or unlabeled images
- **Health Scoring**: Automatic dataset validation with actionable insights
- **Auto-Fix**: One command to repair corrupt images, fix bounds, remove duplicates
- **Version Control**: Git-like commits and visual diffs for datasets
- **CLI + SDK**: Powerful terminal commands and clean Python API

### Annotation (Coming Soon)
- **Modern Canvas**: Smooth drawing with Konva.js, keyboard shortcuts
- **Real-time Validation**: Catch issues as you label
- **Review Mode**: Flag suspicious annotations, batch operations
- **Zero Latency**: Local processing, 60fps canvas rendering

### Training Pipeline (Coming Soon)
- **Auto-Optimization**: Smart defaults based on your GPU and dataset
- **Live Monitoring**: WebSocket updates, no page refresh needed
- **Multi-Format Export**: ONNX, TensorRT, TorchScript, CoreML
- **Reproducible**: Full experiment tracking and config versioning

### Built Different
- **API-First**: CLI → SDK → Core API. Everything is composable
- **Stateless UI**: Kill server, restart, nothing lost. All state in filesystem
- **No Lock-In**: YOLO format internally, export anywhere
- **Privacy-First**: Zero telemetry, 100% offline capable

## 🚀 Quick Start

```bash
# Install (2 minutes)
pip install modelcub

# Create project
modelcub project init my-cv-project
cd my-cv-project

# Add dataset (supports YOLO, Roboflow, COCO)
modelcub dataset add --source ./data --name bears-v1

# Validate and auto-fix
modelcub dataset validate bears-v1
modelcub dataset fix bears-v1 --auto

# Launch UI
modelcub ui
```

**That's it.** Your dataset is imported, validated, and ready.

### Python SDK

```python
from modelcub import Project, Dataset

# Initialize
project = Project.init("my-cv-project")

# Load dataset
dataset = Dataset.load("bears-v1")

# Validate
report = dataset.validate()
print(f"Health Score: {report.health_score}/100")

# Auto-fix issues
fix_report = dataset.fix(auto=True)
print(f"Fixed {fix_report.total_fixed} issues")

# Get statistics
stats = dataset.stats()
print(f"Classes: {stats.class_distribution}")
```

## 🎨 What Makes ModelCub Special?

### 1. Auto-Fix That Actually Works
Most tools tell you what's broken. ModelCub fixes it.

```bash
$ modelcub dataset fix bears-v1 --auto

🔧 Auto-fixing bears-v1...

✅ Fixed 23 issues:
   • Removed 2 corrupt images
   • Clipped 8 out-of-bounds boxes
   • Removed 4 duplicates
   • Fixed 9 invalid labels

Health Score: 67/100 → 94/100

Backup saved: .modelcub/backups/bears-v1_20250115_143022
```

### 2. Dataset Version Control
Git for datasets with visual diffs.

```bash
$ modelcub dataset commit -m "Added 200 outdoor images"
$ modelcub dataset diff v1 v2 --visual

📊 Dataset Diff: bears-v1 (v1 → v2)
   Images:  847 → 1,047 (+200)
   Labels:  2,847 → 3,412 (+565)

   Class distribution changed:
   • grizzly: 45% → 38%
   • polar: 35% → 40%
   • black: 20% → 22%
```

### 3. Beautiful, Fast UI
Modern interface that doesn't feel like enterprise software from 2010.

- Dark mode by default (light mode available)
- 60fps canvas rendering
- Keyboard-first navigation
- Zero latency on local files

### 4. Privacy-First Architecture
Your data never leaves your machine.

- ✅ Works 100% offline
- ✅ No telemetry, no tracking
- ✅ No account required
- ✅ HIPAA/GDPR friendly
- ✅ Perfect for medical/pharma/defense

## 📊 Comparison

|  | ModelCub | Roboflow | Label Studio + Ultralytics |
|---|:---:|:---:|:---:|
| **Annotation** | ✅ | ✅ | ✅ |
| **Training** | ✅ | ✅ | ✅ |
| **Local-first** | ✅ | ❌ | ✅ |
| **Auto-fix** | ✅ | ❌ | ❌ |
| **Version control** | ✅ | Basic | Manual |
| **Visual diff** | ✅ | ❌ | ❌ |
| **Integrated** | ✅ | ✅ | ❌ |
| **Pricing** | **Free** | **$500-8k/mo** | **Free** |
| **Setup time** | **2 min** | **5 min** | **30+ min** |

## 🗺️ Roadmap

### ✅ Phase 1: Foundation (Complete)
- [x] Project management
- [x] Dataset import (YOLO, Roboflow, COCO)
- [x] CLI with all core commands
- [x] Python SDK
- [x] FastAPI backend
- [x] React frontend with routing

### 🚧 Phase 2: Dataset Operations (In Progress)
- [ ] Dataset validation with health scoring
- [ ] Auto-fix system with backups
- [ ] Version control and diff
- [ ] Visual diff UI
- [ ] Export to multiple formats

### 📅 Phase 3: Annotation (February 2025)
- [ ] Canvas-based annotation tool
- [ ] Rectangle and polygon drawing
- [ ] Keyboard shortcuts
- [ ] Auto-save and undo/redo
- [ ] Review mode

### 📅 Phase 4: Training (March 2025)
- [ ] YOLO training integration
- [ ] Auto-configuration
- [ ] Real-time progress (WebSocket)
- [ ] Model evaluation
- [ ] Multi-format export

### 🔮 Future
- [ ] Active learning
- [ ] Multi-annotator consensus
- [ ] Custom augmentation plugins
- [ ] Team collaboration features
- [ ] Cloud sync (optional)

## 🎓 Who Is This For?

### Indie Developers & Startups
Building CV products without the Roboflow tax. Use the savings to hire engineers.

### Medical/Pharma/Defense
HIPAA-compliant, air-gapped training. Your data stays on your servers.

### Research Labs
Reproducible experiments with full audit trails. Perfect for papers.

### Anyone Fed Up With Cloud Platforms
Own your data. Own your tools. Pay nothing.

## 💻 Architecture

```
CLI → Python SDK → Core API ← FastAPI ← React UI
                     ↓
            File System State
         (.modelcub/ directory)
```

**Key Principles:**
- **API-First**: Everything is composable
- **Stateless**: No hidden database, all state in files
- **Format-Agnostic**: YOLO internally, import/export anything
- **Git-Friendly**: Human-readable text files

## 📚 Documentation

- [Installation Guide](docs/guide/installation.md)
- [Quick Start Tutorial](docs/guide/quick-start.md)
- [CLI Reference](docs/cli/reference.md)
- [Python SDK API](docs/api/overview.md)
- [Architecture Overview](docs/architecture.md)

## 🤝 Contributing

We welcome contributions! ModelCub is built in the open.

**Areas we need help:**
- [ ] Web UI/UX improvements
- [ ] Testing and bug reports
- [ ] Documentation and tutorials
- [ ] Format converters (more import/export formats)
- [ ] Example workflows

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 🌟 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=SeifBoukerdenna/ModelCub&type=Date)](https://star-history.com/#SeifBoukerdenna/ModelCub&Date)

## 💬 Community

- **Discord**: [Join our server](https://discord.gg/modelcub) (coming soon)
- **GitHub Discussions**: [Ask questions, share projects](https://github.com/SeifBoukerdenna/ModelCub/discussions)
- **Twitter**: [@ModelCub](https://twitter.com/modelcub) (coming soon)

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

Built with ❤️ by developers who got tired of expensive cloud platforms.

---

<div align="center">

**If ModelCub saves you from Roboflow's pricing, star the repo!** ⭐

[⬆ Back to top](#modelcub)

</div>
