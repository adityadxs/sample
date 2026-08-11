"""Abstract interfaces and base classes for ML Detector, Classifier, and Continual Learning."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, NamedTuple, Optional
from PIL import Image


class DetectionResult(NamedTuple):
    """Bounding box detection result."""
    bbox: List[float]  # [x1, y1, x2, y2]
    confidence: float
    object_class: str = "bottle"


class TopKPredictionItem(NamedTuple):
    """Single top-k class score."""
    sku_id: str
    confidence: float


class ClassificationResult(NamedTuple):
    """SKU classification prediction result."""
    sku_id: str
    confidence: float
    top_k: List[TopKPredictionItem]


class BaseDetector(ABC):
    """Abstract Base Class for Object Detectors (Bottle localization)."""

    @abstractmethod
    def predict(self, image: Image.Image, confidence_threshold: Optional[float] = None) -> List[DetectionResult]:
        """Detect visible bottles in the input image.

        Args:
            image: PIL Image instance.
            confidence_threshold: Optional threshold override.

        Returns:
            List of DetectionResult instances containing bounding boxes and confidences.
        """
        pass


class BaseClassifier(ABC):
    """Abstract Base Class for SKU Classifiers (Product identification)."""

    @abstractmethod
    def predict(self, crop: Image.Image, top_k: int = 5) -> ClassificationResult:
        """Classify a cropped bottle image into its exact SKU.

        Args:
            crop: PIL Image cropped to the bottle boundaries.
            top_k: Number of highest ranking predictions to return.

        Returns:
            ClassificationResult containing top sku_id, confidence, and top_k predictions.
        """
        pass
