# tests/test_commands_negative.py
from argparse import Namespace
from modelcub.commands.project import run as proj_run
from modelcub.commands.dataset import run as ds_run

def test_commands_unknowns():
    assert proj_run(Namespace(proj_cmd="unknown")) == 2
    assert ds_run(Namespace(ds_cmd="unknown")) == 2
