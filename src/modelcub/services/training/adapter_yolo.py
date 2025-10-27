"""
YOLO training adapter for Ultralytics integration.

Handles YOLO-specific command building and results parsing.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
import csv


class YOLOAdapter:
    """
    Adapter for training YOLO models using Ultralytics.

    Builds training commands and parses results for YOLOv8/YOLOv9.
    """

    def build_command(
        self,
        dataset_path: Path,
        output_path: Path,
        config: Dict[str, Any]
    ) -> List[str]:
        """Build YOLO training command."""

        # Correct format: yolo [TASK] MODE args
        # TASK is optional (detect/segment/classify/pose/obb)
        # MODE is required (train/predict/val/export/track)
        task = config.get('task', 'detect')

        command = ['yolo', task, 'train']

        # Add parameters
        dataset_yaml = dataset_path / 'dataset.yaml'
        command.extend([
            f'model={config["model"]}',
            f'data={dataset_yaml}',
            f'project={output_path}',
            'name=train',
            f'epochs={config["epochs"]}',
            f'imgsz={config["imgsz"]}',
            f'batch={config["batch"]}',
            f'device={config["device"]}',
            f'patience={config["patience"]}',
            f'save_period={config["save_period"]}',
            f'workers={config["workers"]}'
        ])

        if 'seed' in config:
            command.append(f'seed={config["seed"]}')

        # Additional YOLO parameters
        yolo_params = [
            'lr0', 'lrf', 'momentum', 'weight_decay', 'warmup_epochs',
            'warmup_momentum', 'warmup_bias_lr', 'box', 'cls', 'dfl',
            'pose', 'kobj', 'label_smoothing', 'nbs', 'hsv_h', 'hsv_s',
            'hsv_v', 'degrees', 'translate', 'scale', 'shear', 'perspective',
            'flipud', 'fliplr', 'mosaic', 'mixup', 'copy_paste'
        ]

        for param in yolo_params:
            if param in config:
                command.append(f'{param}={config[param]}')

        return command


    def parse_results(self, run_path: Path) -> Dict[str, Any]:
        """
        Parse training results from YOLO output.

        Args:
            run_path: Path to training run directory

        Returns:
            Dictionary with metrics (map50, map50_95, precision, recall, etc.)
        """
        results_csv = run_path / 'train' / 'results.csv'

        if not results_csv.exists():
            return {}

        try:
            # Read results CSV
            with open(results_csv, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)

            if not rows:
                return {}

            # Get best epoch (last row or best mAP)
            best_row = max(
                rows,
                key=lambda r: float(r.get('metrics/mAP50-95(B)', 0) or 0)
            )

            # Extract key metrics
            metrics = {
                'map50': float(best_row.get('metrics/mAP50(B)', 0) or 0),
                'map50_95': float(best_row.get('metrics/mAP50-95(B)', 0) or 0),
                'precision': float(best_row.get('metrics/precision(B)', 0) or 0),
                'recall': float(best_row.get('metrics/recall(B)', 0) or 0),
                'best_epoch': int(best_row.get('epoch', 0) or 0),
                'box_loss': float(best_row.get('train/box_loss', 0) or 0),
                'cls_loss': float(best_row.get('train/cls_loss', 0) or 0),
                'dfl_loss': float(best_row.get('train/dfl_loss', 0) or 0)
            }

            return metrics

        except Exception as e:
            # Return empty if parsing fails
            return {}

    def get_best_weights(self, run_path: Path) -> Optional[Path]:
        """
        Get path to best model weights.

        Args:
            run_path: Path to training run directory

        Returns:
            Path to best.pt or None if not found
        """
        weights_path = run_path / 'train' / 'weights' / 'best.pt'

        if weights_path.exists():
            return weights_path

        return None

    def get_last_weights(self, run_path: Path) -> Optional[Path]:
        """
        Get path to last checkpoint weights.

        Args:
            run_path: Path to training run directory

        Returns:
            Path to last.pt or None if not found
        """
        weights_path = run_path / 'train' / 'weights' / 'last.pt'

        if weights_path.exists():
            return weights_path

        return None