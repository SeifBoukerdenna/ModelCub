# tests/test_core_yaml_cfg.py
from pathlib import Path
from modelcub.core.yaml_cfg import ensure_yaml_defaults, replace_yaml_classes
from modelcub.core.paths import project_root

def test_ensure_and_replace_yaml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "modelcub.yaml").write_text("project: demo\nimages: data\n", encoding="utf-8")

    ensure_yaml_defaults(["a","b"])
    txt = (tmp_path / "modelcub.yaml").read_text("utf-8")
    assert "classes: [a, b]" in txt

    replace_yaml_classes(["x","y","z"])
    txt = (tmp_path / "modelcub.yaml").read_text("utf-8")
    assert "classes: [x, y, z]" in txt
