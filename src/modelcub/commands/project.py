from __future__ import annotations
from ..services.project_service import (
    init_project, delete_project,
    InitProjectRequest, DeleteProjectRequest
)

def _confirm(prompt: str) -> bool:
    try:
        ans = input(prompt).strip().lower()
    except EOFError:
        ans = "n"
    return ans in ("y", "yes")

def run(args):
    cmd = getattr(args, "proj_cmd", None)
    if cmd == "init":
        name = args.name
        path = name
        code, msg = init_project(InitProjectRequest(path, name, bool(args.force)))
        print(msg)
        return code

    if cmd == "delete":
        # ask here; service stays pure/guarded
        req = DeleteProjectRequest(getattr(args, "target", None), bool(args.yes))
        if not req.yes:
            print("WARNING: This will permanently delete the project directory.")
            if not _confirm("Are you sure you want to delete this project? [y/N]: "):
                print("Aborted."); return 0
            req.yes = True
        code, msg = delete_project(req)
        print(msg); return code
    print("Unknown project command."); return 2
