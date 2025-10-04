# src/modelcub/services/annotation/app.py
"""
Flask application factory for annotation service.
"""
from __future__ import annotations
import os
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Dict, List

try:
    from flask import Flask, render_template, jsonify, request, send_file, Response
    from flask_cors import CORS
except ImportError:
    print("Flask not installed. Run: pip install flask flask-cors")
    raise

from .models import Annotation, ImageAnnotation, ImageInfo
from .storage import AnnotationStorage
from .image_handler import ImageHandler
from .exporters import ExportManager
from .config import ConfigManager
from .class_manager import ClassManager
from .shortcuts import ShortcutManager


def create_app(data_dir: Path, output_dir: Path,
               storage: AnnotationStorage,
               image_handler: ImageHandler,
               export_manager: ExportManager,
               class_manager: ClassManager,
               shortcut_manager: ShortcutManager,
               classes: List[str],
               images: List[ImageInfo],
               annotations: Dict[str, ImageAnnotation]) -> Flask:
    """
    Create and configure Flask application.

    Args:
        data_dir: Directory containing images
        output_dir: Directory for saving annotations
        storage: Annotation storage instance
        image_handler: Image handler instance
        export_manager: Export manager instance
        classes: List of annotation classes
        images: List of discovered images
        annotations: Dictionary of current annotations

    Returns:
        Configured Flask app
    """
    # Set template and static folders relative to this file
    template_folder = Path(__file__).parent / 'templates'
    static_folder = Path(__file__).parent / 'static'

    app = Flask(__name__,
                template_folder=str(template_folder),
                static_folder=str(static_folder))
    CORS(app)

    # Store instances for access in routes
    app.config['DATA_DIR'] = data_dir
    app.config['OUTPUT_DIR'] = output_dir
    app.config['STORAGE'] = storage
    app.config['IMAGE_HANDLER'] = image_handler
    app.config['EXPORT_MANAGER'] = export_manager
    app.config['CLASS_MANAGER'] = class_manager
    app.config['SHORTCUT_MANAGER'] = shortcut_manager
    app.config['CLASSES'] = classes
    app.config['IMAGES'] = images
    app.config['ANNOTATIONS'] = annotations

    # Register routes
    _register_routes(app)

    return app


def _register_routes(app: Flask) -> None:
    """Register all Flask routes."""

    @app.route('/')
    def index():
        """Serve the main annotation interface."""
        return render_template('index.html')

    @app.route('/api/images')
    def get_images():
        """Get list of all images."""
        images = app.config['IMAGES']
        return jsonify([img.to_dict() for img in images])

    @app.route('/api/classes')
    def get_classes():
        """Get list of annotation classes."""
        return jsonify(app.config['CLASSES'])

    @app.route('/api/image/<path:image_id>')
    def get_image(image_id):
        """Serve an image file."""
        images = app.config['IMAGES']
        image_handler = app.config['IMAGE_HANDLER']

        img_info = image_handler.find_image_by_id(image_id, images)
        if not img_info:
            print(f"Image ID not found in list: {image_id}")
            return jsonify({'error': 'Image not found'}), 404

        img_path = Path(img_info.path)

        # Debug logging
        print(f"Requesting image: {image_id}")
        print(f"Image path: {img_path}")
        print(f"Path exists: {img_path.exists()}")

        if not img_path.exists():
            print(f"Image file not found: {img_path}")
            return jsonify({'error': 'Image file not found'}), 404

        try:
            return send_file(
                str(img_path),
                mimetype=mimetypes.guess_type(str(img_path))[0] or 'image/jpeg',
                as_attachment=False
            )
        except Exception as e:
            print(f"Error serving image {img_path}: {e}")
            # Fallback: try reading as bytes
            try:
                with open(img_path, 'rb') as f:
                    image_data = f.read()
                return Response(
                    image_data,
                    mimetype=mimetypes.guess_type(str(img_path))[0] or 'image/jpeg'
                )
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                return jsonify({'error': f'Cannot read image: {str(e2)}'}), 500

    @app.route('/api/annotations/<path:image_id>', methods=['GET'])
    def get_annotations(image_id):
        """Get annotations for a specific image."""
        annotations = app.config['ANNOTATIONS']
        storage = app.config['STORAGE']

        img_ann = storage.get(image_id, annotations)
        if img_ann:
            return jsonify({
                'annotations': [ann.to_dict() for ann in img_ann.annotations]
            })
        return jsonify({'annotations': []})

    @app.route('/api/annotations/<path:image_id>', methods=['POST'])
    def save_annotations(image_id):
        """Save annotations for a specific image."""
        data = request.json
        images = app.config['IMAGES']
        annotations = app.config['ANNOTATIONS']
        storage = app.config['STORAGE']
        image_handler = app.config['IMAGE_HANDLER']

        # Find image info
        img_info = image_handler.find_image_by_id(image_id, images)
        if not img_info:
            return jsonify({'error': 'Image not found'}), 404

        # Create or update annotation
        annotation_objects = []
        for ann_data in data.get('annotations', []):
            annotation_objects.append(Annotation.from_dict(ann_data))

        img_annotation = ImageAnnotation(
            image_path=img_info.path,
            image_id=image_id,
            width=data.get('width', 0),
            height=data.get('height', 0),
            annotations=annotation_objects,
            timestamp=datetime.now().isoformat(),
            annotator='modelcub'
        )

        # Save to disk
        storage.save_one(image_id, img_annotation, annotations)

        # Update has_annotations flag
        has_annotations = len(annotation_objects) > 0
        image_handler.update_annotation_status(image_id, has_annotations, images)

        return jsonify({'success': True})

    @app.route('/api/export/<format>')
    def export_annotations(format):
        """Export annotations in different formats."""
        annotations = app.config['ANNOTATIONS']
        export_manager = app.config['EXPORT_MANAGER']

        data, status, headers = export_manager.export(format, annotations)

        if isinstance(data, dict) and 'error' in data:
            return jsonify(data), status

        if format == 'coco':
            return jsonify(data), status
        else:
            return data, status, headers

    @app.route('/api/stats')
    def get_stats():
        """Get annotation statistics."""
        images = app.config['IMAGES']
        annotations = app.config['ANNOTATIONS']

        total_images = len(images)
        annotated_images = len(annotations)
        total_annotations = sum(
            len(img_ann.annotations)
            for img_ann in annotations.values()
        )

        class_counts = {}
        for img_ann in annotations.values():
            for ann in img_ann.annotations:
                class_counts[ann.label] = class_counts.get(ann.label, 0) + 1

        return jsonify({
            'total_images': total_images,
            'annotated_images': annotated_images,
            'total_annotations': total_annotations,
            'class_distribution': class_counts,
            'completion_rate': (
                (annotated_images / total_images * 100)
                if total_images > 0 else 0
            )
        })

    @app.route('/api/debug')
    def debug_info():
        """Debug endpoint to check paths and configuration."""
        data_dir = app.config['DATA_DIR']
        output_dir = app.config['OUTPUT_DIR']
        images = app.config['IMAGES']
        classes = app.config['CLASSES']

        return jsonify({
            'data_dir': str(data_dir),
            'output_dir': str(output_dir),
            'num_images': len(images),
            'first_5_images': [img.to_dict() for img in images[:5]],
            'classes': classes,
            'cwd': os.getcwd()
        })

    # Class Management Routes
    @app.route('/api/classes', methods=['POST'])
    def add_class():
        """Add a new class."""
        data = request.json
        class_name = data.get('name', '').strip()

        if not class_name:
            return jsonify({'error': 'Class name required'}), 400

        class_manager = app.config['CLASS_MANAGER']
        if class_manager.add_class(class_name):
            # Update app config
            app.config['CLASSES'] = class_manager.get_classes()
            return jsonify({
                'success': True,
                'classes': class_manager.get_classes()
            })
        else:
            return jsonify({'error': 'Class already exists or invalid'}), 400

    @app.route('/api/classes/<class_name>', methods=['DELETE'])
    def remove_class(class_name):
        """Remove a class."""
        class_manager = app.config['CLASS_MANAGER']
        if class_manager.remove_class(class_name):
            app.config['CLASSES'] = class_manager.get_classes()
            return jsonify({
                'success': True,
                'classes': class_manager.get_classes()
            })
        else:
            return jsonify({'error': 'Class not found'}), 404

    @app.route('/api/classes/<class_name>', methods=['PUT'])
    def rename_class(class_name):
        """Rename a class."""
        data = request.json
        new_name = data.get('new_name', '').strip()

        if not new_name:
            return jsonify({'error': 'New name required'}), 400

        class_manager = app.config['CLASS_MANAGER']
        if class_manager.rename_class(class_name, new_name):
            app.config['CLASSES'] = class_manager.get_classes()
            return jsonify({
                'success': True,
                'classes': class_manager.get_classes()
            })
        else:
            return jsonify({'error': 'Could not rename class'}), 400

    @app.route('/api/classes/reorder', methods=['POST'])
    def reorder_classes():
        """Reorder classes."""
        data = request.json
        new_order = data.get('classes', [])

        class_manager = app.config['CLASS_MANAGER']
        if class_manager.reorder_classes(new_order):
            app.config['CLASSES'] = class_manager.get_classes()
            return jsonify({
                'success': True,
                'classes': class_manager.get_classes()
            })
        else:
            return jsonify({'error': 'Invalid class order'}), 400

    @app.route('/api/classes/reload', methods=['POST'])
    def reload_classes():
        """Reload classes from YAML (external changes)."""
        class_manager = app.config['CLASS_MANAGER']
        classes = class_manager.reload()
        app.config['CLASSES'] = classes
        return jsonify({
            'success': True,
            'classes': classes
        })

    # Shortcut Routes
    @app.route('/api/shortcuts')
    def get_shortcuts():
        """Get all keyboard shortcuts."""
        shortcut_manager = app.config['SHORTCUT_MANAGER']
        return jsonify(shortcut_manager.get_shortcuts_by_category())

    @app.route('/api/shortcuts/reset', methods=['POST'])
    def reset_shortcuts():
        """Reset shortcuts to defaults."""
        shortcut_manager = app.config['SHORTCUT_MANAGER']
        shortcut_manager.reset_to_defaults()
        return jsonify({
            'success': True,
            'shortcuts': shortcut_manager.get_shortcuts()
        })