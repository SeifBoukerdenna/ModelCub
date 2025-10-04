import types
from pathlib import Path
from modelcub.core import generate as G
import sys

def test_generate_cv2_path_without_real_cv2_or_numpy(monkeypatch, tmp_path):
    # Fake numpy with the minimal API used in cv2 path
    fake_np = types.SimpleNamespace()
    def _full(shape, val, dtype=None):
        # return any object; our fake cv2 doesn't care about type
        return [["pix"]]
    def _array(x, dtype=None):  # for fillPoly points
        return x
    fake_np.full = _full
    fake_np.array = _array
    sys.modules["numpy"] = fake_np

    # Fake cv2 with minimal API used: circle/rectangle/fillPoly/imwrite + const
    class FakeCV2:
        IMWRITE_JPEG_QUALITY = 1
        def circle(self, *a, **k): pass
        def rectangle(self, *a, **k): pass
        def fillPoly(self, *a, **k): pass
        def imwrite(self, path, img, params):
            Path(path).write_bytes(b"jpg")
            return True
    fake_cv2 = FakeCV2()

    # Force cv2 path
    monkeypatch.setattr(G, "_cv2", lambda: fake_cv2, raising=True)
    # Ensure PIL path is not taken
    monkeypatch.setattr(G, "_pil", lambda: (None, None), raising=True)

    train = tmp_path / "train"
    valid = tmp_path / "valid"
    G.gen_shapes_dataset(train, valid, n_total=4, train_frac=0.5, imgsz=24,
                         classes=["circle","square","triangle"], seed=42)
    assert len(list(train.glob("*.jpg"))) == 2
    assert len(list(valid.glob("*.jpg"))) == 2
