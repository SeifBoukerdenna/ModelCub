"""
Dataset snapshot management for training reproducibility.

Creates lite snapshots (file list + class map) without hashing
to track dataset state at training time.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def create_snapshot(
    dataset_path: Path,
    dataset_name: str,
    snapshot_id: str
) -> Dict[str, Any]:
    """
    Create lite dataset snapshot with file list and class map.

    Args:
        dataset_path: Path to dataset directory
        dataset_name: Name of the dataset
        snapshot_id: Unique snapshot identifier

    Returns:
        Snapshot dictionary with metadata and file manifest
    """
    snapshot = {
        'id': snapshot_id,
        'dataset_name': dataset_name,
        'created': datetime.utcnow().isoformat() + 'Z',
        'files': _collect_files(dataset_path),
        'classes': _load_classes(dataset_path),
        'stats': _compute_stats(dataset_path)
    }

    return snapshot


def _collect_files(dataset_path: Path) -> Dict[str, List[str]]:
    """
    Collect list of files in each split.

    Args:
        dataset_path: Path to dataset directory

    Returns:
        Dictionary mapping split name to list of relative file paths
    """
    files = {}

    # Collect files from standard splits
    for split in ['train', 'valid', 'test', 'unlabeled']:
        split_path = dataset_path / split
        if split_path.exists():
            # Collect image files
            image_paths = []
            for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                image_paths.extend(split_path.rglob(f'*{ext}'))
                image_paths.extend(split_path.rglob(f'*{ext.upper()}'))

            # Store relative paths
            files[split] = sorted([
                str(p.relative_to(dataset_path))
                for p in image_paths
            ])

    return files


def _load_classes(dataset_path: Path) -> Dict[int, str]:
    """
    Load class mapping from dataset.yaml.

    Args:
        dataset_path: Path to dataset directory

    Returns:
        Dictionary mapping class ID to class name
    """
    dataset_yaml = dataset_path / 'dataset.yaml'
    if not dataset_yaml.exists():
        return {}

    try:
        import yaml
        with open(dataset_yaml, 'r') as f:
            data = yaml.safe_load(f)

        # Extract classes (can be list or dict)
        classes = data.get('names', [])
        if isinstance(classes, list):
            return {i: name for i, name in enumerate(classes)}
        elif isinstance(classes, dict):
            return classes
        else:
            return {}

    except Exception:
        return {}


def _compute_stats(dataset_path: Path) -> Dict[str, Any]:
    """
    Compute basic dataset statistics.

    Args:
        dataset_path: Path to dataset directory

    Returns:
        Dictionary with image counts per split
    """
    stats = {}

    for split in ['train', 'valid', 'test', 'unlabeled']:
        split_path = dataset_path / split / 'images'
        if split_path.exists():
            # Count image files
            count = 0
            for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                count += len(list(split_path.glob(f'*{ext}')))
                count += len(list(split_path.glob(f'*{ext.upper()}')))

            stats[f'{split}_images'] = count

    return stats


def save_snapshot(snapshot: Dict[str, Any], path: Path) -> None:
    """
    Save snapshot to JSON file.

    Args:
        snapshot: Snapshot dictionary
        path: Output path for snapshot file
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as f:
        json.dump(snapshot, f, indent=2)


def load_snapshot(path: Path) -> Dict[str, Any]:
    """
    Load snapshot from JSON file.

    Args:
        path: Path to snapshot file

    Returns:
        Snapshot dictionary

    Raises:
        FileNotFoundError: If snapshot doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(f"Snapshot not found: {path}")

    with open(path, 'r') as f:
        return json.load(f)


def generate_snapshot_id() -> str:
    """
    Generate unique snapshot ID with timestamp.

    Returns:
        Snapshot ID in format: snapshot-YYYYMMDD-HHMMSS
    """
    return datetime.utcnow().strftime('snapshot-%Y%m%d-%H%M%S')