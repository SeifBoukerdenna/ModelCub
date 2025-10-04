# src/modelcub/services/annotation_service_fixed.py
from __future__ import annotations
import json
import base64
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import mimetypes

try:
    from flask import Flask, render_template_string, jsonify, request, send_file, Response
    from flask_cors import CORS
except ImportError:
    print("Flask not installed. Run: pip install flask flask-cors")
    raise

@dataclass
class Annotation:
    """Represents a single annotation (bounding box, polygon, etc.)"""
    id: str
    type: str  # 'bbox', 'polygon', 'point', 'line'
    label: str
    points: List[List[float]]  # [[x1,y1], [x2,y2], ...]
    confidence: float = 1.0
    metadata: Dict = None

@dataclass
class ImageAnnotation:
    """Complete annotation for an image"""
    image_path: str
    image_id: str
    width: int
    height: int
    annotations: List[Annotation]
    timestamp: str
    annotator: str = "modelcub"

class AnnotationService:
    def __init__(self, data_dir: Path, output_dir: Path, port: int = 8000):
        self.data_dir = Path(data_dir).resolve()  # Use absolute path
        self.output_dir = Path(output_dir).resolve()
        self.port = port

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load existing annotations
        self.annotations_file = self.output_dir / "annotations.json"
        self.annotations = self._load_annotations()

        # Get list of images
        self.images = self._discover_images()

        # Load classes from modelcub.yaml
        self.classes = self._load_classes()

        # Initialize Flask app
        self.app = Flask(__name__)
        CORS(self.app)
        self._setup_routes()

    def _discover_images(self) -> List[Dict]:
        """Find all images in data directory and subdirectories."""
        images = []
        extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}

        print(f"Searching for images in: {self.data_dir}")

        for img_path in sorted(self.data_dir.rglob('*')):
            if img_path.is_file() and img_path.suffix.lower() in extensions:
                rel_path = img_path.relative_to(self.data_dir)
                img_id = str(rel_path).replace('\\', '/')

                images.append({
                    'id': img_id,
                    'path': str(img_path.resolve()),  # Store absolute path
                    'name': img_path.name,
                    'relative_path': str(rel_path),
                    'has_annotations': img_id in self.annotations
                })

        print(f"Found {len(images)} images")
        if images:
            print(f"First image: {images[0]['path']}")

        return images

    def _load_classes(self) -> List[str]:
        """Load classes from modelcub.yaml."""
        yaml_path = Path('modelcub.yaml')
        if yaml_path.exists():
            content = yaml_path.read_text()
            for line in content.splitlines():
                if line.strip().startswith('classes:'):
                    # Parse the classes list
                    classes_str = line.split(':', 1)[1].strip()
                    if classes_str.startswith('[') and classes_str.endswith(']'):
                        classes = [c.strip() for c in classes_str[1:-1].split(',')]
                        return [c for c in classes if c]
        return ['object']  # Default

    def _load_annotations(self) -> Dict[str, ImageAnnotation]:
        """Load existing annotations from JSON."""
        if self.annotations_file.exists():
            try:
                with open(self.annotations_file, 'r') as f:
                    data = json.load(f)
                    annotations = {}
                    for img_id, img_data in data.items():
                        # Convert annotation dicts back to Annotation objects
                        ann_objects = []
                        for ann in img_data.get('annotations', []):
                            ann_objects.append(Annotation(
                                id=ann['id'],
                                type=ann['type'],
                                label=ann['label'],
                                points=ann['points'],
                                confidence=ann.get('confidence', 1.0),
                                metadata=ann.get('metadata')
                            ))

                        annotations[img_id] = ImageAnnotation(
                            image_path=img_data['image_path'],
                            image_id=img_data['image_id'],
                            width=img_data['width'],
                            height=img_data['height'],
                            annotations=ann_objects,
                            timestamp=img_data['timestamp'],
                            annotator=img_data.get('annotator', 'modelcub')
                        )
                    return annotations
            except Exception as e:
                print(f"Warning: Could not load annotations: {e}")
        return {}

    def _save_annotations(self):
        """Save annotations to JSON."""
        data = {}
        for img_id, img_ann in self.annotations.items():
            data[img_id] = {
                'image_path': img_ann.image_path,
                'image_id': img_ann.image_id,
                'width': img_ann.width,
                'height': img_ann.height,
                'timestamp': img_ann.timestamp,
                'annotator': img_ann.annotator,
                'annotations': [
                    {
                        'id': ann.id,
                        'type': ann.type,
                        'label': ann.label,
                        'points': ann.points,
                        'confidence': ann.confidence,
                        'metadata': ann.metadata or {}
                    }
                    for ann in img_ann.annotations
                ]
            }

        with open(self.annotations_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _setup_routes(self):
        """Setup Flask routes."""

        @self.app.route('/')
        def index():
            return render_template_string(ANNOTATION_UI_TEMPLATE)

        @self.app.route('/api/images')
        def get_images():
            return jsonify(self.images)

        @self.app.route('/api/classes')
        def get_classes():
            return jsonify(self.classes)

        @self.app.route('/api/image/<path:image_id>')
        def get_image(image_id):
            """Serve image file with proper error handling."""
            # Find the image
            for img in self.images:
                if img['id'] == image_id:
                    img_path = Path(img['path'])

                    # Debug logging
                    print(f"Requesting image: {image_id}")
                    print(f"Image path: {img_path}")
                    print(f"Path exists: {img_path.exists()}")

                    if img_path.exists():
                        try:
                            # Try to read and serve the image
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
                    else:
                        print(f"Image file not found: {img_path}")
                        return jsonify({'error': 'Image file not found'}), 404

            print(f"Image ID not found in list: {image_id}")
            return jsonify({'error': 'Image not found'}), 404

        @self.app.route('/api/annotations/<path:image_id>', methods=['GET'])
        def get_annotations(image_id):
            if image_id in self.annotations:
                ann = self.annotations[image_id]
                return jsonify({
                    'annotations': [
                        {
                            'id': a.id,
                            'type': a.type,
                            'label': a.label,
                            'points': a.points,
                            'confidence': a.confidence,
                            'metadata': a.metadata
                        }
                        for a in ann.annotations
                    ]
                })
            return jsonify({'annotations': []})

        @self.app.route('/api/annotations/<path:image_id>', methods=['POST'])
        def save_annotations(image_id):
            data = request.json

            # Find image info
            img_info = None
            for img in self.images:
                if img['id'] == image_id:
                    img_info = img
                    break

            if not img_info:
                return jsonify({'error': 'Image not found'}), 404

            # Create or update annotation
            annotations = []
            for ann_data in data.get('annotations', []):
                annotations.append(Annotation(
                    id=ann_data['id'],
                    type=ann_data['type'],
                    label=ann_data['label'],
                    points=ann_data['points'],
                    confidence=ann_data.get('confidence', 1.0),
                    metadata=ann_data.get('metadata')
                ))

            self.annotations[image_id] = ImageAnnotation(
                image_path=img_info['path'],
                image_id=image_id,
                width=data.get('width', 0),
                height=data.get('height', 0),
                annotations=annotations,
                timestamp=datetime.now().isoformat(),
                annotator='modelcub'
            )

            # Save to disk
            self._save_annotations()

            # Update has_annotations flag
            img_info['has_annotations'] = len(annotations) > 0

            return jsonify({'success': True})

        @self.app.route('/api/export/<format>')
        def export_annotations(format):
            """Export annotations in different formats."""
            if format == 'yolo':
                return self._export_yolo()
            elif format == 'coco':
                return self._export_coco()
            elif format == 'voc':
                return self._export_voc()
            else:
                return jsonify({'error': f'Unknown format: {format}'}), 400

        @self.app.route('/api/stats')
        def get_stats():
            """Get annotation statistics."""
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

            return jsonify({
                'total_images': total_images,
                'annotated_images': annotated_images,
                'total_annotations': total_annotations,
                'class_distribution': class_counts,
                'completion_rate': (annotated_images / total_images * 100) if total_images > 0 else 0
            })

        @self.app.route('/api/debug')
        def debug_info():
            """Debug endpoint to check paths."""
            return jsonify({
                'data_dir': str(self.data_dir),
                'output_dir': str(self.output_dir),
                'num_images': len(self.images),
                'first_5_images': self.images[:5] if self.images else [],
                'classes': self.classes,
                'cwd': os.getcwd()
            })

    def _export_yolo(self):
        """Export annotations in YOLO format."""
        output = []
        for img_ann in self.annotations.values():
            lines = []
            for ann in img_ann.annotations:
                if ann.type == 'bbox' and len(ann.points) == 2:
                    # Convert to YOLO format (class_id x_center y_center width height)
                    x1, y1 = ann.points[0]
                    x2, y2 = ann.points[1]

                    x_center = (x1 + x2) / 2 / img_ann.width
                    y_center = (y1 + y2) / 2 / img_ann.height
                    width = abs(x2 - x1) / img_ann.width
                    height = abs(y2 - y1) / img_ann.height

                    class_id = self.classes.index(ann.label) if ann.label in self.classes else 0
                    lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

            if lines:
                output.append(f"# {img_ann.image_id}")
                output.extend(lines)
                output.append("")

        return '\n'.join(output), 200, {'Content-Type': 'text/plain'}

    def _export_coco(self):
        """Export annotations in COCO format."""
        coco_data = {
            'images': [],
            'annotations': [],
            'categories': [
                {'id': i, 'name': cls}
                for i, cls in enumerate(self.classes)
            ]
        }

        ann_id = 0
        for img_idx, (img_id, img_ann) in enumerate(self.annotations.items()):
            # Add image
            coco_data['images'].append({
                'id': img_idx,
                'file_name': img_id,
                'width': img_ann.width,
                'height': img_ann.height
            })

            # Add annotations
            for ann in img_ann.annotations:
                if ann.type == 'bbox' and len(ann.points) == 2:
                    x1, y1 = ann.points[0]
                    x2, y2 = ann.points[1]

                    coco_data['annotations'].append({
                        'id': ann_id,
                        'image_id': img_idx,
                        'category_id': self.classes.index(ann.label) if ann.label in self.classes else 0,
                        'bbox': [x1, y1, abs(x2 - x1), abs(y2 - y1)],
                        'area': abs(x2 - x1) * abs(y2 - y1),
                        'iscrowd': 0
                    })
                    ann_id += 1

        return jsonify(coco_data)

    def _export_voc(self):
        """Export annotations in Pascal VOC XML format."""
        xml_snippets = []
        for img_ann in self.annotations.values():
            xml_snippets.append(f"<annotation for='{img_ann.image_id}'>")
            for ann in img_ann.annotations:
                if ann.type == 'bbox':
                    xml_snippets.append(f"  <object class='{ann.label}' />")
            xml_snippets.append("</annotation>")

        return '\n'.join(xml_snippets), 200, {'Content-Type': 'text/xml'}

    def run(self, debug=False):
        """Run the Flask server."""
        print(f"\n🎨 ModelCub Annotation Studio")
        print(f"{'='*50}")
        print(f"📁 Data directory: {self.data_dir}")
        print(f"💾 Output directory: {self.output_dir}")
        print(f"🖼️  Found {len(self.images)} images")
        print(f"🏷️  Classes: {', '.join(self.classes)}")
        print(f"{'='*50}")
        print(f"\n🌐 Starting server at http://localhost:{self.port}")
        print(f"🐛 Debug endpoint: http://localhost:{self.port}/api/debug")
        print(f"Press Ctrl+C to stop\n")

        self.app.run(host='0.0.0.0', port=self.port, debug=debug)


# Keep the HTML template the same but with error handling
ANNOTATION_UI_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ModelCub Annotation Studio</title>
    <style>
        /* ... (keeping all the same styles from before) ... */
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --bg: #0f172a;
            --bg-light: #1e293b;
            --bg-lighter: #334155;
            --text: #f1f5f9;
            --text-dim: #94a3b8;
            --border: #475569;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: var(--bg);
            color: var(--text);
            height: 100vh;
            overflow: hidden;
        }

        .app {
            display: flex;
            height: 100vh;
        }

        .sidebar {
            width: 280px;
            background: var(--bg-light);
            border-right: 1px solid var(--border);
            display: flex;
            flex-direction: column;
        }

        .sidebar-header {
            padding: 20px;
            border-bottom: 1px solid var(--border);
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        }

        .logo {
            font-size: 24px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .stats {
            margin-top: 15px;
            font-size: 12px;
            opacity: 0.9;
        }

        .stat-row {
            display: flex;
            justify-content: space-between;
            margin: 4px 0;
        }

        .image-list {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }

        .image-item {
            padding: 12px;
            margin: 5px 0;
            background: var(--bg-lighter);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .image-item:hover {
            background: var(--border);
            transform: translateX(5px);
        }

        .image-item.active {
            background: var(--primary);
            color: white;
        }

        .image-item-name {
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            font-size: 14px;
        }

        .annotation-badge {
            background: var(--secondary);
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: bold;
        }

        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .toolbar {
            height: 60px;
            background: var(--bg-light);
            border-bottom: 1px solid var(--border);
            display: flex;
            align-items: center;
            padding: 0 20px;
            gap: 15px;
        }

        .tool-group {
            display: flex;
            gap: 10px;
            padding: 0 15px;
            border-right: 1px solid var(--border);
        }

        .tool-group:last-child {
            border-right: none;
            margin-left: auto;
        }

        .tool-btn {
            padding: 8px 16px;
            background: var(--bg-lighter);
            border: 1px solid var(--border);
            border-radius: 6px;
            color: var(--text);
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .tool-btn:hover {
            background: var(--primary);
            border-color: var(--primary);
            transform: translateY(-2px);
        }

        .tool-btn.active {
            background: var(--primary);
            border-color: var(--primary);
        }

        .canvas-container {
            flex: 1;
            display: flex;
            position: relative;
            background: var(--bg);
            overflow: hidden;
        }

        .canvas-wrapper {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }

        #annotationCanvas {
            max-width: 100%;
            max-height: 100%;
            cursor: crosshair;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }

        .right-panel {
            width: 320px;
            background: var(--bg-light);
            border-left: 1px solid var(--border);
            padding: 20px;
            overflow-y: auto;
        }

        .panel-section {
            margin-bottom: 25px;
        }

        .panel-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 12px;
            color: var(--primary);
        }

        .class-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }

        .class-btn {
            padding: 10px;
            background: var(--bg-lighter);
            border: 2px solid var(--border);
            border-radius: 6px;
            color: var(--text);
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
            text-align: center;
        }

        .class-btn:hover {
            background: var(--primary);
            border-color: var(--primary);
        }

        .class-btn.selected {
            background: var(--primary);
            border-color: var(--primary);
        }

        .annotation-list {
            max-height: 300px;
            overflow-y: auto;
        }

        .annotation-item {
            padding: 12px;
            background: var(--bg-lighter);
            border-radius: 6px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .annotation-label {
            font-weight: 500;
            color: var(--secondary);
        }

        .delete-btn {
            padding: 4px 8px;
            background: var(--danger);
            border: none;
            border-radius: 4px;
            color: white;
            cursor: pointer;
            font-size: 12px;
        }

        .export-section {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .export-btn {
            padding: 12px;
            background: linear-gradient(135deg, var(--secondary), #059669);
            border: none;
            border-radius: 6px;
            color: white;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }

        .export-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(16, 185, 129, 0.4);
        }

        .nav-controls {
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 10px;
            background: var(--bg-light);
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.5);
        }

        .nav-btn {
            padding: 10px 20px;
            background: var(--primary);
            border: none;
            border-radius: 6px;
            color: white;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }

        .nav-btn:hover:not(:disabled) {
            background: var(--primary-dark);
            transform: translateY(-2px);
        }

        .nav-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .image-counter {
            display: flex;
            align-items: center;
            padding: 0 15px;
            color: var(--text);
            font-weight: 600;
        }

        .loading {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(15, 23, 42, 0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 3px solid var(--border);
            border-top-color: var(--primary);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .error-message {
            background: var(--danger);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 20px;
            text-align: center;
        }

        .shortcuts {
            position: fixed;
            bottom: 10px;
            right: 10px;
            padding: 10px;
            background: var(--bg-lighter);
            border-radius: 6px;
            font-size: 11px;
            opacity: 0.7;
        }
    </style>
</head>
<body>
    <div id="loadingScreen" class="loading">
        <div class="spinner"></div>
    </div>

    <div class="app">
        <div class="sidebar">
            <div class="sidebar-header">
                <div class="logo">
                    🐻 ModelCub Annotate
                </div>
                <div class="stats">
                    <div class="stat-row">
                        <span>Total Images:</span>
                        <span id="totalImages">0</span>
                    </div>
                    <div class="stat-row">
                        <span>Annotated:</span>
                        <span id="annotatedImages">0</span>
                    </div>
                    <div class="stat-row">
                        <span>Progress:</span>
                        <span id="progressPercent">0%</span>
                    </div>
                </div>
            </div>

            <div class="image-list" id="imageList">
                <!-- Image items will be added here -->
            </div>
        </div>

        <div class="main-content">
            <div class="toolbar">
                <div class="tool-group">
                    <button class="tool-btn active" data-tool="bbox" title="Bounding Box (B)">
                        ⬜ BBox
                    </button>
                    <button class="tool-btn" data-tool="polygon" title="Polygon (P)">
                        🔷 Polygon
                    </button>
                    <button class="tool-btn" data-tool="select" title="Select (S)">
                        👆 Select
                    </button>
                </div>

                <div class="tool-group">
                    <button class="tool-btn" id="undoBtn" title="Undo (Ctrl+Z)">
                        ↶ Undo
                    </button>
                    <button class="tool-btn" id="clearBtn" title="Clear All">
                        🗑️ Clear
                    </button>
                </div>

                <div class="tool-group">
                    <button class="tool-btn" id="autoSaveBtn" title="Auto-save is ON">
                        💾 Auto-save ON
                    </button>
                    <button class="tool-btn" id="gridBtn" title="Toggle Grid (G)">
                        ⊞ Grid
                    </button>
                </div>
            </div>

            <div class="canvas-container">
                <div class="canvas-wrapper">
                    <canvas id="annotationCanvas"></canvas>
                    <div id="errorMessage" style="display:none;" class="error-message"></div>
                </div>

                <div class="nav-controls">
                    <button class="nav-btn" id="prevBtn" title="Previous (←)">← Previous</button>
                    <span class="image-counter">
                        <span id="currentIndex">1</span> / <span id="totalCount">0</span>
                    </span>
                    <button class="nav-btn" id="nextBtn" title="Next (→)">Next →</button>
                </div>
            </div>
        </div>

        <div class="right-panel">
            <div class="panel-section">
                <div class="panel-title">Classes</div>
                <div class="class-grid" id="classGrid">
                    <!-- Class buttons will be added here -->
                </div>
            </div>

            <div class="panel-section">
                <div class="panel-title">Annotations</div>
                <div class="annotation-list" id="annotationList">
                    <!-- Annotation items will be added here -->
                </div>
            </div>

            <div class="panel-section">
                <div class="panel-title">Export</div>
                <div class="export-section">
                    <button class="export-btn" data-format="yolo">Export as YOLO</button>
                    <button class="export-btn" data-format="coco">Export as COCO JSON</button>
                    <button class="export-btn" data-format="voc">Export as Pascal VOC</button>
                </div>
            </div>
        </div>
    </div>

    <div class="shortcuts">
        ← → Navigate | B: BBox | P: Polygon | S: Select | G: Grid | Del: Delete | Ctrl+S: Save
    </div>

    <script>
        class AnnotationStudio {
            constructor() {
                this.canvas = document.getElementById('annotationCanvas');
                this.ctx = this.canvas.getContext('2d');

                this.images = [];
                this.currentIndex = 0;
                this.currentImage = null;
                this.annotations = [];
                this.selectedClass = null;
                this.currentTool = 'bbox';
                this.isDrawing = false;
                this.startPoint = null;
                this.currentAnnotation = null;
                this.selectedAnnotation = null;
                this.showGrid = false;
                this.autoSave = true;
                this.classes = [];

                this.init();
            }

            async init() {
                try {
                    // First check debug info
                    const debugResponse = await fetch('/api/debug');
                    const debugInfo = await debugResponse.json();
                    console.log('Debug info:', debugInfo);

                    await this.loadImages();
                    await this.loadClasses();
                    this.setupEventListeners();
                    this.setupKeyboardShortcuts();

                    if (this.images.length > 0) {
                        await this.loadImage(0);
                    } else {
                        this.showError('No images found in data directory');
                    }
                } catch (error) {
                    console.error('Initialization error:', error);
                    this.showError('Failed to initialize: ' + error.message);
                } finally {
                    document.getElementById('loadingScreen').style.display = 'none';
                }
            }

            showError(message) {
                const errorDiv = document.getElementById('errorMessage');
                if (!errorDiv) {
                    const canvas = document.getElementById('annotationCanvas');
                    canvas.style.display = 'none';
                    const wrapper = canvas.parentElement;
                    const error = document.createElement('div');
                    error.className = 'error-message';
                    error.textContent = message;
                    wrapper.appendChild(error);
                } else {
                    errorDiv.textContent = message;
                    errorDiv.style.display = 'block';
                }
            }

            async loadImages() {
                try {
                    const response = await fetch('/api/images');
                    if (!response.ok) {
                        throw new Error('Failed to load images: ' + response.statusText);
                    }

                    this.images = await response.json();
                    console.log('Loaded images:', this.images.length);

                    // Update UI
                    document.getElementById('totalImages').textContent = this.images.length;
                    document.getElementById('totalCount').textContent = this.images.length;

                    // Populate image list
                    const imageList = document.getElementById('imageList');
                    imageList.innerHTML = '';

                    this.images.forEach((img, index) => {
                        const item = document.createElement('div');
                        item.className = 'image-item';
                        item.dataset.index = index;

                        const name = document.createElement('div');
                        name.className = 'image-item-name';
                        name.textContent = img.name;
                        item.appendChild(name);

                        if (img.has_annotations) {
                            const badge = document.createElement('div');
                            badge.className = 'annotation-badge';
                            badge.textContent = '✓';
                            item.appendChild(badge);
                        }

                        item.addEventListener('click', () => this.loadImage(index));
                        imageList.appendChild(item);
                    });

                    await this.updateStats();
                } catch (error) {
                    console.error('Failed to load images:', error);
                    this.showError('Failed to load images: ' + error.message);
                }
            }

            async loadClasses() {
                try {
                    const response = await fetch('/api/classes');
                    this.classes = await response.json();

                    // Populate class grid
                    const classGrid = document.getElementById('classGrid');
                    classGrid.innerHTML = '';

                    this.classes.forEach(cls => {
                        const btn = document.createElement('button');
                        btn.className = 'class-btn';
                        btn.textContent = cls;
                        btn.addEventListener('click', () => this.selectClass(cls, btn));
                        classGrid.appendChild(btn);
                    });

                    // Select first class by default
                    if (this.classes.length > 0) {
                        const firstBtn = classGrid.querySelector('.class-btn');
                        this.selectClass(this.classes[0], firstBtn);
                    }
                } catch (error) {
                    console.error('Failed to load classes:', error);
                    // Use default class
                    this.classes = ['object'];
                }
            }

            selectClass(cls, btn) {
                this.selectedClass = cls;
                document.querySelectorAll('.class-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
            }

            async loadImage(index) {
                if (index < 0 || index >= this.images.length) return;

                // Save current annotations if auto-save is on
                if (this.autoSave && this.currentImage) {
                    await this.saveAnnotations();
                }

                this.currentIndex = index;
                const imageData = this.images[index];

                console.log('Loading image:', imageData);

                // Update sidebar
                document.querySelectorAll('.image-item').forEach(item => {
                    item.classList.toggle('active', parseInt(item.dataset.index) === index);
                });

                // Load image with better error handling
                const img = new Image();
                img.crossOrigin = 'anonymous';  // Handle CORS if needed

                img.onload = () => {
                    console.log('Image loaded successfully');
                    this.currentImage = img;
                    this.resizeCanvas();
                    this.render();

                    // Load annotations for this image
                    this.loadAnnotations(imageData.id);
                };

                img.onerror = (error) => {
                    console.error('Failed to load image:', error);
                    this.showError(`Failed to load image: ${imageData.name}`);
                };

                // Build the image URL
                const imageUrl = `/api/image/${encodeURIComponent(imageData.id)}`;
                console.log('Image URL:', imageUrl);
                img.src = imageUrl;

                // Update navigation
                document.getElementById('currentIndex').textContent = index + 1;
                document.getElementById('prevBtn').disabled = index === 0;
                document.getElementById('nextBtn').disabled = index === this.images.length - 1;
            }

            async loadAnnotations(imageId) {
                try {
                    const response = await fetch(`/api/annotations/${encodeURIComponent(imageId)}`);
                    const data = await response.json();
                    this.annotations = data.annotations || [];
                    this.updateAnnotationList();
                    this.render();
                } catch (error) {
                    console.error('Failed to load annotations:', error);
                    this.annotations = [];
                }
            }

            async saveAnnotations() {
                if (this.currentIndex >= this.images.length) return;

                const imageData = this.images[this.currentIndex];

                try {
                    const response = await fetch(`/api/annotations/${encodeURIComponent(imageData.id)}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            annotations: this.annotations,
                            width: this.canvas.width,
                            height: this.canvas.height
                        })
                    });

                    if (!response.ok) {
                        throw new Error('Failed to save annotations');
                    }

                    // Update has_annotations flag
                    imageData.has_annotations = this.annotations.length > 0;

                    // Update sidebar badge
                    const item = document.querySelector(`.image-item[data-index="${this.currentIndex}"]`);
                    if (item) {
                        const badge = item.querySelector('.annotation-badge');
                        if (this.annotations.length > 0 && !badge) {
                            const newBadge = document.createElement('div');
                            newBadge.className = 'annotation-badge';
                            newBadge.textContent = '✓';
                            item.appendChild(newBadge);
                        } else if (this.annotations.length === 0 && badge) {
                            badge.remove();
                        }
                    }

                    await this.updateStats();
                } catch (error) {
                    console.error('Failed to save annotations:', error);
                }
            }

            async updateStats() {
                try {
                    const response = await fetch('/api/stats');
                    const stats = await response.json();

                    document.getElementById('annotatedImages').textContent = stats.annotated_images;
                    document.getElementById('progressPercent').textContent =
                        Math.round(stats.completion_rate) + '%';
                } catch (error) {
                    console.error('Failed to update stats:', error);
                }
            }

            resizeCanvas() {
                if (!this.currentImage) return;

                const container = this.canvas.parentElement;
                const maxWidth = container.clientWidth - 40;
                const maxHeight = container.clientHeight - 40;

                const scale = Math.min(
                    maxWidth / this.currentImage.width,
                    maxHeight / this.currentImage.height,
                    1
                );

                this.canvas.width = this.currentImage.width * scale;
                this.canvas.height = this.currentImage.height * scale;

                this.scale = scale;
            }

            render() {
                if (!this.currentImage) return;

                // Clear canvas
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

                // Draw image
                this.ctx.drawImage(this.currentImage, 0, 0, this.canvas.width, this.canvas.height);

                // Draw grid if enabled
                if (this.showGrid) {
                    this.drawGrid();
                }

                // Draw annotations
                this.annotations.forEach(ann => {
                    this.drawAnnotation(ann, ann === this.selectedAnnotation);
                });

                // Draw current annotation being created
                if (this.currentAnnotation) {
                    this.drawAnnotation(this.currentAnnotation, true);
                }
            }

            drawGrid() {
                this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
                this.ctx.lineWidth = 1;

                const gridSize = 50;

                for (let x = 0; x <= this.canvas.width; x += gridSize) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(x, 0);
                    this.ctx.lineTo(x, this.canvas.height);
                    this.ctx.stroke();
                }

                for (let y = 0; y <= this.canvas.height; y += gridSize) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(0, y);
                    this.ctx.lineTo(this.canvas.width, y);
                    this.ctx.stroke();
                }
            }

            drawAnnotation(ann, isSelected) {
                const color = isSelected ? '#10b981' : '#6366f1';

                if (ann.type === 'bbox') {
                    const [x1, y1] = ann.points[0];
                    const [x2, y2] = ann.points[1];

                    // Draw box
                    this.ctx.strokeStyle = color;
                    this.ctx.lineWidth = 2;
                    this.ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

                    // Draw label
                    this.ctx.fillStyle = color;
                    this.ctx.fillRect(x1, y1 - 20, ann.label.length * 8 + 10, 20);
                    this.ctx.fillStyle = 'white';
                    this.ctx.font = '12px sans-serif';
                    this.ctx.fillText(ann.label, x1 + 5, y1 - 5);

                    // Draw corners if selected
                    if (isSelected) {
                        const corners = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]];
                        corners.forEach(([x, y]) => {
                            this.ctx.fillStyle = color;
                            this.ctx.fillRect(x - 4, y - 4, 8, 8);
                        });
                    }
                } else if (ann.type === 'polygon') {
                    // Draw polygon
                    this.ctx.strokeStyle = color;
                    this.ctx.lineWidth = 2;
                    this.ctx.beginPath();
                    ann.points.forEach((point, i) => {
                        if (i === 0) {
                            this.ctx.moveTo(point[0], point[1]);
                        } else {
                            this.ctx.lineTo(point[0], point[1]);
                        }
                    });
                    this.ctx.closePath();
                    this.ctx.stroke();

                    // Draw label
                    if (ann.points.length > 0) {
                        const [x, y] = ann.points[0];
                        this.ctx.fillStyle = color;
                        this.ctx.fillRect(x, y - 20, ann.label.length * 8 + 10, 20);
                        this.ctx.fillStyle = 'white';
                        this.ctx.font = '12px sans-serif';
                        this.ctx.fillText(ann.label, x + 5, y - 5);
                    }

                    // Draw points if selected
                    if (isSelected) {
                        ann.points.forEach(([x, y]) => {
                            this.ctx.fillStyle = color;
                            this.ctx.fillRect(x - 4, y - 4, 8, 8);
                        });
                    }
                }
            }

            updateAnnotationList() {
                const list = document.getElementById('annotationList');
                list.innerHTML = '';

                if (this.annotations.length === 0) {
                    list.innerHTML = '<div style="color: var(--text-dim); text-align: center; padding: 20px;">No annotations yet</div>';
                    return;
                }

                this.annotations.forEach((ann, index) => {
                    const item = document.createElement('div');
                    item.className = 'annotation-item';

                    const label = document.createElement('div');
                    label.className = 'annotation-label';
                    label.textContent = `${ann.label} (${ann.type})`;
                    item.appendChild(label);

                    const deleteBtn = document.createElement('button');
                    deleteBtn.className = 'delete-btn';
                    deleteBtn.textContent = 'Delete';
                    deleteBtn.addEventListener('click', () => this.deleteAnnotation(index));
                    item.appendChild(deleteBtn);

                    item.addEventListener('click', () => {
                        this.selectedAnnotation = ann;
                        this.render();
                    });

                    list.appendChild(item);
                });
            }

            deleteAnnotation(index) {
                this.annotations.splice(index, 1);
                this.selectedAnnotation = null;
                this.updateAnnotationList();
                this.render();

                if (this.autoSave) {
                    this.saveAnnotations();
                }
            }

            setupEventListeners() {
                // Tool selection
                document.querySelectorAll('.tool-btn[data-tool]').forEach(btn => {
                    btn.addEventListener('click', () => {
                        document.querySelectorAll('.tool-btn[data-tool]').forEach(b =>
                            b.classList.remove('active'));
                        btn.classList.add('active');
                        this.currentTool = btn.dataset.tool;
                        this.canvas.style.cursor = this.currentTool === 'select' ? 'pointer' : 'crosshair';
                    });
                });

                // Canvas mouse events
                this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
                this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
                this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));

                // Navigation
                document.getElementById('prevBtn').addEventListener('click', () => {
                    this.loadImage(this.currentIndex - 1);
                });

                document.getElementById('nextBtn').addEventListener('click', () => {
                    this.loadImage(this.currentIndex + 1);
                });

                // Clear button
                document.getElementById('clearBtn').addEventListener('click', () => {
                    if (confirm('Clear all annotations for this image?')) {
                        this.annotations = [];
                        this.updateAnnotationList();
                        this.render();
                        if (this.autoSave) {
                            this.saveAnnotations();
                        }
                    }
                });

                // Grid toggle
                document.getElementById('gridBtn').addEventListener('click', () => {
                    this.showGrid = !this.showGrid;
                    document.getElementById('gridBtn').classList.toggle('active', this.showGrid);
                    this.render();
                });

                // Auto-save toggle
                document.getElementById('autoSaveBtn').addEventListener('click', () => {
                    this.autoSave = !this.autoSave;
                    const btn = document.getElementById('autoSaveBtn');
                    btn.textContent = this.autoSave ? '💾 Auto-save ON' : '💾 Auto-save OFF';
                    btn.style.background = this.autoSave ? '' : 'var(--warning)';
                });

                // Export buttons
                document.querySelectorAll('.export-btn').forEach(btn => {
                    btn.addEventListener('click', async () => {
                        const format = btn.dataset.format;
                        const response = await fetch(`/api/export/${format}`);

                        if (format === 'coco') {
                            const data = await response.json();
                            const blob = new Blob([JSON.stringify(data, null, 2)],
                                { type: 'application/json' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `annotations_${format}.json`;
                            a.click();
                        } else {
                            const data = await response.text();
                            const blob = new Blob([data], { type: 'text/plain' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `annotations_${format}.txt`;
                            a.click();
                        }
                    });
                });

                // Window resize
                window.addEventListener('resize', () => {
                    this.resizeCanvas();
                    this.render();
                });
            }

            setupKeyboardShortcuts() {
                document.addEventListener('keydown', (e) => {
                    // Navigation
                    if (e.key === 'ArrowLeft' && this.currentIndex > 0) {
                        this.loadImage(this.currentIndex - 1);
                    } else if (e.key === 'ArrowRight' && this.currentIndex < this.images.length - 1) {
                        this.loadImage(this.currentIndex + 1);
                    }

                    // Tool selection
                    else if (e.key === 'b' || e.key === 'B') {
                        document.querySelector('.tool-btn[data-tool="bbox"]').click();
                    } else if (e.key === 'p' || e.key === 'P') {
                        document.querySelector('.tool-btn[data-tool="polygon"]').click();
                    } else if (e.key === 's' || e.key === 'S') {
                        document.querySelector('.tool-btn[data-tool="select"]').click();
                    }

                    // Grid toggle
                    else if (e.key === 'g' || e.key === 'G') {
                        document.getElementById('gridBtn').click();
                    }

                    // Delete selected
                    else if (e.key === 'Delete' && this.selectedAnnotation) {
                        const index = this.annotations.indexOf(this.selectedAnnotation);
                        if (index !== -1) {
                            this.deleteAnnotation(index);
                        }
                    }

                    // Save
                    else if (e.ctrlKey && e.key === 's') {
                        e.preventDefault();
                        this.saveAnnotations();
                    }

                    // Undo
                    else if (e.ctrlKey && e.key === 'z') {
                        e.preventDefault();
                        if (this.annotations.length > 0) {
                            this.annotations.pop();
                            this.updateAnnotationList();
                            this.render();
                        }
                    }
                });
            }

            handleMouseDown(e) {
                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                if (this.currentTool === 'select') {
                    // Select annotation
                    this.selectedAnnotation = this.getAnnotationAt(x, y);
                    this.render();
                } else if (this.currentTool === 'bbox') {
                    // Start drawing bbox
                    if (!this.selectedClass) {
                        alert('Please select a class first');
                        return;
                    }

                    this.isDrawing = true;
                    this.startPoint = [x, y];
                    this.currentAnnotation = {
                        id: 'ann_' + Date.now(),
                        type: 'bbox',
                        label: this.selectedClass,
                        points: [[x, y], [x, y]],
                        confidence: 1.0
                    };
                } else if (this.currentTool === 'polygon') {
                    // Add polygon point
                    if (!this.selectedClass) {
                        alert('Please select a class first');
                        return;
                    }

                    if (!this.currentAnnotation) {
                        this.currentAnnotation = {
                            id: 'ann_' + Date.now(),
                            type: 'polygon',
                            label: this.selectedClass,
                            points: [],
                            confidence: 1.0
                        };
                    }

                    this.currentAnnotation.points.push([x, y]);

                    // Close polygon on right click or double click
                    if (e.button === 2 || (this.currentAnnotation.points.length > 2 &&
                        this.isNearFirstPoint(x, y))) {
                        this.annotations.push(this.currentAnnotation);
                        this.currentAnnotation = null;
                        this.updateAnnotationList();
                        if (this.autoSave) {
                            this.saveAnnotations();
                        }
                    }

                    this.render();
                }
            }

            handleMouseMove(e) {
                if (!this.isDrawing || !this.currentAnnotation) return;

                const rect = this.canvas.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                if (this.currentTool === 'bbox') {
                    this.currentAnnotation.points[1] = [x, y];
                    this.render();
                }
            }

            handleMouseUp(e) {
                if (!this.isDrawing || !this.currentAnnotation) return;

                if (this.currentTool === 'bbox') {
                    this.isDrawing = false;

                    // Check if bbox is valid (not too small)
                    const [x1, y1] = this.currentAnnotation.points[0];
                    const [x2, y2] = this.currentAnnotation.points[1];

                    if (Math.abs(x2 - x1) > 10 && Math.abs(y2 - y1) > 10) {
                        // Normalize points (ensure top-left to bottom-right)
                        this.currentAnnotation.points = [
                            [Math.min(x1, x2), Math.min(y1, y2)],
                            [Math.max(x1, x2), Math.max(y1, y2)]
                        ];

                        this.annotations.push(this.currentAnnotation);
                        this.updateAnnotationList();

                        if (this.autoSave) {
                            this.saveAnnotations();
                        }
                    }

                    this.currentAnnotation = null;
                    this.render();
                }
            }

            getAnnotationAt(x, y) {
                // Check annotations in reverse order (top to bottom)
                for (let i = this.annotations.length - 1; i >= 0; i--) {
                    const ann = this.annotations[i];

                    if (ann.type === 'bbox') {
                        const [x1, y1] = ann.points[0];
                        const [x2, y2] = ann.points[1];

                        if (x >= x1 && x <= x2 && y >= y1 && y <= y2) {
                            return ann;
                        }
                    } else if (ann.type === 'polygon') {
                        if (this.isPointInPolygon(x, y, ann.points)) {
                            return ann;
                        }
                    }
                }

                return null;
            }

            isPointInPolygon(x, y, points) {
                let inside = false;

                for (let i = 0, j = points.length - 1; i < points.length; j = i++) {
                    const xi = points[i][0], yi = points[i][1];
                    const xj = points[j][0], yj = points[j][1];

                    const intersect = ((yi > y) !== (yj > y))
                        && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);

                    if (intersect) inside = !inside;
                }

                return inside;
            }

            isNearFirstPoint(x, y) {
                if (!this.currentAnnotation || this.currentAnnotation.points.length === 0) {
                    return false;
                }

                const [fx, fy] = this.currentAnnotation.points[0];
                const distance = Math.sqrt((x - fx) ** 2 + (y - fy) ** 2);
                return distance < 10;
            }
        }

        // Initialize the annotation studio
        const studio = new AnnotationStudio();
    </script>
</body>
</html>'''