import types, sys
from pathlib import Path
import modelcub.core.generate as G

def test_draw_one_cv2_direct(monkeypatch, tmp_path):
    # Minimal fake numpy with int32
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
            Path(path).write_bytes(b"jpg"); return True

    # Patch AFTER any reloads (we’re not reloading here)
    monkeypatch.setattr(G, "_cv2", lambda: FakeCV2(), raising=True)

    out = tmp_path / "cv2_one.jpg"
    G._draw_one_cv2(out, 48, ["circle", "square", "triangle"])
    assert out.exists() and out.read_bytes() == b"jpg"

    sys.modules.pop("numpy", None)
