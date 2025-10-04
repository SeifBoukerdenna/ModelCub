from argparse import Namespace
from modelcub.commands.project import run as proj_run
from modelcub.commands.dataset import run as ds_run

def test_commands_wire_happily(monkeypatch):
    # project init
    code = proj_run(Namespace(proj_cmd="init", path=".", name="wire", force=False))
    assert code == 0

    # dataset add via commands layer (toy-shapes); generator is stubbed autouse
    code = ds_run(Namespace(
        ds_cmd="add", name="wiretoy", source="toy-shapes",
        classes=None, n=4, train_frac=0.5, imgsz=64, seed=1, force=True
    ))
    assert code == 0

    # dataset delete path (simulate user confirming "yes")
    monkeypatch.setattr("builtins.input", lambda _=None: "y")
    code = ds_run(Namespace(ds_cmd="delete", name="wiretoy", yes=False, purge_cache=False))
    assert code == 0

    # project delete path (confirm)
    monkeypatch.setattr("builtins.input", lambda _=None: "y")
    code = proj_run(Namespace(proj_cmd="delete", target=".", yes=False))
    assert code == 0
