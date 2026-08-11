"""Human feedback and correction endpoint."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.database_models import Detection, Feedback, TrainingSample
from app.models.schemas import FeedbackCreate, FeedbackResponse
from app.services.sku_service import sku_service
from app.utils.logging import logger

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit prediction feedback / human correction",
    description="Allows human operators to correct SKU predictions. Adds verified sample to continual learning queue.",
)
def submit_feedback(
    feedback_in: FeedbackCreate,
    db: Session = Depends(get_db),
) -> FeedbackResponse:
    """Record human correction and enqueue sample for incremental training."""
    # 1. Validate corrected SKU exists in registry
    target_sku = sku_service.get_sku_by_id(db, feedback_in.corrected_sku_id)
    if not target_sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Target SKU '{feedback_in.corrected_sku_id}' does not exist in registry.",
        )

    # 2. Record Feedback entry
    feedback = Feedback(
        image_id=feedback_in.image_id,
        detection_id=feedback_in.detection_id,
        predicted_sku_id=feedback_in.predicted_sku_id,
        corrected_sku_id=feedback_in.corrected_sku_id,
        comments=feedback_in.comments,
        is_processed_for_training=True,
    )
    db.add(feedback)

    # 3. If detection exists, enqueue crop as verified training sample
    crop_path = ""
    if feedback_in.detection_id:
        detection = db.query(Detection).filter(Detection.detection_id == feedback_in.detection_id).first()
        if detection and detection.crop_path:
            crop_path = detection.crop_path

    if crop_path:
        sample = TrainingSample(
            sku_id=feedback_in.corrected_sku_id,
            crop_path=crop_path,
            source="human_feedback",
            is_verified=True,
            is_replay_candidate=True,
        )
        db.add(sample)

    db.commit()
    db.refresh(feedback)
    logger.info(f"Recorded feedback {feedback.feedback_id} for SKU {feedback_in.corrected_sku_id}")

    return FeedbackResponse(
        feedback_id=feedback.feedback_id,
        status="queued_for_training",
        corrected_sku_id=feedback.corrected_sku_id,
        created_at=feedback.created_at,
    )
