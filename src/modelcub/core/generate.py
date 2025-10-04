from __future__ import annotations

import math
import random
from pathlib import Path
from typing import List, Tuple, Optional


# ---- Lightweight backends -----------------------------------------------------

def _cv2():
    try:
        import cv2  # type: ignore
        return cv2
    except Exception:
        return None


def _pil():
    try:
        from PIL import Image, ImageDraw  # type: ignore
        return Image, ImageDraw
    except Exception:
        return None, None


# ---- Geometry -----------------------------------------------------------------

def _triangle_points(cx: int, cy: int, r: int) -> List[Tuple[int, int]]:
    """
    Equilateral triangle centered at (cx, cy) with "radius" r.
    Implemented with math only (no NumPy) so PIL path has zero heavy deps.
    Angles chosen to give a nice upright-ish triangle.
    """
    angles_deg = (90, 210, 330)
    pts: List[Tuple[int, int]] = []
    for a in angles_deg:
        rad = math.radians(a)
        x = cx + int(round(r * math.cos(rad)))
        y = cy + int(round(r * math.sin(rad)))
        pts.append((x, y))
    return pts


def _canvas_params(imgsz: int) -> Tuple[int, int, int, int]:
    """
    Return (W, H, margin, max_size) for the given imgsz, with safe guards so
    tiny canvases (e.g., 32, 64) do not produce invalid randranges.
    """
    W = H = max(8, int(imgsz))  # hard floor
    # margin is proportional but capped; always at least 4px.
    margin = max(4, min(80, W // 8, H // 8))
    # keep shapes comfortably inside the canvas
    max_size = max(3, min((W - 2 * margin), (H - 2 * margin)) // 2)
    return W, H, margin, max_size


# ---- Single image drawing -----------------------------------------------------

def _draw_one_cv2(out_path: Path, imgsz: int, classes: List[str]) -> None:
    cv2 = _cv2()
    if cv2 is None:
        raise RuntimeError("OpenCV backend requested but not available.")

    # cv2 path needs numpy; import lazily so PIL-only environments still import the module
    try:
        import numpy as np  # type: ignore
    except Exception as e:
        raise RuntimeError("OpenCV path requires NumPy; please install numpy.") from e

    W, H, margin, max_size = _canvas_params(imgsz)
    img = np.full((H, W, 3), 255, dtype=np.uint8)

    num_objs = random.randint(1, 5)
    for _ in range(num_objs):
        cls = random.choice(classes)
        color = (random.randint(64, 200), random.randint(64, 200), random.randint(64, 200))
        cx = random.randint(margin, max(margin, W - margin))
        cy = random.randint(margin, max(margin, H - margin))
        size = random.randint(3, max_size)

        if cls == "circle":
            cv2.circle(img, (cx, cy), size, color, -1)
        elif cls == "square":
            cv2.rectangle(img, (cx - size, cy - size), (cx + size, cy + size), color, -1)
        else:
            pts = _triangle_points(cx, cy, size)
            cv2.fillPoly(img, [np.array(pts, dtype=np.int32)], color)

    # Write JPEG with quality ~92
    cv2.imwrite(str(out_path), img, [int(cv2.IMWRITE_JPEG_QUALITY), 92])


def _draw_one_pil(out_path: Path, imgsz: int, classes: List[str]) -> None:
    PIL_Image, PIL_Draw = _pil()
    if not (PIL_Image and PIL_Draw):
        raise RuntimeError("Pillow backend requested but not available.")

    W, H, margin, max_size = _canvas_params(imgsz)
    img = PIL_Image.new("RGB", (W, H), (255, 255, 255))
    drw = PIL_Draw.Draw(img)

    num_objs = random.randint(1, 5)
    for _ in range(num_objs):
        cls = random.choice(classes)
        color = (random.randint(64, 200), random.randint(64, 200), random.randint(64, 200))
        cx = random.randint(margin, max(margin, W - margin))
        cy = random.randint(margin, max(margin, H - margin))
        size = random.randint(3, max_size)

        if cls == "circle":
            drw.ellipse([cx - size, cy - size, cx + size, cy + size], fill=color)
        elif cls == "square":
            drw.rectangle([cx - size, cy - size, cx + size, cy + size], fill=color)
        else:
            pts = _triangle_points(cx, cy, size)
            drw.polygon(pts, fill=color)

    img.save(out_path, "JPEG", quality=92)


# ---- Public API ----------------------------------------------------------------

def gen_shapes_dataset(
    train_dir: Path,
    valid_dir: Path,
    n_total: int,
    train_frac: float,
    imgsz: int,
    classes: List[str],
    seed: int,
) -> None:
    """
    Generate a small synthetic classification dataset with colored shapes.
    - Uses OpenCV if available; otherwise falls back to Pillow.
    - Deterministic per `seed`.
    - Robust to tiny `imgsz` values (no invalid random ranges).
    """
    if n_total <= 0:
        return

    random.seed(seed)
    n_train = int(n_total * train_frac)
    n_valid = max(0, n_total - n_train)

    # Pick backend: prefer OpenCV (fast), otherwise PIL.
    backend = "cv2" if _cv2() is not None else ("pil" if _pil()[0] is not None else None)
    if backend is None:
        raise RuntimeError("Neither OpenCV (opencv-python) nor Pillow is available to generate images.")

    train_dir.mkdir(parents=True, exist_ok=True)
    valid_dir.mkdir(parents=True, exist_ok=True)

    for i in range(n_train):
        out = train_dir / f"img_{i:05d}.jpg"
        if backend == "cv2":
            _draw_one_cv2(out, imgsz, classes)
        else:
            _draw_one_pil(out, imgsz, classes)

    for i in range(n_valid):
        out = valid_dir / f"img_{i:05d}.jpg"
        if backend == "cv2":
            _draw_one_cv2(out, imgsz, classes)
        else:
            _draw_one_pil(out, imgsz, classes)
