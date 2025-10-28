"""
Inference module for ModelCub.
"""

from .inference_service import InferenceService
from .inference_base import (
    InferenceAdapter,
    ImagePrediction,
    Detection,
    BoundingBox
)
from .inference_yolo import YOLOInferenceAdapter

__all__ = [
    'InferenceService',
    'InferenceAdapter',
    'ImagePrediction',
    'Detection',
    'BoundingBox',
    'YOLOInferenceAdapter'
]