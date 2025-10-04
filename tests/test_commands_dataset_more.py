from argparse import Namespace
from modelcub.commands.dataset import run as ds_run
from modelcub.services.project_service import init_project, InitProjectRequest

def test_dataset_info_error_via_commands():
    init_project(InitProjectRequest(path=".", name="p", force=False))
    # info on non-existent dataset should bubble code 2
    code = ds_run(Namespace(ds_cmd="info", name="nope"))
    assert code == 2
