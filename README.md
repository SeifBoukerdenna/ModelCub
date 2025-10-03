# 🐻 ModelCub Demo
From cub to beast — train and deploy AI models in **minutes**, fully local.
This demo walks through the **end-to-end workflow** of ModelCub: creating a project, labeling, training, inference, exporting, and annotating.

---

## 1. Install
ModelCub is lightweight and modular. Core works with zero dependencies.
Add extras for training and inference:

```bash
pip install "modelcub[ultra,onnx,opencv]"
```

---

## 2. Init a Project
Create a new project with ready-to-use structure:

```bash
modelcub init my-cub
cd my-cub
```

This generates:

```
my-cub/
├── data/
│   ├── raw/        # your images go here
│   └── labels/     # annotations (auto/manual)
├── models/         # trained weights
├── runs/           # training logs
├── notebooks/      # experiments
├── scripts/        # utils
├── modelcub.yaml   # project config
└── README.md
```

---

## 3. Get a Sample Dataset
Try ModelCub instantly with built-in datasets:

```bash
# Options: cats-dogs, hotdog, pokemon
modelcub dataset cats-dogs
```

---

## 4. Auto-Label Your Images
Jumpstart annotation with pretrained YOLO models:

```bash
modelcub autolabel data/raw --out data/labels
```

✨ This uses YOLO under the hood (if installed) to generate bounding boxes automatically.
You can correct them later in `annotate`.

---

## 5. Train Your Model
Train on your dataset, CPU or GPU automatically detected:

```bash
modelcub train --data modelcub.yaml --epochs 5
```

Outputs go to `models/` and `runs/`.

---

## 6. Run Inference
Test your trained model on images or folders:

```bash
modelcub infer --source data/raw --weights models/last.pt
```

For a live webcam demo:

```bash
modelcub demo --webcam
```

---

## 7. Annotate Manually (Optional)
Launch a local labeling frontend (Label Studio) connected to your project:

```bash
modelcub annotate --port 9000
```

Open [http://localhost:9000](http://localhost:9000) and refine your annotations.
ModelCub can also run a **prelabel backend** so predictions appear as suggestions.

---

## 8. Export Your Labels
Easily export annotations into standard formats for interoperability:

```bash
# Export to COCO JSON
modelcub export --format coco --out exports/labels_coco.json

# Export to YOLO format
modelcub export --format yolo --out exports/yolo/
```

---

## 🎉 Congrats!
You just went from raw images → labels → trained model → inference → export in one simple workflow.

This is the vision of **ModelCub**:
- 🍼 **Easy** for beginners
- 🐻 **Powerful** for researchers
- 🔒 **Private** for professionals
