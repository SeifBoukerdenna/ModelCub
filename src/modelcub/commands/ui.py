"""UI server commands."""
import sys
import subprocess
import multiprocessing
from pathlib import Path
from typing import NoReturn


def run_api(host: str, port: int) -> None:
    """Run FastAPI server in separate process."""
    from modelcub.api.main import run_server
    # Don't use reload in multiprocess context - causes daemon issues
    run_server(host=host, port=port, reload=False)


def run_dev_mode(host: str, port: int) -> None:
    """Run in development mode (separate Vite + FastAPI servers)."""
    ui_dir = Path(__file__).parent.parent / "ui"

    if not ui_dir.exists():
        print("❌ UI directory not found", file=sys.stderr)
        sys.exit(1)

    # Check if node_modules exists
    if not (ui_dir / "node_modules").exists():
        print("📦 Installing UI dependencies...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=ui_dir,
                check=True
            )
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies", file=sys.stderr)
            sys.exit(1)

    # Start FastAPI in separate process (NOT daemon)
    api_process = multiprocessing.Process(
        target=run_api,
        args=(host, port),
        daemon=False  # Changed to False to avoid daemon issue
    )
    api_process.start()

    try:
        # Start Vite dev server (blocking)
        subprocess.run(["npm", "run", "dev"], cwd=ui_dir, check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Vite failed: {e}", file=sys.stderr)
    finally:
        # Gracefully terminate API process
        if api_process.is_alive():
            api_process.terminate()
            api_process.join(timeout=5)
            if api_process.is_alive():
                api_process.kill()


def run_production_mode(host: str, port: int) -> NoReturn:
    """Run in production mode (serve built UI from FastAPI)."""
    from modelcub.api.main import run_server

    # Check if UI is built
    ui_build = Path(__file__).parent.parent / "api" / "static"
    if not ui_build.exists():
        print(
            "❌ UI not built. Build it first:\n"
            "   cd src/modelcub/ui && npm run build\n"
            "   Or use --dev flag for development mode.",
            file=sys.stderr
        )
        sys.exit(1)

    run_server(host=host, port=port, reload=False)


def run(args) -> int:
    """Run UI command with argparse args."""
    host = args.host
    port = args.port
    dev = args.dev

    if dev:
        print("🚀 Starting ModelCub UI in development mode...")
        print(f"   API: http://{host}:{port}")
        print(f"   UI:  http://localhost:3000")
        print()
        run_dev_mode(host, port)
    else:
        print(f"🚀 Starting ModelCub UI at http://{host}:{port}")
        run_production_mode(host, port)

    return 0