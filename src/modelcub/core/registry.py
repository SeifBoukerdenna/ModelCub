from __future__ import annotations

# Built-in dataset sources shipped with ModelCub.
# - "cub" defaults to the requested classes (teddy, polar, black, grizzly, panda)
AVAILABLE_SOURCES: dict[str, dict] = {
    "toy-shapes": {
        "description": "Synthetic circles/squares/triangles for quick demos.",
        "classes": ["circle", "square", "triangle"],
        "generator": "shapes",
    },
    "cub": {
        "description": "Bears dataset (teddy, polar, black, grizzly, panda).",
        "classes": ["teddy", "polar", "black", "grizzly", "panda"],
        "generator": None,
        "url": "https://github.com/user-attachments/files/22673489/archive.zip",
        "sha256": None,
        "root_in_zip": None,
    },
}
