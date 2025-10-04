# tests/test_services_error_paths.py
import json
from pathlib import Path
from modelcub.services.project_service import init_project, delete_project, InitProjectRequest, DeleteProjectRequest
from modelcub.services.dataset_service import (
    add_dataset, delete_dataset, info_dataset, list_datasets,
    AddDatasetRequest, DeleteDatasetRequest
)
from modelcub.core.registry import AVAILABLE_SOURCES

def _init():
    code, _ = init_project(InitProjectRequest(path=".", name=None, force=False))
    assert code == 0

def test_dataset_error_branches(monkeypatch, tmp_path):
    _init()

    # unknown source
    code, msg = add_dataset(AddDatasetRequest(name="x", source="does-not-exist"))
    assert code == 2 and "Unknown source" in msg

    # refuse overwrite when dir exists and non-empty without --force
    d = Path("data/exists")
    (d / "train").mkdir(parents=True)
    (d / "train" / "foo.jpg").write_bytes(b"x")
    code, msg = add_dataset(AddDatasetRequest(name="exists", source="toy-shapes", n=1, force=False))
    assert code == 2 and "Refusing to overwrite" in msg

    # delete without yes refused at service layer
    code, msg = delete_dataset(DeleteDatasetRequest(name="exists", yes=False))
    assert code == 2 and "Refusing to delete" in msg

def test_project_delete_without_yes_and_with_yes(tmp_path):
    _init()
    code, msg = delete_project(DeleteProjectRequest(target=".", yes=False))
    assert code == 2 and "confirmation" in msg

    # re-init to cleanup and test happy path
    _init()
    code, msg = delete_project(DeleteProjectRequest(target=".", yes=True))
    assert code == 0 and "Deleted project directory" in msg

def test_download_source_checksum_and_purge(monkeypatch, tmp_path):
    # init again
    code, _ = init_project(InitProjectRequest(path=".", name=None, force=False))
    assert code == 0

    from modelcub.services import dataset_service as ds
    from modelcub.core import io as cio

    spec = AVAILABLE_SOURCES["cub"].copy()
    spec["sha256"] = "0" * 64
    monkeypatch.setitem(ds.AVAILABLE_SOURCES, "cub_mismatch", spec)

    def fake_download(url: str, dst: Path):
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(b"content")
    monkeypatch.setattr(cio, "download_with_progress", fake_download, raising=True)
    monkeypatch.setattr(ds, "download_with_progress", fake_download, raising=True)

    code, msg = add_dataset(AddDatasetRequest(name="bad", source="cub_mismatch"))
    assert code == 2 and "Checksum mismatch" in msg

    # Prepare a dataset dir so delete path executes purge logic
    ds_root = Path("data/purgeme")
    (ds_root / "train").mkdir(parents=True, exist_ok=True)
    (ds_root / "valid").mkdir(parents=True, exist_ok=True)
    (ds_root / "manifest.json").write_text('{"dataset":"purgeme","classes":[]}', encoding="utf-8")

    # Create a cached file matching naming pattern to be purged
    cache = ds.CACHE_DIR
    cached = cache / f"cub_{Path('archive.zip').name}"
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_bytes(b"dummy")

    # Now delete with purge
    code, msg = delete_dataset(DeleteDatasetRequest(name="purgeme", yes=True, purge_cache=True))
    assert code == 0 and "Purged cache" in msg
