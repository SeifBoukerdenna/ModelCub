"""
Lockfile generation for reproducible training.

Captures the exact environment (packages, versions, config) used
for a training run to enable exact reproduction.
"""

import sys
import platform
import yaml
import subprocess
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def generate_lockfile(
    run_id: str,
    config: Dict[str, Any],
    dataset_name: str,
    dataset_snapshot_id: str
) -> Dict[str, Any]:
    """
    Generate training lockfile with environment snapshot.

    Args:
        run_id: Training run identifier
        config: Training configuration parameters
        dataset_name: Name of dataset used
        dataset_snapshot_id: Dataset snapshot identifier

    Returns:
        Lockfile dictionary with environment details
    """
    lockfile = {
        'run_id': run_id,
        'created': datetime.utcnow().isoformat() + 'Z',
        'config': config,
        'dataset': {
            'name': dataset_name,
            'snapshot_id': dataset_snapshot_id
        },
        'environment': _capture_environment()
    }

    return lockfile


def _capture_environment() -> Dict[str, Any]:
    """
    Capture current Python environment details.

    Returns:
        Dictionary with Python version, platform, and installed packages
    """
    env = {
        'python': {
            'version': sys.version,
            'executable': sys.executable,
            'platform': sys.platform
        },
        'system': {
            'platform': platform.platform(),
            'machine': platform.machine(),
            'processor': platform.processor()
        },
        'packages': _get_installed_packages()
    }

    return env


def _get_installed_packages() -> Dict[str, str]:
    """
    Get list of installed Python packages with versions.

    Returns:
        Dictionary mapping package name to version
    """
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format', 'json'],
            capture_output=True,
            text=True,
            check=True
        )

        import json
        packages = json.loads(result.stdout)

        return {pkg['name']: pkg['version'] for pkg in packages}

    except Exception as e:
        # Fallback: return empty dict if pip list fails
        return {}


def save_lockfile(lockfile: Dict[str, Any], path: Path) -> None:
    """
    Save lockfile to YAML file.

    Args:
        lockfile: Lockfile dictionary
        path: Output path for lockfile
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, 'w') as f:
        yaml.safe_dump(
            lockfile,
            f,
            default_flow_style=False,
            sort_keys=False
        )


def load_lockfile(path: Path) -> Dict[str, Any]:
    """
    Load lockfile from YAML file.

    Args:
        path: Path to lockfile

    Returns:
        Lockfile dictionary

    Raises:
        FileNotFoundError: If lockfile doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(f"Lockfile not found: {path}")

    with open(path, 'r') as f:
        return yaml.safe_load(f)