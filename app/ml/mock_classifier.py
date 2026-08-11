"""Mock SKU Classifier implementation conforming to BaseClassifier interface."""
import random
from typing import List
from PIL import Image
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.database_models import SKU
from app.ml.base import BaseClassifier, ClassificationResult, TopKPredictionItem
from app.utils.logging import logger


class MockSKUClassifier(BaseClassifier):
    """Mock classifier that predicts SKUs with top-k probabilities from registered catalog.
    
    Can be replaced transparently with ViT, CNN, or CLIP embedding search in later phases.
    """

    def __init__(self, model_version: str = "mock-v1.0.0"):
        self.model_version = model_version

    def _get_active_sku_ids(self) -> List[str]:
        """Fetch available active SKU IDs from database."""
        db: Session = SessionLocal()
        try:
            skus = db.query(SKU.sku_id).filter(SKU.active.is_(True)).all()
            return [s[0] for s in skus]
        finally:
            db.close()

    def predict(self, crop: Image.Image, top_k: int = 5) -> ClassificationResult:
        """Classify a bottle crop and return top prediction with top-k candidates."""
        available_skus = self._get_active_sku_ids()
        
        # Fallback if no SKUs exist in database yet
        if not available_skus:
            available_skus = ["COCA_COLA_500ML_PET", "PEPSI_500ML_PET", "SPRITE_500ML_PET"]

        # Randomly choose a top SKU or sample consistently
        chosen_sku = random.choice(available_skus)
        top_conf = round(random.uniform(0.70, 0.98), 2)
        
        remaining_conf = 1.0 - top_conf
        other_skus = [s for s in available_skus if s != chosen_sku]
        random.shuffle(other_skus)
        
        top_k_items = [TopKPredictionItem(sku_id=chosen_sku, confidence=top_conf)]
        
        num_others = min(top_k - 1, len(other_skus))
        if num_others > 0:
            # Generate remaining softmax distribution
            weights = [random.random() for _ in range(num_others)]
            sum_w = sum(weights) or 1.0
            for i in range(num_others):
                c = round((weights[i] / sum_w) * remaining_conf, 3)
                top_k_items.append(TopKPredictionItem(sku_id=other_skus[i], confidence=c))
        
        return ClassificationResult(
            sku_id=chosen_sku,
            confidence=top_conf,
            top_k=top_k_items,
        )
