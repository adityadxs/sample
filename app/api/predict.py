"""Bottle detection and SKU prediction endpoint."""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.schemas import PredictionResponse
from app.services.prediction_service import prediction_service
from app.utils.image_utils import validate_upload_image

router = APIRouter(tags=["Prediction"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect bottles and identify SKUs",
    description=(
        "Receives a refrigerator beverage image, detects all visible bottles, "
        "crops each bottle, identifies the exact product/SKU, derives brand metadata, "
        "and routes predictions by confidence."
    ),
)
async def predict_image(
    file: UploadFile = File(..., description="Beverage shelf/refrigerator image (JPEG, PNG, WebP)"),
    db: Session = Depends(get_db),
) -> PredictionResponse:
    """Run object detector and SKU classifier on uploaded image."""
    validate_upload_image(file)
    try:
        contents = await file.read()
        return prediction_service.process_image(
            image_bytes=contents,
            db=db,
            source="api_upload",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process image: {str(e)}",
        )
