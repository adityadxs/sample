"""ML models, interfaces, and adapters."""
from app.ml.base import (
    BaseDetector,
    BaseClassifier,
    DetectionResult,
    ClassificationResult,
    TopKPredictionItem,
)
from app.ml.mock_detector import MockBottleDetector
from app.ml.mock_classifier import MockSKUClassifier

__all__ = [
    "BaseDetector",
    "BaseClassifier",
    "DetectionResult",
    "ClassificationResult",
    "TopKPredictionItem",
    "MockBottleDetector",
    "MockSKUClassifier",
]
