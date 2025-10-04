import importlib
import pytest
import modelcub.core.generate as G

def test_cv2_path_requires_numpy(monkeypatch, tmp_path):
    # Reload to restore real functions (not autouse stub)
    importlib.reload(G)

    class FakeCV2:
        IMWRITE_JPEG_QUALITY = 1
        def circle(self, *a, **k): pass
        def rectangle(self, *a, **k): pass
        def fillPoly(self, *a, **k): pass
        def imwrite(self, path, img, params): return True

    # Force cv2 backend, but make numpy import fail
    monkeypatch.setattr(G, "_cv2", lambda: FakeCV2(), raising=True)
    # Ensure _pil returns None/None so cv2 path is the one used
    monkeypatch.setattr(G, "_pil", lambda: (None, None), raising=True)

    # Remove any cached numpy so import fails inside _draw_one_cv2
    import sys
    sys.modules.pop("numpy", None)

    with pytest.raises(RuntimeError):
        G._draw_one_cv2(tmp_path/"x.jpg", 24, ["circle"])
