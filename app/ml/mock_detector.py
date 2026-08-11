"""Mock Bottle Detector implementation conforming to BaseDetector interface."""
import random
from typing import List, Optional
from PIL import Image
from app.config import settings
from app.ml.base import BaseDetector, DetectionResult
from app.utils.logging import logger


class MockBottleDetector(BaseDetector):
    """Mock detector for locating bottles in refrigerator shelf images.
    
    Divides image dynamically or simulates realistic bottle bounding boxes.
    Can be replaced transparently with YOLO or Grounding DINO in subsequent phases.
    """

    def __init__(self, default_confidence: float = 0.94):
        self.default_confidence = default_confidence

    def predict(
        self,
        image: Image.Image,
        confidence_threshold: Optional[float] = None,
    ) -> List[DetectionResult]:
        """Generate realistic bottle bounding boxes based on image dimensions."""
        thresh = confidence_threshold if confidence_threshold is not None else settings.DETECTION_CONFIDENCE_THRESHOLD
        width, height = image.size
        
        detections: List[DetectionResult] = []
        
        # Heuristic simulation: Generate 3 to 6 bottle columns across shelf rows
        cols = 4
        rows = 2 if height > 600 else 1
        
        cell_w = width / cols
        cell_h = height / rows
        
        for r in range(rows):
            for c in range(cols):
                # Calculate bounding box with natural bottle aspect ratio (tall and slim)
                pad_x = cell_w * 0.15
                pad_y = cell_h * 0.10
                
                x1 = (c * cell_w) + pad_x
                y1 = (r * cell_h) + pad_y
                x2 = ((c + 1) * cell_w) - pad_x
                y2 = ((r + 1) * cell_h) - pad_y
                
                conf = round(random.uniform(0.78, 0.98), 2)
                if conf >= thresh:
                    detections.append(
                        DetectionResult(
                            bbox=[round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
                            confidence=conf,
                            object_class="bottle",
                        )
                    )
        
        logger.info(f"[MockDetector] Generated {len(detections)} bottle detections.")
        return detections
