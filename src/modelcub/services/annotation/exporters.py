# src/modelcub/services/annotation/exporters.py
"""
Export annotations to different formats (YOLO, COCO, VOC).
"""
from __future__ import annotations
from typing import Dict, List, Tuple

from .models import ImageAnnotation


class YOLOExporter:
    """Export annotations in YOLO format."""

    def __init__(self, classes: List[str]):
        self.classes = classes

    def export(self, annotations: Dict[str, ImageAnnotation]) -> str:
        """
        Export to YOLO format.
        Returns a string with YOLO-formatted annotations.
        """
        output = []

        for img_ann in annotations.values():
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
                    lines.append(
                        f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                    )

            if lines:
                output.append(f"# {img_ann.image_id}")
                output.extend(lines)
                output.append("")

        return '\n'.join(output)


class COCOExporter:
    """Export annotations in COCO JSON format."""

    def __init__(self, classes: List[str]):
        self.classes = classes

    def export(self, annotations: Dict[str, ImageAnnotation]) -> dict:
        """
        Export to COCO format.
        Returns a dictionary in COCO format.
        """
        coco_data = {
            'images': [],
            'annotations': [],
            'categories': [
                {'id': i, 'name': cls}
                for i, cls in enumerate(self.classes)
            ]
        }

        ann_id = 0
        for img_idx, (img_id, img_ann) in enumerate(annotations.items()):
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
                        'category_id': (
                            self.classes.index(ann.label)
                            if ann.label in self.classes else 0
                        ),
                        'bbox': [x1, y1, abs(x2 - x1), abs(y2 - y1)],
                        'area': abs(x2 - x1) * abs(y2 - y1),
                        'iscrowd': 0
                    })
                    ann_id += 1

        return coco_data


class VOCExporter:
    """Export annotations in Pascal VOC XML format."""

    def export(self, annotations: Dict[str, ImageAnnotation]) -> str:
        """
        Export to Pascal VOC format.
        Returns a string with XML annotations.
        """
        xml_snippets = []

        for img_ann in annotations.values():
            xml_snippets.append(f"<annotation for='{img_ann.image_id}'>")
            for ann in img_ann.annotations:
                if ann.type == 'bbox':
                    xml_snippets.append(f"  <object class='{ann.label}' />")
            xml_snippets.append("</annotation>")

        return '\n'.join(xml_snippets)


class ExportManager:
    """Manages different export formats."""

    def __init__(self, classes: List[str]):
        self.yolo_exporter = YOLOExporter(classes)
        self.coco_exporter = COCOExporter(classes)
        self.voc_exporter = VOCExporter()

    def export(self, format: str, annotations: Dict[str, ImageAnnotation]) -> Tuple[any, int, dict]:
        """
        Export annotations in the specified format.

        Args:
            format: Export format ('yolo', 'coco', 'voc')
            annotations: Dictionary of annotations to export

        Returns:
            Tuple of (data, status_code, headers)
        """
        if format == 'yolo':
            data = self.yolo_exporter.export(annotations)
            return data, 200, {'Content-Type': 'text/plain'}

        elif format == 'coco':
            data = self.coco_exporter.export(annotations)
            return data, 200, {'Content-Type': 'application/json'}

        elif format == 'voc':
            data = self.voc_exporter.export(annotations)
            return data, 200, {'Content-Type': 'text/xml'}

        else:
            return {'error': f'Unknown format: {format}'}, 400, {'Content-Type': 'application/json'}