from pathlib import Path
from modelcub.services.project_service import (
    init_project, delete_project, InitProjectRequest, DeleteProjectRequest
)

def test_project_init_and_delete(subscribe_events, tmp_path):
    # init
    code, msg = init_project(InitProjectRequest(path=".", name="demo", force=False))
    assert code == 0
    root = Path(".").resolve()
    assert (root / "modelcub.yaml").exists()
    assert (root / "data").is_dir()
    assert (root / "models").is_dir()
    assert "Initialized ModelCub project" in msg

    # delete without --yes should be blocked at service level
    code, msg = delete_project(DeleteProjectRequest(target=".", yes=False))
    assert code == 2 and "confirmation" in msg

    # delete with confirmation
    code, msg = delete_project(DeleteProjectRequest(target=".", yes=True))
    assert code == 0
    assert "Deleted project directory" in msg
    assert not root.exists()

    # events fired (at least ProjectInitialized and ProjectDeleted)
    names = [type(e).__name__ for e in subscribe_events]
    assert "ProjectInitialized" in names
    assert "ProjectDeleted" in names
