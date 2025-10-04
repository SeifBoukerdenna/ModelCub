# tests/test_commands_about.py
from argparse import Namespace
from modelcub.commands.about import run as about_run

def test_about_runs_smoke():
    assert about_run(Namespace()) == 0
