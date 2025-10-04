# tests/conftest.py
import io
import zipfile
from pathlib import Path
import pytest

def _touch_file(p: Path, content: bytes = b"\xff\xd8\xff"):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)

@pytest.fixture(autouse=True)
def _isolate_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path

@pytest.fixture(autouse=True)
def fake_shapes_generator(monkeypatch):
    """
    Stub gen_shapes_dataset both at the source module and where the service imported it.
    Autouse so command-layer tests use the stub too.
    """
    # Source module
    from modelcub.core import generate as gen

    def _stub(train_dir: Path, valid_dir: Path, n_total: int, train_frac: float, imgsz: int, classes, seed: int):
        n_train = int(n_total * train_frac)
        n_valid = max(0, n_total - n_train)
        for i in range(n_train):
            _touch_file(train_dir / f"img_{i:05d}.jpg")
        for i in range(n_valid):
            _touch_file(valid_dir / f"img_{i:05d}.jpg")

    monkeypatch.setattr(gen, "gen_shapes_dataset", _stub, raising=True)

    # Service module imported the symbol at import time → patch there too
    import modelcub.services.dataset_service as ds
    monkeypatch.setattr(ds, "gen_shapes_dataset", _stub, raising=True)

    return _stub

@pytest.fixture
def stub_cache_dir(tmp_path, monkeypatch):
    """
    Point CACHE_DIR into tmp in BOTH the source and the service module.
    """
    from modelcub.core import paths
    import modelcub.services.dataset_service as ds

    new_cache = tmp_path / ".cache" / "datasets"
    new_cache.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(paths, "CACHE_DIR", new_cache, raising=True)
    monkeypatch.setattr(ds, "CACHE_DIR", new_cache, raising=True)
    return new_cache

@pytest.fixture
def fake_cub_archive(tmp_path):
    """ZIP with 10 flat .jpg files to drive auto-split 8/2."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for i in range(10):
            z.writestr(f"img_{i:02d}.jpg", b"\xff\xd8\xff")
    buf.seek(0)
    zip_path = tmp_path / "cub_flat.zip"
    zip_path.write_bytes(buf.getvalue())
    return zip_path

@pytest.fixture
def stub_download_and_extract(monkeypatch, fake_cub_archive):
    """
    Patch download_with_progress in BOTH the source and service modules.
    (extract_archive stays real; it can read our tiny zip.)
    """
    from modelcub.core import io as cio
    import modelcub.services.dataset_service as ds

    def fake_download(url: str, dst: Path):
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(fake_cub_archive.read_bytes())

    monkeypatch.setattr(cio, "download_with_progress", fake_download, raising=True)
    monkeypatch.setattr(ds, "download_with_progress", fake_download, raising=True)
    return True

@pytest.fixture
def subscribe_events():
    """Capture published events for assertions."""
    from modelcub import events
    seen = []
    def record(e): seen.append(e)
    for et in (events.ProjectInitialized, events.ProjectDeleted,
               events.DatasetAdded, events.DatasetEdited, events.DatasetDeleted):
        events.bus.subscribe(et, record)
    return seen
