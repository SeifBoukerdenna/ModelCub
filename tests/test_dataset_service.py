import json
from pathlib import Path
from modelcub.services.project_service import init_project, InitProjectRequest
from modelcub.services.dataset_service import (
    add_dataset, edit_dataset, info_dataset, list_datasets, delete_dataset,
    AddDatasetRequest, EditDatasetRequest, DeleteDatasetRequest
)
from modelcub.core.registry import AVAILABLE_SOURCES

def _init_project():
    code, _ = init_project(InitProjectRequest(path=".", name="demo", force=False))
    assert code == 0

def test_add_list_info_edit_delete_toy_shapes(fake_shapes_generator, stub_cache_dir, subscribe_events):
    _init_project()

    # add toy-shapes
    req = AddDatasetRequest(name="toy", source="toy-shapes", n=12, train_frac=0.75)
    code, msg = add_dataset(req)
    assert code == 0
    payload = json.loads(msg)
    ds_dir = Path(payload["out"])
    assert (ds_dir / "train").exists() and (ds_dir / "valid").exists()
    # check counts (9 train, 3 valid) from our stub generator
    assert len(list((ds_dir / "train").glob("*.jpg"))) == 9
    assert len(list((ds_dir / "valid").glob("*.jpg"))) == 3

    # list
    code, out = list_datasets()
    assert code == 0 and "toy" in out

    # info
    code, info = info_dataset("toy")
    inf = json.loads(info)
    assert inf["name"] == "toy"
    assert inf["train_images"] == 9
    assert inf["valid_images"] == 3

    # edit classes
    code, msg = edit_dataset(EditDatasetRequest(name="toy", classes="a,b"))
    assert code == 0 and "Updated classes" in msg

    # delete (service requires yes)
    code, msg = delete_dataset(DeleteDatasetRequest(name="toy", yes=True, purge_cache=True))
    assert code == 0 and "Deleted dataset 'toy'" in msg
    assert not ds_dir.exists()

    # events: added, edited, deleted present
    names = [type(e).__name__ for e in subscribe_events]
    assert {"DatasetAdded", "DatasetEdited", "DatasetDeleted"}.issubset(set(names))

def test_add_cub_defaults_auto_split(stub_cache_dir, stub_download_and_extract, subscribe_events, tmp_path):
    _init_project()

    # sanity: registry has the default cub classes
    expected = ["teddy", "polar", "black", "grizzly", "panda"]
    assert AVAILABLE_SOURCES["cub"]["classes"] == expected

    # add cub -> our stubbed download puts a tiny flat zip; auto-split kicks in
    req = AddDatasetRequest(name="cubset", source="cub", n=0)  # n ignored for downloads
    code, msg = add_dataset(req)
    assert code == 0
    payload = json.loads(msg)
    ds_dir = Path(payload["out"])
    assert ds_dir.exists()
    # manifest classes should equal the cub default when no class dirs to infer
    manifest = json.loads((ds_dir / "manifest.json").read_text("utf-8"))
    assert manifest["classes"] == expected

    # split sizes (10 files in stub archive; default train_frac=0.8 -> 8/2)
    from modelcub.services.dataset_service import info_dataset
    code, info = info_dataset("cubset")
    inf = json.loads(info)
    assert inf["train_images"] == 8
    assert inf["valid_images"] == 2

    # clean up
    code, msg = delete_dataset(DeleteDatasetRequest(name="cubset", yes=True, purge_cache=True))
    assert code == 0 and "Deleted dataset 'cubset'" in msg
