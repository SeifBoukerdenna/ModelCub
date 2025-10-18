"""UI server command."""
import click
import sys
import subprocess
import multiprocessing
import os
from pathlib import Path


def run_api(host: str, port: int) -> None:
    """Run FastAPI server in separate process."""
    from modelcub.ui.backend.main import run_server
    run_server(host=host, port=port, reload=False)


def run_dev_mode(host: str, port: int) -> None:
    """Run in development mode (separate Vite + FastAPI servers)."""
    frontend_dir = Path(__file__).parent.parent / "ui" / "frontend"

    working_dir = os.environ.get("MODELCUB_WORKING_DIR", str(Path.cwd()))

    if not frontend_dir.exists():
        click.echo("❌ Frontend directory not found", err=True)
        raise SystemExit(1)

    # Check if node_modules exists
    if not (frontend_dir / "node_modules").exists():
        click.echo("📦 Installing frontend dependencies...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                check=True
            )
        except subprocess.CalledProcessError:
            click.echo("❌ Failed to install dependencies", err=True)
            raise SystemExit(1)

    click.echo(f"📁 Working directory: {working_dir}")

    # Start FastAPI in separate process (NOT daemon)
    api_process = multiprocessing.Process(
        target=run_api,
        args=(host, port),
        daemon=False
    )
    api_process.start()

    try:
        # Start Vite dev server (blocking)
        subprocess.run(["npm", "run", "dev"], cwd=frontend_dir, check=True)
    except KeyboardInterrupt:
        click.echo("\n👋 Shutting down...")
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Vite failed: {e}", err=True)
    finally:
        # Gracefully terminate API process
        if api_process.is_alive():
            api_process.terminate()
            api_process.join(timeout=5)
            if api_process.is_alive():
                api_process.kill()


def run_production_mode(host: str, port: int) -> None:
    """Run in production mode (serve built UI from FastAPI)."""
    working_dir = os.environ.get("MODELCUB_WORKING_DIR", str(Path.cwd()))

    from modelcub.ui.backend.main import run_server

    # Check if UI is built
    ui_build = Path(__file__).parent.parent / "ui" / "frontend" / "dist"
    if not ui_build.exists():
        click.echo(
            "❌ Frontend not built. Build it first:\n"
            "   cd src/modelcub/ui/frontend && npm run build\n"
            "   Or use --dev flag for development mode.",
            err=True
        )
        raise SystemExit(1)

    click.echo(f"📁 Working directory: {working_dir}")
    run_server(host=host, port=port, reload=False)


@click.command()
@click.option('--dev', is_flag=True, help='Run in development mode')
@click.option('--port', '-p', type=int, default=8000, help='Server port')
@click.option('--host', default='127.0.0.1', help='Server host')
def ui(dev: bool, port: int, host: str):
    """Launch the ModelCub web UI."""
    # Set working directory in environment
    os.environ["MODELCUB_WORKING_DIR"] = str(Path.cwd())

    if dev:
        click.echo("🚀 Starting ModelCub UI in development mode...")
        click.echo(f"   API: http://{host}:{port}")
        click.echo(f"   UI:  http://localhost:3000")
        click.echo()
        run_dev_mode(host, port)
    else:
        click.echo(f"🚀 Starting ModelCub UI at http://{host}:{port}")
        run_production_mode(host, port)

    raise SystemExit(0)