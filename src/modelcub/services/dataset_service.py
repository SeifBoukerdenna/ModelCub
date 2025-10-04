from __future__ import annotations
import json, random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

from ..core.paths import project_root, CACHE_DIR
from ..core.io import (
    download_with_progress, extract_archive, sha256_file,
    copy_tree, delete_tree
)
from ..core.yaml_cfg import ensure_yaml_defaults, replace_yaml_classes
from ..core.discover import find_split_dirs, infer_classes_from_subdirs
from ..core.generate import gen_shapes_dataset
from ..core.registry import AVAILABLE_SOURCES
from ..events import DatasetAdded, DatasetEdited, DatasetDeleted, bus

# ---------- DTOs ----------
@dataclass
class AddDatasetRequest:
    name: str
    source: str
    classes_override: Optional[str] = None
    n: int = 200
    train_frac: float = 0.8
    imgsz: int = 640
    seed: int = 123
    force: bool = False

@dataclass
class EditDatasetRequest:
    name: str
    classes: str

@dataclass
class DeleteDatasetRequest:
    name: str
    yes: bool = False
    purge_cache: bool = False

# ---------- Helpers ----------
def _dataset_dir(name: str) -> Path:
    return project_root() / "data" / name

def _read_manifest(root: Path) -> Optional[dict]:
    f = root / "manifest.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return None

def _write_manifest(root: Path, name: str, classes: List[str] | None, extra: dict | None = None) -> None:
    manifest = {"dataset": name, "classes": classes or []}
    if extra:
        manifest.update(extra)
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

# ---------- Service ----------
def list_datasets() -> tuple[int, str]:
    data_dir = project_root() / "data"
    if not data_dir.exists():
        return 0, "No data/ directory. Run: modelcub project init"
    rows = []
    for sub in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        mani = _read_manifest(sub)
        if mani:
            rows.append((sub.name, ", ".join(mani.get("classes", []) or [])))
    if not rows:
        return 0, "No datasets found under data/."
    out = ["Datasets:"]
    out += [f"  - {name:16s} classes=[{cls}]" for name, cls in rows]
    return 0, "\n".join(out)

def info_dataset(name: str) -> tuple[int, str]:
    ds_dir = _dataset_dir(name)
    mani = _read_manifest(ds_dir)
    if not mani:
        return 2, f"No manifest found for dataset '{name}' at {ds_dir}."
    train_dir = ds_dir / "train"
    valid_dir = ds_dir / "valid"
    n_train = sum(1 for _ in train_dir.glob("*.*")) if train_dir.exists() else 0
    n_valid = sum(1 for _ in valid_dir.glob("*.*")) if valid_dir.exists() else 0
    payload = {
        "name": name,
        "path": str(ds_dir),
        "classes": mani.get("classes", []),
        "train_images": n_train,
        "valid_images": n_valid,
        "source_url": mani.get("source_url"),
        "auto_split": mani.get("auto_split"),
        "train_frac": mani.get("train_frac"),
        "generator": mani.get("generator"),
    }
    return 0, json.dumps(payload, indent=2)

def delete_dataset(req: DeleteDatasetRequest) -> tuple[int, str]:
    ds_dir = _dataset_dir(req.name)
    if not ds_dir.exists():
        return 0, f"Nothing to delete: {ds_dir} does not exist."
    if not req.yes:
        return 2, "Refusing to delete without confirmation (--yes)."
    delete_tree(ds_dir)
    msg = f"Deleted dataset '{req.name}' directory: {ds_dir}"

    if req.purge_cache:
        for key, spec in AVAILABLE_SOURCES.items():
            url = spec.get("url")
            if not url:
                continue
            cached = CACHE_DIR / f"{key}_{Path(url).name}"
            if cached.exists():
                try:
                    cached.unlink()
                    msg += f" | Purged cache: {cached}"
                except Exception:
                    pass

    bus.publish(DatasetDeleted(name=req.name, path=str(ds_dir)))
    return 0, msg

def edit_dataset(req: EditDatasetRequest) -> tuple[int, str]:
    ds_dir = _dataset_dir(req.name)
    mani = _read_manifest(ds_dir)
    if not mani:
        return 2, f"No manifest.json found for dataset '{req.name}' in {ds_dir}"
    classes = [c.strip() for c in req.classes.split(",") if c.strip()]
    if not classes:
        return 2, "No classes provided."
    mani["classes"] = classes
    (ds_dir / "manifest.json").write_text(json.dumps(mani, indent=2), encoding="utf-8")
    replace_yaml_classes(classes)
    bus.publish(DatasetEdited(name=req.name, classes=classes))
    return 0, f"Updated classes for dataset '{req.name}': {classes}"

def add_dataset(req: AddDatasetRequest) -> tuple[int, str]:
    out_dir = _dataset_dir(req.name)
    out_train, out_valid = out_dir / "train", out_dir / "valid"
    if out_dir.exists() and any(out_dir.iterdir()) and not req.force:
        return 2, f"Refusing to overwrite non-empty dir: {out_dir}. Use --force."
    out_train.mkdir(parents=True, exist_ok=True); out_valid.mkdir(parents=True, exist_ok=True)

    if req.source not in AVAILABLE_SOURCES:
        return 2, f"Unknown source '{req.source}'. Available: {', '.join(AVAILABLE_SOURCES.keys())}"
    spec = AVAILABLE_SOURCES[req.source]

    override_classes: list[str] | None = None
    if req.classes_override:
        override_classes = [c.strip() for c in req.classes_override.split(",") if c.strip()] or None

    # Generator path
    if spec.get("generator") == "shapes":
        classes = override_classes or spec["classes"]
        gen_shapes_dataset(out_train, out_valid,
                           n_total=max(1, int(req.n)),
                           train_frac=float(req.train_frac),
                           imgsz=max(64, int(req.imgsz)),
                           classes=classes, seed=int(req.seed))
        ensure_yaml_defaults(classes)
        _write_manifest(out_dir, req.name, classes, {"generator": "shapes"})
        bus.publish(DatasetAdded(name=req.name, path=str(out_dir), classes=classes))
        payload = {"name": req.name, "out": str(out_dir), "classes": classes}
        return 0, json.dumps(payload, indent=2)

    # Downloaded source
    url = spec.get("url")
    if not url:
        return 2, "Source entry missing 'url'."

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_name = f"{req.source}_{Path(url).name}"
    cached = CACHE_DIR / cache_name
    if not cached.exists():
        download_with_progress(url, cached)
    else:
        # keep UX similar to before
        pass

    if spec.get("sha256"):
        if sha256_file(cached).lower() != spec["sha256"].lower():
            return 2, f"Checksum mismatch for {cached.name}. Re-download and verify manually."

    # Extract to temp
    tmp_extract = out_dir.parent / f".{req.name}_extract_tmp"
    if tmp_extract.exists():
        delete_tree(tmp_extract)
    extract_archive(cached, tmp_extract)

    # Try explicit split dirs, else auto-split
    train_dir, valid_dir = find_split_dirs(tmp_extract)
    classes: Optional[List[str]] = None

    if train_dir and valid_dir:
        copy_tree(train_dir, out_train)
        copy_tree(valid_dir, out_valid)
        inferred = infer_classes_from_subdirs(train_dir)
        classes = inferred or spec.get("classes") or ["object"]
    else:
        exts = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
        all_imgs = [p for p in tmp_extract.rglob("*") if p.is_file() and p.suffix.lower() in exts]
        if not all_imgs:
            delete_tree(tmp_extract)
            return 2, "No images found after extraction."
        random.seed(int(req.seed))
        all_imgs.sort(); random.shuffle(all_imgs)
        n_total = len(all_imgs); n_train = int(n_total * float(req.train_frac))
        for src in all_imgs[:n_train]:
            (out_train / src.name).write_bytes(src.read_bytes())
        for src in all_imgs[n_train:]:
            (out_valid / src.name).write_bytes(src.read_bytes())
        classes = spec.get("classes") or ["object"]

    if override_classes:
        classes = override_classes

    ensure_yaml_defaults(classes or ["object"])
    _write_manifest(out_dir, req.name, classes, {
        "source_url": url,
        "auto_split": not (train_dir and valid_dir),
        "train_frac": float(req.train_frac),
    })
    delete_tree(tmp_extract)

    bus.publish(DatasetAdded(name=req.name, path=str(out_dir), classes=classes or []))
    payload = {"name": req.name, "out": str(out_dir), "classes": classes or ["object"]}
    return 0, json.dumps(payload, indent=2)
