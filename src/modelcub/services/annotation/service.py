# src/modelcub/services/annotation/service.py
"""
Main annotation service that orchestrates all components.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List

from .models import ImageAnnotation, ImageInfo
from .storage import AnnotationStorage
from .image_handler import ImageHandler
from .exporters import ExportManager
from .config import ConfigManager
from .class_manager import ClassManager
from .shortcuts import ShortcutManager
from .app import create_app


class AnnotationService:
    """
    Main service for the annotation studio.
    Orchestrates storage, image handling, exports, and the web interface.
    """

    def __init__(self, data_dir: Path, output_dir: Path, port: int = 8000):
        """
        Initialize the annotation service.

        Args:
            data_dir: Directory containing images to annotate
            output_dir: Directory where annotations will be saved
            port: Port for the web server
        """
        self.data_dir = Path(data_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.port = port

        # Initialize components
        self.storage = AnnotationStorage(self.output_dir)
        self.image_handler = ImageHandler(self.data_dir)
        self.config = ConfigManager()
        self.class_manager = ClassManager()
        self.shortcut_manager = ShortcutManager()

        # Load data
        self.classes = self.class_manager.get_classes()
        self.annotations = self.storage.load_all()
        self.images = self.image_handler.discover_images(self.annotations)

        # Initialize export manager
        self.export_manager = ExportManager(self.classes)

        # Create Flask app
        self.app = create_app(
            data_dir=self.data_dir,
            output_dir=self.output_dir,
            storage=self.storage,
            image_handler=self.image_handler,
            export_manager=self.export_manager,
            class_manager=self.class_manager,
            shortcut_manager=self.shortcut_manager,
            classes=self.classes,
            images=self.images,
            annotations=self.annotations
        )

    def run(self, debug: bool = False) -> None:
        """
        Run the annotation service web server.

        Args:
            debug: Enable Flask debug mode
        """
        self._print_startup_banner()
        self.app.run(host='0.0.0.0', port=self.port, debug=debug)

    def _print_startup_banner(self) -> None:
        """Print startup information."""
        print(f"\n{'='*60}")
        print(f"🎨 ModelCub Annotation Studio")
        print(f"{'='*60}")
        print(f"📁 Data directory:     {self.data_dir}")
        print(f"💾 Output directory:   {self.output_dir}")
        print(f"🖼️  Images found:       {len(self.images)}")
        print(f"🏷️  Classes:            {', '.join(self.classes)}")
        print(f"{'='*60}")
        print(f"\n🌐 Annotation Studio running at:")
        print(f"\n   👉  http://localhost:{self.port}  👈\n")
        print(f"{'='*60}")
        print(f"💡 Tips:")
        print(f"   • Open the URL above in your browser")
        print(f"   • Press ? in the UI to see keyboard shortcuts")
        print(f"   • Click '⚙️ Manage Classes' to add/edit classes")
        print(f"   • Press Ctrl+C to stop the server")
        print(f"{'='*60}\n")

    def get_statistics(self) -> dict:
        """
        Get current annotation statistics.

        Returns:
            Dictionary with annotation statistics
        """
        total_images = len(self.images)
        annotated_images = len(self.annotations)
        total_annotations = sum(
            len(img_ann.annotations)
            for img_ann in self.annotations.values()
        )

        class_counts = {}
        for img_ann in self.annotations.values():
            for ann in img_ann.annotations:
                class_counts[ann.label] = class_counts.get(ann.label, 0) + 1

        return {
            'total_images': total_images,
            'annotated_images': annotated_images,
            'total_annotations': total_annotations,
            'class_distribution': class_counts,
            'completion_rate': (
                (annotated_images / total_images * 100)
                if total_images > 0 else 0
            )
        }