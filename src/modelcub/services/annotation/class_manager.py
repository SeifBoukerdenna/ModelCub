# src/modelcub/services/annotation/class_manager.py
"""
Dynamic class management for annotation service.
"""
from __future__ import annotations
from pathlib import Path
from typing import List


class ClassManager:
    """Manages annotation classes with YAML sync."""

    def __init__(self, yaml_path: Path = None):
        self.yaml_path = yaml_path or Path('modelcub.yaml')
        self._classes = []
        self.load()

    def load(self) -> List[str]:
        """Load classes from YAML."""
        if not self.yaml_path.exists():
            self._classes = ['object']
            return self._classes

        try:
            content = self.yaml_path.read_text()
            for line in content.splitlines():
                if line.strip().startswith('classes:'):
                    classes_str = line.split(':', 1)[1].strip()
                    if classes_str.startswith('[') and classes_str.endswith(']'):
                        self._classes = [
                            c.strip()
                            for c in classes_str[1:-1].split(',')
                            if c.strip()
                        ]
                        return self._classes
        except Exception as e:
            print(f"Warning: Could not load classes: {e}")

        self._classes = ['object']
        return self._classes

    def save(self) -> None:
        """Save classes to YAML."""
        if not self.yaml_path.exists():
            print(f"Warning: YAML file not found: {self.yaml_path}")
            return

        try:
            content = self.yaml_path.read_text()
            lines = content.splitlines()

            # Find and replace classes line
            new_lines = []
            replaced = False

            for line in lines:
                if line.strip().startswith('classes:'):
                    new_lines.append(f"classes: [{', '.join(self._classes)}]")
                    replaced = True
                else:
                    new_lines.append(line)

            # Add classes line if not found
            if not replaced:
                new_lines.append(f"classes: [{', '.join(self._classes)}]")

            # Write back with newline at end
            self.yaml_path.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
            print(f"✅ Saved classes to {self.yaml_path}: {self._classes}")
        except Exception as e:
            print(f"❌ Error saving classes: {e}")

    def get_classes(self) -> List[str]:
        """Get current classes."""
        return self._classes.copy()

    def add_class(self, class_name: str) -> bool:
        """Add a new class."""
        class_name = class_name.strip()
        if not class_name or class_name in self._classes:
            return False

        self._classes.append(class_name)
        self.save()
        return True

    def remove_class(self, class_name: str) -> bool:
        """Remove a class."""
        if class_name in self._classes:
            self._classes.remove(class_name)
            self.save()
            return True
        return False

    def rename_class(self, old_name: str, new_name: str) -> bool:
        """Rename a class."""
        new_name = new_name.strip()
        if old_name not in self._classes or not new_name:
            return False

        if new_name in self._classes and new_name != old_name:
            return False  # Already exists

        idx = self._classes.index(old_name)
        self._classes[idx] = new_name
        self.save()
        return True

    def reorder_classes(self, classes: List[str]) -> bool:
        """Reorder classes."""
        # Verify all classes are present
        if set(classes) != set(self._classes):
            return False

        self._classes = classes
        self.save()
        return True

    def reload(self) -> List[str]:
        """Reload classes from YAML (for external changes)."""
        return self.load()