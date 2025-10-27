"""
Atomic I/O utilities for safe concurrent operations.

Provides atomic file writes and file-based locking to prevent
corruption from concurrent access or crashes mid-write.
"""

import os
import time
import tempfile
from pathlib import Path
from typing import Optional


def atomic_write(path: Path, content: str, encoding: str = 'utf-8') -> None:
    """
    Atomic file write using tmp file + rename.

    Prevents corruption from concurrent writes or crashes mid-write.
    Works on all platforms (Windows, Linux, macOS).

    Args:
        path: Target file path
        content: Content to write
        encoding: File encoding (default: utf-8)
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Write to temp file in same directory (same filesystem)
    fd, tmp_path = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp"
    )

    try:
        with os.fdopen(fd, 'w', encoding=encoding) as f:
            f.write(content)

        # Atomic rename (POSIX) or move (Windows)
        os.replace(tmp_path, str(path))
    except:
        # Clean up temp file on error
        try:
            os.unlink(tmp_path)
        except:
            pass
        raise


class FileLock:
    """
    Simple file-based lock for registry operations.

    Uses lock files + polling. Works across platforms.
    Not suitable for high-concurrency scenarios but sufficient for ModelCub.

    Usage:
        with FileLock(registry_path):
            # perform atomic operation
            registry = load_registry()
            registry['key'] = 'value'
            save_registry(registry)
    """

    def __init__(
        self,
        path: Path,
        timeout: float = 30.0,
        poll_interval: float = 0.1
    ):
        """
        Args:
            path: Path to the file being protected
            timeout: Max seconds to wait for lock (default: 30)
            poll_interval: Seconds between lock acquisition attempts
        """
        self.path = Path(path)
        self.lock_path = self.path.parent / f".{self.path.name}.lock"
        self.timeout = timeout
        self.poll_interval = poll_interval
        self._acquired = False

    def acquire(self) -> bool:
        """Acquire the lock with timeout."""
        start_time = time.time()

        while True:
            try:
                # Try to create lock file exclusively
                fd = os.open(
                    self.lock_path,
                    os.O_CREAT | os.O_EXCL | os.O_WRONLY
                )
                os.close(fd)
                self._acquired = True
                return True
            except FileExistsError:
                # Lock exists, check timeout
                if time.time() - start_time > self.timeout:
                    raise TimeoutError(
                        f"Could not acquire lock on {self.path} "
                        f"after {self.timeout}s"
                    )
                time.sleep(self.poll_interval)

    def release(self) -> None:
        """Release the lock."""
        if self._acquired:
            try:
                self.lock_path.unlink()
            except FileNotFoundError:
                pass
            self._acquired = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False