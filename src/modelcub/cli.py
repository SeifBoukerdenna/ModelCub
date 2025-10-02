import argparse
from .commands.about import run as about_run
from .commands.init import run as init_run


def main(argv=None):
    parser = argparse.ArgumentParser(prog="modelcub", description="ModelCub CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_about = sub.add_parser("about", help="Show version and environment info.")
    p_about.set_defaults(func=about_run)

    p_init = sub.add_parser("init", help="Create a new ModelCub project skeleton.")
    p_init.add_argument("path", nargs="?", default=".", help="Target directory (default: current).")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing files.")
    p_init.set_defaults(func=init_run)

    args = parser.parse_args(argv)
    return args.func(args)
