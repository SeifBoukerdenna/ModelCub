from __future__ import annotations
from ..services.dataset_service import (
    list_datasets, info_dataset,
    add_dataset, edit_dataset, delete_dataset,
    AddDatasetRequest, EditDatasetRequest, DeleteDatasetRequest
)

def _confirm(prompt: str) -> bool:
    try:
        ans = input(prompt).strip().lower()
    except EOFError:
        ans = "n"
    return ans in ("y", "yes")

def run(args):
    cmd = getattr(args, "ds_cmd", None)

    if cmd == "list":
        code, msg = list_datasets(); print(msg); return code

    if cmd == "info":
        code, msg = info_dataset(args.name); print(msg); return code

    if cmd == "add":
        req = AddDatasetRequest(
            name=args.name, source=str(args.source),
            classes_override=getattr(args, "classes", None),
            n=int(getattr(args, "n", 200)),
            train_frac=float(getattr(args, "train_frac", 0.8)),
            imgsz=int(getattr(args, "imgsz", 640)),
            seed=int(getattr(args, "seed", 123)),
            force=bool(getattr(args, "force", False)),
        )
        code, msg = add_dataset(req); print(msg); return code

    if cmd == "edit":
        req = EditDatasetRequest(name=args.name, classes=args.classes)
        code, msg = edit_dataset(req); print(msg); return code

    if cmd == "delete":
        req = DeleteDatasetRequest(
            name=args.name, yes=bool(args.yes),
            purge_cache=bool(args.purge_cache)
        )
        if not req.yes:
            if not _confirm(f"Are you sure you want to delete dataset '{args.name}'? [y/N]: "):
                print("Aborted."); return 0
            req.yes = True
        code, msg = delete_dataset(req); print(msg); return code

    print("Unknown dataset command."); return 2
