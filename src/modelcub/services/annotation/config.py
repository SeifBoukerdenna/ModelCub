# src/modelcub/services/annotation/config.py
"""
Configuration management for annotation service.
"""
from __future__ import annotations
from pathlib import Path
from typing import List


class ConfigManager:
    """Manages configuration for the annotation service."""

    @staticmethod
    def load_classes() -> List[str]:
        """Load classes from modelcub.yaml."""
        yaml_path = Path('modelcub.yaml')

        if not yaml_path.exists():
            return ['object']  # Default

        try:
            content = yaml_path.read_text()
            for line in content.splitlines():
                if line.strip().startswith('classes:'):
                    # Parse the classes list
                    classes_str = line.split(':', 1)[1].strip()
                    if classes_str.startswith('[') and classes_str.endswith(']'):
                        classes = [c.strip() for c in classes_str[1:-1].split(',')]
                        return [c for c in classes if c]
        except Exception as e:
            print(f"Warning: Could not load classes from modelcub.yaml: {e}")

        return ['object']  # Default fallback