from __future__ import annotations
from pathlib import Path
from typing import Optional, Tuple, List

def find_split_dirs(root: Path) -> Tuple[Optional[Path], Optional[Path]]:
    train_dir = valid_dir = None
    for p in root.rglob("*"):
        if p.is_dir() and p.name.lower() in ("train", "training"):
            train_dir = train_dir or p
        if p.is_dir() and p.name.lower() in ("valid", "val", "validation"):
            valid_dir = valid_dir or p
    return train_dir, valid_dir

def infer_classes_from_subdirs(split_dir: Path) -> List[str]:
    classes: List[str] = []
    for child in sorted(split_dir.iterdir()):
        if child.is_dir():
            classes.append(child.name)
    return classes
