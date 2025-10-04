# tests/test_core_paths.py
from pathlib import Path
from modelcub.core.paths import project_root

def test_project_root_fallback_when_missing_yaml(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    # no modelcub.yaml anywhere upward
    assert project_root() == tmp_path.resolve()
