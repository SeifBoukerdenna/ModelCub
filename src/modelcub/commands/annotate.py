# src/modelcub/commands/annotate.py
from __future__ import annotations
import json
import os
import sys
import webbrowser
from pathlib import Path
from typing import Optional
import threading
import time

def run(args):
    """Launch the annotation web interface."""
    from ..services.annotation_service import AnnotationService

    port = getattr(args, 'port', 8000)
    data_dir = getattr(args, 'data_dir', 'data')
    output_dir = getattr(args, 'output_dir', 'data/labels')
    auto_open = getattr(args, 'no_browser', False) == False

    # Check if we're in a project
    if not Path('modelcub.yaml').exists():
        print("Error: Not in a ModelCub project directory (no modelcub.yaml found)")
        return 1

    # Initialize the annotation service
    service = AnnotationService(
        data_dir=Path(data_dir),
        output_dir=Path(output_dir),
        port=port
    )

    # Start the server in a separate thread if auto-opening browser
    if auto_open:
        server_thread = threading.Thread(target=service.run, kwargs={'debug': False})
        server_thread.daemon = True
        server_thread.start()

        # Wait a moment for server to start
        time.sleep(1.5)

        # Open browser
        url = f"http://localhost:{port}"
        print(f"Opening browser at {url}")
        webbrowser.open(url)

        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down annotation server...")
            return 0
    else:
        # Run server directly
        service.run(debug=False)

    return 0