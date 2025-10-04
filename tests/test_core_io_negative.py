from pathlib import Path
import pytest
from modelcub.core.io import extract_archive

def test_extract_unsupported_archive_raises(tmp_path):
    bad = tmp_path / "weird.bin"
    bad.write_bytes(b"not-archive")
    with pytest.raises(RuntimeError):
        extract_archive(bad, tmp_path / "out")
