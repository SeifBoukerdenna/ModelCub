"""
Process management for training subprocesses.

Handles spawning, monitoring, and terminating training processes
with OS-specific signal handling.
"""

import os
import sys
import signal
import subprocess
import psutil
from pathlib import Path
from typing import Optional, Dict, Any


def spawn_training(
    command: list[str],
    cwd: Path,
    stdout_path: Path,
    stderr_path: Path,
    env: Optional[Dict[str, str]] = None
) -> int:
    """
    Spawn training process as subprocess.

    Args:
        command: Command to execute (e.g., ['python', 'train.py', ...])
        cwd: Working directory
        stdout_path: Path to stdout log file
        stderr_path: Path to stderr log file
        env: Additional environment variables

    Returns:
        Process ID (PID)

    Raises:
        RuntimeError: If process spawn fails
    """
    # Ensure log directory exists
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)

    # Prepare environment
    process_env = os.environ.copy()
    if env:
        process_env.update(env)

    try:
        with open(stdout_path, 'w') as stdout_f, open(stderr_path, 'w') as stderr_f:
            process = subprocess.Popen(
                command,
                cwd=str(cwd),
                stdout=stdout_f,
                stderr=stderr_f,
                env=process_env,
                # Detach from parent (platform-specific)
                start_new_session=True if sys.platform != 'win32' else False,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )

        return process.pid

    except Exception as e:
        raise RuntimeError(f"Failed to spawn training process: {e}")


def is_process_alive(pid: int) -> bool:
    """
    Check if process with given PID is still running.

    Args:
        pid: Process ID

    Returns:
        True if process exists and is running
    """
    try:
        process = psutil.Process(pid)
        return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def terminate_process(pid: int, timeout: float = 10.0) -> bool:
    """
    Gracefully terminate process with SIGTERM, then SIGKILL if needed.

    Args:
        pid: Process ID to terminate
        timeout: Seconds to wait for graceful shutdown before force kill

    Returns:
        True if process was terminated successfully

    Raises:
        ProcessLookupError: If process doesn't exist
    """
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        raise ProcessLookupError(f"Process {pid} not found")

    # Try graceful termination first
    try:
        if sys.platform == 'win32':
            # Windows: terminate entire process tree
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)

            # Terminate children first
            for child in children:
                try:
                    child.terminate()
                except psutil.NoSuchProcess:
                    pass

            parent.terminate()

        else:
            # Unix: send SIGTERM
            process.terminate()

        # Wait for graceful shutdown
        process.wait(timeout=timeout)
        return True

    except psutil.TimeoutExpired:
        # Force kill if graceful termination fails
        try:
            if sys.platform == 'win32':
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)

                for child in children:
                    try:
                        child.kill()
                    except psutil.NoSuchProcess:
                        pass

                parent.kill()
            else:
                process.kill()

            process.wait(timeout=5.0)
            return True

        except Exception as e:
            raise RuntimeError(f"Failed to kill process {pid}: {e}")

    except psutil.NoSuchProcess:
        # Process already dead
        return True


def get_process_info(pid: int) -> Dict[str, Any]:
    """
    Get information about running process.

    Args:
        pid: Process ID

    Returns:
        Dictionary with process info (status, cpu_percent, memory_mb, runtime_seconds)

    Raises:
        ProcessLookupError: If process doesn't exist
    """
    try:
        process = psutil.Process(pid)

        with process.oneshot():
            info = {
                'pid': pid,
                'status': process.status(),
                'cpu_percent': process.cpu_percent(interval=0.1),
                'memory_mb': process.memory_info().rss / (1024 * 1024),
                'runtime_seconds': None,
                'command': ' '.join(process.cmdline())
            }

            # Calculate runtime if process has create_time
            try:
                import time
                create_time = process.create_time()
                info['runtime_seconds'] = time.time() - create_time
            except:
                pass

            return info

    except psutil.NoSuchProcess:
        raise ProcessLookupError(f"Process {pid} not found")