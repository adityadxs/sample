"""Prediction Service coordinating Detection, Cropping, SKU Classification, and Confidence Routing."""
from collections import Counter
from typing import Dict, List, Optional
from PIL import Image
from sqlalchemy.orm import Session

from app.config import settings
from app.ml.base import BaseDetector, BaseClassifier
from app.ml.mock_detector import MockBottleDetector
from app.ml.mock_classifier import MockSKUClassifier
from app.models.database_models import Image as DBImage, Detection as DBDetection, Prediction as DBPrediction
from app.models.schemas import DetectionItem, PredictionResponse, TopKPrediction
from app.services.sku_service import sku_service
from app.utils.image_utils import crop_bottle_bounding_box, read_image_from_bytes, save_image_to_disk
from app.utils.logging import logger


class PredictionService:
    """Production prediction service orchestrating detector, cropper, classifier, and SKU registry."""

    def __init__(
        self,
        detector: Optional[BaseDetector] = None,
        classifier: Optional[BaseClassifier] = None,
        model_version: str = "v1.0.0-mock",
    ):
        self.detector = detector or MockBottleDetector()
        self.classifier = classifier or MockSKUClassifier()
        self.model_version = model_version

    def determine_review_status(
        self,
        confidence: float,
        top_k_confidences: List[float],
    ) -> str:
        """Determine if prediction is automatically accepted or requires review."""
        if confidence < settings.CLASSIFICATION_REVIEW_THRESHOLD:
            return "manual_review"

        # Check margin between top 1 and top 2 predictions
        if len(top_k_confidences) >= 2:
            margin = top_k_confidences[0] - top_k_confidences[1]
            if margin < settings.CONFIDENCE_MARGIN_THRESHOLD:
                return "review_queue"

        if confidence >= settings.CLASSIFICATION_HIGH_CONFIDENCE:
            return "accepted"

        return "review_queue"

    def process_image(
        self,
        image_bytes: bytes,
        db: Session,
        source: str = "api_upload",
    ) -> PredictionResponse:
        """Execute the complete bottle vision pipeline on uploaded image bytes."""
        # 1. Decode Image
        pil_image: Image.Image = read_image_from_bytes(image_bytes)
        img_width, img_height = pil_image.size

        # 2. Save Raw Image to disk & record in DB
        image_id, raw_image_path = save_image_to_disk(
            pil_image,
            directory=str(settings.RAW_IMAGE_DIR),
            prefix="raw",
        )
        db_image = DBImage(
            image_id=image_id,
            file_path=raw_image_path,
            source=source,
            width=img_width,
            height=img_height,
        )
        db.add(db_image)
        db.commit()

        # 3. Object Detection (Bottle Localization)
        detected_boxes = self.detector.predict(
            image=pil_image,
            confidence_threshold=settings.DETECTION_CONFIDENCE_THRESHOLD,
        )

        detections_out: List[DetectionItem] = []
        sku_counter = Counter()

        # 4. Process each detected bottle crop
        for det in detected_boxes:
            # Crop bottle area
            bottle_crop = crop_bottle_bounding_box(pil_image, det.bbox)
            det_id, crop_path = save_image_to_disk(
                bottle_crop,
                directory=str(settings.CROP_IMAGE_DIR),
                prefix="crop",
            )

            # Record Detection in DB
            db_detection = DBDetection(
                detection_id=det_id,
                image_id=image_id,
                bbox_x1=det.bbox[0],
                bbox_y1=det.bbox[1],
                bbox_x2=det.bbox[2],
                bbox_y2=det.bbox[3],
                object_class=det.object_class,
                confidence=det.confidence,
                crop_path=crop_path,
            )
            db.add(db_detection)
            db.commit()

            # 5. SKU Classification
            cls_result = self.classifier.predict(bottle_crop, top_k=5)

            # 6. Lookup SKU metadata from registry (brand, SKU name, etc.)
            top_sku = sku_service.get_sku_by_id(db, cls_result.sku_id)
            sku_name = top_sku.sku_name if top_sku else cls_result.sku_id
            brand = top_sku.brand if top_sku else "Unknown Brand"

            # Format top-k list with metadata
            top_k_items: List[TopKPrediction] = []
            top_k_confs: List[float] = []
            for item in cls_result.top_k:
                top_k_confs.append(item.confidence)
                candidate_sku = sku_service.get_sku_by_id(db, item.sku_id)
                top_k_items.append(
                    TopKPrediction(
                        sku_id=item.sku_id,
                        sku_name=candidate_sku.sku_name if candidate_sku else item.sku_id,
                        brand=candidate_sku.brand if candidate_sku else "Unknown Brand",
                        confidence=item.confidence,
                    )
                )

            # 7. Confidence Routing
            review_status = self.determine_review_status(
                cls_result.confidence,
                top_k_confs,
            )
            is_accepted = (review_status == "accepted")

            # 8. Record Prediction in DB
            db_prediction = DBPrediction(
                detection_id=det_id,
                sku_id=cls_result.sku_id,
                confidence=cls_result.confidence,
                top_k_predictions=[item.model_dump() for item in top_k_items],
                model_version=self.model_version,
                review_status=review_status,
                is_accepted=is_accepted,
            )
            db.add(db_prediction)
            db.commit()

            # 9. Append to response items
            detections_out.append(
                DetectionItem(
                    detection_id=det_id,
                    bbox=det.bbox,
                    object_class=det.object_class,
                    sku_id=cls_result.sku_id,
                    sku_name=sku_name,
                    brand=brand,
                    confidence=cls_result.confidence,
                    review_status=review_status,
                    top_k=top_k_items,
                )
            )
            sku_counter[cls_result.sku_id] += 1

        logger.info(
            f"Processed image {image_id}: {len(detections_out)} bottles detected across {len(sku_counter)} unique SKUs."
        )

        return PredictionResponse(
            model_version=self.model_version,
            image_id=image_id,
            total_bottles=len(detections_out),
            detections=detections_out,
            sku_counts=dict(sku_counter),
        )


prediction_service = PredictionService()
