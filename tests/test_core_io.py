# tests/test_core_io.py
import io
import tarfile
import zipfile
from pathlib import Path
from modelcub.core.io import (
    sha256_file, extract_archive, copy_tree, delete_tree, download_with_progress
)

def test_sha256_and_copy_delete(tmp_path):
    f = tmp_path / "a.txt"
    f.write_bytes(b"hello")
    h = sha256_file(f)
    assert len(h) == 64

    src = tmp_path / "src"
    dst = tmp_path / "dst"
    (src / "sub").mkdir(parents=True)
    (src / "sub" / "f.bin").write_bytes(b"data")
    copy_tree(src, dst)
    assert (dst / "sub" / "f.bin").read_bytes() == b"data"

    delete_tree(dst)
    assert not dst.exists()

def test_extract_zip_and_tar(tmp_path):
    # zip
    zpath = tmp_path / "t.zip"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("foo.txt", b"zipdata")
    zpath.write_bytes(buf.getvalue())

    out = tmp_path / "zout"
    extract_archive(zpath, out)
    assert (out / "foo.txt").read_bytes() == b"zipdata"

    # tar
    tpath = tmp_path / "t.tar"
    with tarfile.open(tpath, "w") as tf:
        p = tmp_path / "bar.txt"
        p.write_bytes(b"tardata")
        tf.add(p, arcname="bar.txt")

    tout = tmp_path / "tout"
    extract_archive(tpath, tout)
    assert (tout / "bar.txt").read_bytes() == b"tardata"

def test_download_with_progress_stub(monkeypatch, tmp_path):
    # stub urllib.request.urlretrieve to write content
    import urllib.request

    def fake_urlretrieve(url, filename, reporthook=None):
        Path(filename).write_bytes(b"ok")
        if reporthook:
            reporthook(1, 1, 1)
        return filename, None

    monkeypatch.setattr(urllib.request, "urlretrieve", fake_urlretrieve, raising=True)

    dst = tmp_path / "dl.bin"
    download_with_progress("http://example.com/file", dst)
    assert dst.read_bytes() == b"ok"
