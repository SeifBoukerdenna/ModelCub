import types
import sys
import pytest
import importlib
from modelcub.core import generate as G

def test__cv2_failure_path(monkeypatch):
    # Ensure no cv2 -> returns None (executes try/except)
    monkeypatch.setitem(sys.modules, "cv2", None)
    # Remove if present (avoid leftover fake)
    sys.modules.pop("cv2", None)
    assert G._cv2() is None  # executes lines 12-16

def test__cv2_success_path(monkeypatch):
    class FakeCV2: pass
    monkeypatch.setitem(sys.modules, "cv2", FakeCV2())
    try:
        got = G._cv2()
        assert isinstance(got, FakeCV2)
    finally:
        sys.modules.pop("cv2", None)

def test__pil_failure_path(monkeypatch):
    # Ensure no PIL -> returns (None, None) (executes lines 20-24)
    sys.modules.pop("PIL", None)
    img, drw = G._pil()
    assert img is None and drw is None

def test__pil_success_path(monkeypatch):
    # Build a minimal fake PIL package with Image and ImageDraw
    class FakeImage: pass
    class FakeImageDraw: pass
    fake_PIL = types.SimpleNamespace(Image=FakeImage, ImageDraw=FakeImageDraw)
    monkeypatch.setitem(sys.modules, "PIL", fake_PIL)
    try:
        img, drw = G._pil()
        assert img is FakeImage and drw is FakeImageDraw
    finally:
        sys.modules.pop("PIL", None)

def test__canvas_params_small_and_large():
    W, H, margin, max_size = G._canvas_params(24)
    assert (W, H) == (24, 24)
    assert margin >= 4
    assert max_size >= 3

    W2, H2, margin2, max_size2 = G._canvas_params(2048)
    # margin is capped at 80 in implementation
    assert margin2 == 80
    assert max_size2 >= 3

def test_gen_shapes_dataset_early_return(tmp_path, monkeypatch):
    # Force no backends to prove we exit before checking (_cv2/_pil not even needed)
    monkeypatch.setattr(G, "_cv2", lambda: None, raising=True)
    monkeypatch.setattr(G, "_pil", lambda: (None, None), raising=True)
    train = tmp_path / "train"; valid = tmp_path / "valid"
    # n_total <= 0 => should NO-OP, not raise
    G.gen_shapes_dataset(train, valid, n_total=0, train_frac=0.5, imgsz=32,
                         classes=["c","s","t"], seed=0)
    assert not train.exists() and not valid.exists()


def test_gen_shapes_dataset_no_backends_raises(tmp_path, monkeypatch):
    # reload to undo the autouse stub on gen_shapes_dataset
    import modelcub.core.generate as Gmod
    importlib.reload(Gmod)

    # now patch on the reloaded module object
    monkeypatch.setattr(Gmod, "_cv2", lambda: None, raising=True)
    monkeypatch.setattr(Gmod, "_pil", lambda: (None, None), raising=True)

    # with n_total > 0 and no backends, it should raise
    with pytest.raises(RuntimeError):
        Gmod.gen_shapes_dataset(tmp_path/"train", tmp_path/"valid",
                                n_total=2, train_frac=0.5, imgsz=32,
                                classes=["c","s","t"], seed=1)
