# tests/test_cli_wiring.py
from modelcub import cli

def test_cli_project_init_and_delete_wire(monkeypatch):
    called = []

    def fake_run(args):
        # record which subparser ran
        called.append((getattr(args, "proj_cmd", None), getattr(args, "ds_cmd", None)))
        return 0

    # Patch the bound call sites used by cli.main
    monkeypatch.setattr(cli, "project_run", fake_run, raising=True)
    monkeypatch.setattr(cli, "dataset_run", fake_run, raising=True)
    monkeypatch.setattr(cli, "about_run", lambda a: 0, raising=True)

    # create project in ./foo
    code = cli.main(["project", "init", "foo", "--name", "foo"])
    assert code == 0

    # now delete by name (./foo)
    code = cli.main(["project", "delete", "foo", "--yes"])
    assert code == 0

    # dataset add/list just to exercise wiring
    code = cli.main(["dataset", "add", "toy", "--source", "toy-shapes", "--force"])
    assert code == 0
    code = cli.main(["dataset", "list"])
    assert code == 0

    # about
    code = cli.main(["about"])
    assert code == 0

    # sanity: our fake_run was invoked for both project subcommands
    assert ("init", None) in called
    assert ("delete", None) in called
