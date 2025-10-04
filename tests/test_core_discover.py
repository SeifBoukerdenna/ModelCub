# tests/test_core_discover.py
from pathlib import Path
from modelcub.core.discover import find_split_dirs, infer_classes_from_subdirs

def test_find_split_and_infer(tmp_path):
    root = tmp_path
    (root / "x/train/dog").mkdir(parents=True)
    (root / "x/train/cat").mkdir(parents=True)
    (root / "x/valid").mkdir(parents=True)

    tr, va = find_split_dirs(root)
    assert tr and va
    classes = infer_classes_from_subdirs(tr)
    assert classes == ["cat", "dog"] or classes == ["dog", "cat"]  # order not guaranteed
