# src/modelcub/services/annotation/shortcuts.py
"""
Keyboard shortcut configuration and management.
"""
from __future__ import annotations
from typing import Dict, List
from dataclasses import dataclass, asdict
import json
from pathlib import Path


@dataclass
class Shortcut:
    """Keyboard shortcut definition."""
    key: str
    action: str
    description: str
    category: str
    modifiers: List[str] = None

    def __post_init__(self):
        if self.modifiers is None:
            self.modifiers = []


class ShortcutManager:
    """Manages keyboard shortcuts for the annotation interface."""

    DEFAULT_SHORTCUTS = {
        # Navigation
        'ArrowLeft': Shortcut('ArrowLeft', 'previous_image', 'Previous image', 'Navigation'),
        'ArrowRight': Shortcut('ArrowRight', 'next_image', 'Next image', 'Navigation'),
        'Home': Shortcut('Home', 'first_image', 'First image', 'Navigation'),
        'End': Shortcut('End', 'last_image', 'Last image', 'Navigation'),

        # Tools
        'b': Shortcut('b', 'tool_bbox', 'Bounding Box tool', 'Tools'),
        'p': Shortcut('p', 'tool_polygon', 'Polygon tool', 'Tools'),
        's': Shortcut('s', 'tool_select', 'Select tool', 'Tools'),
        'v': Shortcut('v', 'tool_select', 'Select tool (alternate)', 'Tools'),
        'Tab': Shortcut('Tab', 'cycle_tool', 'Cycle through tools', 'Tools'),

        # Quick class selection (1-9)
        '1': Shortcut('1', 'select_class_0', 'Select class 1', 'Classes'),
        '2': Shortcut('2', 'select_class_1', 'Select class 2', 'Classes'),
        '3': Shortcut('3', 'select_class_2', 'Select class 3', 'Classes'),
        '4': Shortcut('4', 'select_class_3', 'Select class 4', 'Classes'),
        '5': Shortcut('5', 'select_class_4', 'Select class 5', 'Classes'),
        '6': Shortcut('6', 'select_class_5', 'Select class 6', 'Classes'),
        '7': Shortcut('7', 'select_class_6', 'Select class 7', 'Classes'),
        '8': Shortcut('8', 'select_class_7', 'Select class 8', 'Classes'),
        '9': Shortcut('9', 'select_class_8', 'Select class 9', 'Classes'),

        # Actions
        'Delete': Shortcut('Delete', 'delete_selected', 'Delete selected annotation', 'Actions'),
        'Backspace': Shortcut('Backspace', 'delete_selected', 'Delete selected (alternate)', 'Actions'),
        'Escape': Shortcut('Escape', 'cancel', 'Cancel current action', 'Actions'),
        'Enter': Shortcut('Enter', 'confirm', 'Confirm current action', 'Actions'),
        ' ': Shortcut(' ', 'toggle_mode', 'Quick toggle mode', 'Actions'),

        # View
        'g': Shortcut('g', 'toggle_grid', 'Toggle grid', 'View'),
        'h': Shortcut('h', 'toggle_labels', 'Toggle annotation labels', 'View'),
        'f': Shortcut('f', 'fit_to_screen', 'Fit image to screen', 'View'),
        'z': Shortcut('z', 'zoom_in', 'Zoom in', 'View'),
        'x': Shortcut('x', 'zoom_out', 'Zoom out', 'View'),
        '0': Shortcut('0', 'zoom_reset', 'Reset zoom', 'View'),

        # Edit
        'a': Shortcut('a', 'select_all', 'Select all annotations', 'Edit'),
        'd': Shortcut('d', 'duplicate', 'Duplicate selected', 'Edit'),
        'c': Shortcut('c', 'copy', 'Copy selected', 'Edit', ['ctrl']),
        'v_paste': Shortcut('v', 'paste', 'Paste', 'Edit', ['ctrl']),
        'z_undo': Shortcut('z', 'undo', 'Undo', 'Edit', ['ctrl']),
        'y_redo': Shortcut('y', 'redo', 'Redo', 'Edit', ['ctrl']),
        'Z_redo': Shortcut('Z', 'redo', 'Redo (alternate)', 'Edit', ['ctrl', 'shift']),

        # Save
        's_save': Shortcut('s', 'save', 'Save annotations', 'File', ['ctrl']),
        'S_save_all': Shortcut('S', 'save_all', 'Save all', 'File', ['ctrl', 'shift']),

        # Help
        '?': Shortcut('?', 'show_shortcuts', 'Show shortcuts', 'Help'),
        '/': Shortcut('/', 'show_shortcuts', 'Show shortcuts (alternate)', 'Help'),
    }

    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path('.modelcub_shortcuts.json')
        self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
        self.load()

    def load(self) -> None:
        """Load custom shortcuts from config file."""
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)

            for key, shortcut_data in data.items():
                self.shortcuts[key] = Shortcut(**shortcut_data)
        except Exception as e:
            print(f"Warning: Could not load shortcuts: {e}")

    def save(self) -> None:
        """Save shortcuts to config file."""
        try:
            data = {
                key: asdict(shortcut)
                for key, shortcut in self.shortcuts.items()
            }

            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving shortcuts: {e}")

    def get_shortcuts(self) -> Dict[str, dict]:
        """Get all shortcuts as dictionary."""
        return {
            key: asdict(shortcut)
            for key, shortcut in self.shortcuts.items()
        }

    def get_shortcuts_by_category(self) -> Dict[str, List[dict]]:
        """Get shortcuts grouped by category."""
        categories = {}

        for shortcut in self.shortcuts.values():
            category = shortcut.category
            if category not in categories:
                categories[category] = []
            categories[category].append(asdict(shortcut))

        return categories

    def reset_to_defaults(self) -> None:
        """Reset shortcuts to defaults."""
        self.shortcuts = self.DEFAULT_SHORTCUTS.copy()
        self.save()