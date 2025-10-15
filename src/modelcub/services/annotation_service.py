from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

from ..core.registries import DatasetRegistry
from ..events import AnnotationSaved, AnnotationDeleted, bus

# ---------- DTOs ----------
@dataclass
class BoundingBox:
    """YOLO format: class_id x_center y_center width height (normalized 0-1)"""
    class_id: int
    x: float
    y: float
    w: float
    h: float

    def to_yolo_line(self) -> str:
        return f"{self.class_id} {self.x:.6f} {self.y:.6f} {self.w:.6f} {self.h:.6f}"

    @classmethod
    def from_yolo_line(cls, line: str) -> BoundingBox:
        parts = line.strip().split()
        return cls(
            class_id=int(parts[0]),
            x=float(parts[1]),
            y=float(parts[2]),
            w=float(parts[3]),
            h=float(parts[4])
        )

    def clamp_bounds(self) -> BoundingBox:
        """Clamp coordinates to valid range [0, 1]"""
        return BoundingBox(
            class_id=self.class_id,
            x=max(0.0, min(1.0, self.x)),
            y=max(0.0, min(1.0, self.y)),
            w=max(0.0, min(1.0, self.w)),
            h=max(0.0, min(1.0, self.h))
        )

@dataclass
class SaveAnnotationRequest:
    dataset_name: str
    image_id: str
    boxes: List[BoundingBox]
    project_path: Path

@dataclass
class DeleteAnnotationRequest:
    dataset_name: str
    image_id: str
    box_index: int
    project_path: Path

@dataclass
class GetAnnotationRequest:
    dataset_name: str
    image_id: Optional[str] = None
    project_path: Optional[Path] = None

# ---------- Helpers ----------
def _find_image_path(dataset_dir: Path, image_id: str) -> Optional[Path]:
    """Find image file in images/{split}/ structure"""
    images_dir = dataset_dir / "images"

    for split in ["train", "val", "test", "unlabeled"]:
        split_dir = images_dir / split
        if not split_dir.exists():
            continue

        for ext in [".jpg", ".jpeg", ".png", ".bmp"]:
            path = split_dir / f"{image_id}{ext}"
            if path.exists():
                return path

    return None

def _load_yolo_labels(label_path: Path) -> List[BoundingBox]:
    """Parse YOLO label file"""
    boxes = []
    if not label_path.exists():
        return boxes

    try:
        for line in label_path.read_text().strip().split('\n'):
            if line.strip():
                boxes.append(BoundingBox.from_yolo_line(line))
    except Exception as e:
        print(f"Warning: Failed to parse {label_path}: {e}")

    return boxes

def _validate_boxes(boxes: List[BoundingBox], max_class_id: int) -> tuple[List[BoundingBox], List[str]]:
    """Validate and clamp boxes, return valid boxes + warnings"""
    valid = []
    warnings = []

    for i, box in enumerate(boxes):
        if box.class_id < 0 or box.class_id > max_class_id:
            warnings.append(f"Box {i}: Invalid class_id {box.class_id}, skipping")
            continue

        clamped = box.clamp_bounds()
        if clamped.x != box.x or clamped.y != box.y or clamped.w != box.w or clamped.h != box.h:
            warnings.append(f"Box {i}: Clamped out-of-bounds coordinates")

        valid.append(clamped)

    return valid, warnings

# ---------- Service Functions ----------
def save_annotation(req: SaveAnnotationRequest) -> tuple[int, str]:
    """Save annotation for single image"""
    dataset_dir = req.project_path / "data" / "datasets" / req.dataset_name

    if not dataset_dir.exists():
        return 2, f"Dataset '{req.dataset_name}' not found"

    # Get classes from registry
    registry = DatasetRegistry(req.project_path)
    classes = registry.list_classes(req.dataset_name)

    # Find image
    img_path = _find_image_path(dataset_dir, req.image_id)
    if not img_path:
        return 2, f"Image '{req.image_id}' not found in dataset"

    # Validate boxes
    max_class_id = len(classes) - 1
    valid_boxes, warnings = _validate_boxes(req.boxes, max_class_id)

    # Label file: images/{split}/labels/{image}.txt
    labels_dir = img_path.parent.parent / "labels" / img_path.parent.name
    labels_dir.mkdir(parents=True, exist_ok=True)
    label_path = labels_dir / f"{img_path.stem}.txt"

    # Atomic write
    temp_path = label_path.with_suffix('.txt.tmp')

    try:
        with open(temp_path, 'w') as f:
            for box in valid_boxes:
                f.write(box.to_yolo_line() + '\n')

        temp_path.replace(label_path)

        bus.publish(AnnotationSaved(
            dataset_name=req.dataset_name,
            image_id=req.image_id,
            num_boxes=len(valid_boxes)
        ))

        result = {
            "image_id": req.image_id,
            "boxes_saved": len(valid_boxes),
            "boxes_skipped": len(req.boxes) - len(valid_boxes),
            "warnings": warnings
        }

        return 0, json.dumps(result, indent=2)

    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        return 2, f"Failed to save annotation: {e}"

def get_annotation(req: GetAnnotationRequest) -> tuple[int, str]:
    """Get annotation(s) for image(s)"""
    dataset_dir = req.project_path / "data" / "datasets" / req.dataset_name

    if not dataset_dir.exists():
        return 2, f"Dataset '{req.dataset_name}' not found"

    if req.image_id:
        # Single image
        img_path = _find_image_path(dataset_dir, req.image_id)
        if not img_path:
            return 2, f"Image '{req.image_id}' not found"

        # Label path: images/{split}/labels/{image}.txt
        labels_dir = img_path.parent.parent / "labels" / img_path.parent.name
        label_path = labels_dir / f"{img_path.stem}.txt"
        boxes = _load_yolo_labels(label_path)

        annotation = {
            "image_id": req.image_id,
            "image_path": str(img_path.relative_to(dataset_dir)),
            "boxes": [
                {"class_id": b.class_id, "x": b.x, "y": b.y, "w": b.w, "h": b.h}
                for b in boxes
            ],
            "status": "labeled" if boxes else "unlabeled"
        }
        return 0, json.dumps(annotation, indent=2)

    else:
        # All images
        annotations = []
        images_dir = dataset_dir / "images"

        for split in ["train", "val", "test", "unlabeled"]:
            split_dir = images_dir / split
            if not split_dir.exists():
                continue

            labels_dir = images_dir / "labels" / split

            for img_path in split_dir.glob("*.[jp][pn][g]*"):
                label_path = labels_dir / f"{img_path.stem}.txt"
                boxes = _load_yolo_labels(label_path)

                annotations.append({
                    "image_id": img_path.stem,
                    "image_path": str(img_path.relative_to(dataset_dir)),
                    "num_boxes": len(boxes),
                    "status": "labeled" if boxes else "unlabeled"
                })

        result = {
            "dataset": req.dataset_name,
            "total_images": len(annotations),
            "images": annotations
        }
        return 0, json.dumps(result, indent=2)

def delete_annotation(req: DeleteAnnotationRequest) -> tuple[int, str]:
    """Delete single box from annotation"""
    get_req = GetAnnotationRequest(
        dataset_name=req.dataset_name,
        image_id=req.image_id,
        project_path=req.project_path
    )
    code, result = get_annotation(get_req)
    if code != 0:
        return code, result

    annotation = json.loads(result)
    boxes = [
        BoundingBox(
            class_id=b["class_id"],
            x=b["x"],
            y=b["y"],
            w=b["w"],
            h=b["h"]
        )
        for b in annotation["boxes"]
    ]

    if req.box_index < 0 or req.box_index >= len(boxes):
        return 2, f"Invalid box_index {req.box_index}, must be 0-{len(boxes)-1}"

    boxes.pop(req.box_index)

    save_req = SaveAnnotationRequest(
        dataset_name=req.dataset_name,
        image_id=req.image_id,
        boxes=boxes,
        project_path=req.project_path
    )

    code, msg = save_annotation(save_req)
    if code == 0:
        bus.publish(AnnotationDeleted(
            dataset_name=req.dataset_name,
            image_id=req.image_id
        ))

    return code, msg

def get_annotation_stats(dataset_name: str, project_path: Path) -> tuple[int, str]:
    """Get annotation statistics for dataset"""
    dataset_dir = project_path / "data" / "datasets" / dataset_name

    if not dataset_dir.exists():
        return 2, f"Dataset '{dataset_name}' not found"

    # Get classes from registry
    registry = DatasetRegistry(project_path)
    classes = registry.list_classes(dataset_name)

    total_images = 0
    labeled = 0
    total_boxes = 0
    class_counts = {cls: 0 for cls in classes}

    images_dir = dataset_dir / "images"

    for split in ["train", "val", "test", "unlabeled"]:
        split_dir = images_dir / split
        if not split_dir.exists():
            continue

        labels_dir = images_dir / "labels" / split

        for img_path in split_dir.glob("*.[jp][pn][g]*"):
            total_images += 1
            label_path = labels_dir / f"{img_path.stem}.txt"
            boxes = _load_yolo_labels(label_path)

            if boxes:
                labeled += 1
                total_boxes += len(boxes)

                for box in boxes:
                    if 0 <= box.class_id < len(classes):
                        class_counts[classes[box.class_id]] += 1

    stats = {
        "dataset": dataset_name,
        "total_images": total_images,
        "labeled": labeled,
        "unlabeled": total_images - labeled,
        "progress": labeled / total_images if total_images > 0 else 0,
        "total_boxes": total_boxes,
        "avg_boxes_per_image": total_boxes / labeled if labeled > 0 else 0,
        "class_distribution": class_counts
    }

    return 0, json.dumps(stats, indent=2)