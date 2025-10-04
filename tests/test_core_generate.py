# tests/test_core_generate.py
from pathlib import Path
import types
from modelcub.core import generate as G

def test_generate_pil_path_without_real_pil(monkeypatch, tmp_path):
    # force cv2 path to be unavailable
    monkeypatch.setattr(G, "_cv2", lambda: None, raising=True)

    # build fake PIL modules
    class FakeImage:
        def __init__(self, mode, size, color): self.mode, self.size = mode, size
        def save(self, path, fmt, quality=92): Path(path).write_bytes(b"jpg")

    class FakeImageMod:
        @staticmethod
        def new(mode, size, color): return FakeImage(mode, size, color)

    class FakeDrawCtx:
        def ellipse(self, *_args, **_kwargs): pass
        def rectangle(self, *_args, **_kwargs): pass
        def polygon(self, *_args, **_kwargs): pass

    class FakeDrawMod:
        @staticmethod
        def Draw(_img): return FakeDrawCtx()

    # force pil path
    monkeypatch.setattr(G, "_pil", lambda: (FakeImageMod, FakeDrawMod), raising=True)

    train = tmp_path / "train"
    valid = tmp_path / "valid"
    G.gen_shapes_dataset(train, valid, n_total=4, train_frac=0.5, imgsz=32, classes=["circle","square","triangle"], seed=0)

    assert len(list(train.glob("*.jpg"))) == 2
    assert len(list(valid.glob("*.jpg"))) == 2

def test_triangle_points_and_canvas_params():
    # small sanity on helpers to cover pure code
    pts = G._triangle_points(10, 10, 5)
    assert len(pts) == 3
    W, H, margin, max_size = G._canvas_params(32)
    assert W == H == 32
    assert margin >= 4
    assert max_size >= 3
