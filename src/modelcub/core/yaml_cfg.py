from __future__ import annotations
from pathlib import Path
from .paths import project_root

def ensure_yaml_defaults(fallback_classes: list[str]) -> None:
    """Ensure modelcub.yaml contains a classes: [...] line (fallback insert)."""
    yaml_path = project_root() / "modelcub.yaml"
    text = yaml_path.read_text("utf-8") if yaml_path.exists() else ""
    lines = [ln.rstrip("\n") for ln in text.splitlines()] if text else []
    if not any(ln.strip().startswith("classes:") for ln in lines):
        lines.append("classes: [" + ", ".join(fallback_classes) + "]")
        yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def replace_yaml_classes(new_classes: list[str]) -> None:
    """Replace classes: [...] in modelcub.yaml (or append if missing)."""
    yaml_path = project_root() / "modelcub.yaml"
    text = yaml_path.read_text("utf-8") if yaml_path.exists() else ""
    lines = [ln.rstrip("\n") for ln in text.splitlines()] if text else []
    replaced, out = False, []
    for ln in lines:
        if ln.strip().startswith("classes:"):
            out.append("classes: [" + ", ".join(new_classes) + "]")
            replaced = True
        else:
            out.append(ln)
    if not replaced:
        out.append("classes: [" + ", ".join(new_classes) + "]")
    yaml_path.write_text("\n".join(out) + "\n", encoding="utf-8")
