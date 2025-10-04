from pathlib import Path
import modelcub.core.generate as G

def test_draw_one_pil_direct(monkeypatch, tmp_path):
    class FakeImage:
        def save(self, p, fmt, quality=92):
            Path(p).write_bytes(b"jpg")
    class FakeImageMod:
        @staticmethod
        def new(*a, **k): return FakeImage()
    class FakeDrawCtx:
        def ellipse(self, *a, **k): pass
        def rectangle(self, *a, **k): pass
        def polygon(self, *a, **k): pass
    class FakeDrawMod:
        @staticmethod
        def Draw(_img): return FakeDrawCtx()

    # Patch directly
    monkeypatch.setattr(G, "_pil", lambda: (FakeImageMod, FakeDrawMod), raising=True)

    out = tmp_path / "pil_one.jpg"
    G._draw_one_pil(out, 32, ["circle", "square", "triangle"])
    assert out.exists() and out.read_bytes() == b"jpg"
