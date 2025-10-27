from __future__ import annotations
import hashlib, shutil, sys, tarfile, urllib.request, zipfile
from pathlib import Path

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def download_with_progress(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    def hook(blocks, block_size, total_size):
        total_size = max(int(total_size), 1)
        done = min(50, int(blocks * block_size * 50 / total_size))
        sys.stdout.write("\r[" + "#" * done + "." * (50 - done) + "]")
        sys.stdout.flush()
    print(f"Downloading: {url}")
    urllib.request.urlretrieve(url, filename=str(dst), reporthook=hook)
    sys.stdout.write("\n")

def extract_archive(archive: Path, dest: Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive, "r") as zf:
            zf.extractall(dest)
    elif tarfile.is_tarfile(archive):
        with tarfile.open(archive, "r:*") as tf:
            tf.extractall(dest)
    else:
        raise RuntimeError(f"Unsupported archive: {archive}")

def copy_tree(src: Path, dst: Path) -> None:
    for p in src.rglob("*"):
        rel = p.relative_to(src)
        out = dst / rel
        if p.is_dir():
            out.mkdir(parents=True, exist_ok=True)
        else:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(p.read_bytes())

def delete_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
