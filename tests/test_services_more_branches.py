from pathlib import Path
import json
from modelcub.services.project_service import (
    init_project, delete_project, InitProjectRequest, DeleteProjectRequest
)
from modelcub.services.dataset_service import (
    add_dataset, info_dataset, list_datasets, edit_dataset, delete_dataset,
    AddDatasetRequest, EditDatasetRequest, DeleteDatasetRequest
)
from modelcub.core.registry import AVAILABLE_SOURCES

def _init_here():
    code, _ = init_project(InitProjectRequest(path=".", name="p", force=False))
    assert code == 0

def test_dataset_info_missing_manifest_and_override_classes(tmp_path, monkeypatch):
    _init_here()

    # Create dataset dir without manifest -> info should return error
    d = Path("data/emptyset")
    (d / "train").mkdir(parents=True)
    (d / "valid").mkdir(parents=True)
    code, msg = info_dataset("emptyset")
    assert code == 2 and "No manifest" in msg

    # Add toy-shapes with override classes (generator stub from previous conftest)
    code, out = add_dataset(AddDatasetRequest(
        name="toyov", source="toy-shapes", n=4, train_frac=0.5, classes_override="x,y"
    ))
    assert code == 0
    mani = json.loads((Path("data/toyov") / "manifest.json").read_text())
    assert mani["classes"] == ["x","y"]

def test_project_delete_non_project_path(tmp_path):
    # try deleting a non-project folder
    np = tmp_path / "notproj"
    np.mkdir()
    code, msg = delete_project(DeleteProjectRequest(target=str(np), yes=True))
    assert code == 2 and "Not a ModelCub project" in msg

def test_registry_missing_url_branch(monkeypatch):
    _init_here()
    # Inject a source with no URL to hit 'missing url' branch
    from modelcub.services import dataset_service as ds
    src = {"description": "no url", "classes": ["a"], "generator": None, "url": None}
    monkeypatch.setitem(ds.AVAILABLE_SOURCES, "no_url", src)
    code, msg = add_dataset(AddDatasetRequest(name="nourl", source="no_url"))
    assert code == 2 and "missing 'url'" in msg

def test_commands_delete_yes_bypass_prompt(monkeypatch):
    _init_here()
    # Make a tiny dataset to allow service delete to run (and no prompt)
    d = Path("data/dy")
    (d / "train").mkdir(parents=True)
    (d / "valid").mkdir(parents=True)
    (d / "manifest.json").write_text('{"dataset":"dy","classes":[]}', encoding="utf-8")
    code, msg = delete_dataset(DeleteDatasetRequest(name="dy", yes=True, purge_cache=False))
    assert code == 0
