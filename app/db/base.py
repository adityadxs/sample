"""Database base metadata imports."""
from app.db.session import Base
# Import all database models here so Alembic / Base.metadata.create_all has access
from app.models.database_models import (
    SKU,
    Image,
    Detection,
    Prediction,
    Feedback,
    TrainingSample,
    TrainingJob,
    ModelVersion,
)

__all__ = [
    "Base",
    "SKU",
    "Image",
    "Detection",
    "Prediction",
    "Feedback",
    "TrainingSample",
    "TrainingJob",
    "ModelVersion",
]
