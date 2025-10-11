---
layout: home

hero:
  name: ModelCub
  text: Computer Vision, Simplified
  tagline: Train and deploy CV models locally. Version datasets like code. Zero cloud costs.
  image:
    src: /logo.svg
    alt: ModelCub
  actions:
    - theme: brand
      text: Get Started
      link: /guide/installation
    - theme: alt
      text: GitHub
      link: https://github.com/SeifBoukerdenna/ModelCub

features:
  - title: 🩹 Auto-Fix Datasets
    details: Detect and repair corrupt images, invalid labels, and duplicates in one command.

  - title: 🔄 Version Control
    details: Git-like workflows for datasets. Commit, diff, and rollback with visual comparisons.

  - title: 🚀 Smart Training
    details: Auto-optimize settings based on your GPU. Multi-GPU support. Early stopping included.

  - title: 💰 Zero Cloud Costs
    details: Run 100% locally. No subscriptions, no surprises. Your machine, your rules.

  - title: 🔒 Privacy-First
    details: Your data never leaves your machine. Perfect for medical, pharma, and sensitive applications.

  - title: 🛠️ Simple API
    details: Clean Python SDK and powerful CLI. Works with your existing tools.
---

<div class="vp-doc" style="max-width: 900px; margin: 0 auto; padding: 48px 24px;">

## The Workflow

```bash
pip install modelcub
modelcub init my-project
modelcub dataset add --path ./data --name v1
modelcub dataset fix v1 --auto
modelcub train --dataset v1 --auto
```

## Why ModelCub?

**Stop wasting time on dataset debugging.** Automatically detect and fix corrupt images, invalid labels, duplicates, and format issues.

**Stop paying Roboflow $8k/month.** Run everything locally with zero cloud costs.

**Stop losing track of datasets.** Version control with git-like semantics. Visual diffs show exactly what changed.

## Python SDK

```python
from modelcub import Project, Dataset, Model

# Initialize
project = Project.init("my-project")
dataset = Dataset.from_path("./data", name="v1")

# Fix issues
dataset.fix(auto=True)

# Train
model = Model("yolov11n", task="detect")
run = model.train(dataset=dataset, auto=True)

# Results
print(f"mAP50: {run.evaluate().map50:.3f}")
```

## Comparison

|  | ModelCub | Roboflow | Ultralytics |
|---|:--------:|:--------:|:-----------:|
| **Cost** | Free | $8k+/mo | Free |
| **Runs Locally** | ✅ | ❌ | ✅ |
| **Auto-Fix** | ✅ | ❌ | ❌ |
| **Version Control** | ✅ | Limited | ❌ |
| **Visual Diff** | ✅ | ❌ | ❌ |

## Use Cases

- **Medical Imaging**: HIPAA-compliant, on-premise training
- **Startups**: Save $96k/year in cloud costs
- **Research**: Reproducible experiments with versioned datasets
- **Privacy-Sensitive**: Air-gapped environments supported

## Get Started

```bash
pip install modelcub
```

Read the **[Installation Guide](/guide/installation)** or check out the **[Quick Start](/guide/quick-start)**.

---

<p style="text-align: center; color: #666; margin-top: 48px;">
MIT License • <a href="https://github.com/SeifBoukerdenna/ModelCub">GitHub</a> • <a href="/guide/introduction">Documentation</a>
</p>

</div>

<style>
.vp-doc h2 {
  margin-top: 48px;
  border-top: 1px solid var(--vp-c-divider);
  padding-top: 24px;
}

.vp-doc h2:first-child {
  margin-top: 0;
  border-top: none;
  padding-top: 0;
}
</style>