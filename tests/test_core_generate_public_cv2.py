import types, sys, importlib
import modelcub.core.generate as G

def test_gen_shapes_dataset_cv2_backend(monkeypatch, tmp_path):
    # Reload to restore real gen_shapes_dataset (autouse stub bypass)
    importlib.reload(G)

    # Fake numpy with int32
    np = types.SimpleNamespace(
        full=lambda shape, val, dtype=None: [["pix"]],
        array=lambda x, dtype=None: x,
        uint8=object,
        int32=int,
    )
    sys.modules["numpy"] = np

    class FakeCV2:
        IMWRITE_JPEG_QUALITY = 1
        def circle(self, *a, **k): pass
        def rectangle(self, *a, **k): pass
        def fillPoly(self, *a, **k): pass
        def imwrite(self, path, img, params):
            open(path, "wb").write(b"jpg"); return True

    # Patch AFTER reload
    monkeypatch.setattr(G, "_cv2", lambda: FakeCV2(), raising=True)
    monkeypatch.setattr(G, "_pil", lambda: (None, None), raising=True)

    train = tmp_path / "train"; valid = tmp_path / "valid"
    G.gen_shapes_dataset(train, valid, n_total=5, train_frac=0.6, imgsz=24,
                         classes=["circle","square","triangle"], seed=0)

    assert len(list(train.glob("*.jpg"))) == 3
    assert len(list(valid.glob("*.jpg"))) == 2

    sys.modules.pop("numpy", None)
