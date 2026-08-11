"""SQLAlchemy database models for SKU, vision, feedback, and training entities."""
import uuid
from datetime import datetime
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


def generate_uuid() -> str:
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


class SKU(Base):
    """SKU registry table - primary classification target."""
    __tablename__ = "skus"

    sku_id = Column(String(100), primary_key=True, index=True)
    sku_name = Column(String(255), nullable=False)
    brand = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    variant = Column(String(100), nullable=True)
    pack_type = Column(String(50), nullable=True)
    volume_ml = Column(Float, nullable=True)
    metadata_json = Column(JSON, default=dict, nullable=False)
    active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    predictions = relationship("Prediction", back_populates="sku")
    training_samples = relationship("TrainingSample", back_populates="sku")


class Image(Base):
    """Raw uploaded or processed images."""
    __tablename__ = "images"

    image_id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    file_path = Column(String(500), nullable=False)
    source = Column(String(50), default="upload", nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    detections = relationship("Detection", back_populates="image", cascade="all, delete-orphan")


class Detection(Base):
    """Detected bottle bounding boxes within images."""
    __tablename__ = "detections"

    detection_id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    image_id = Column(String(36), ForeignKey("images.image_id", ondelete="CASCADE"), nullable=False, index=True)
    bbox_x1 = Column(Float, nullable=False)
    bbox_y1 = Column(Float, nullable=False)
    bbox_x2 = Column(Float, nullable=False)
    bbox_y2 = Column(Float, nullable=False)
    object_class = Column(String(50), default="bottle", nullable=False)
    confidence = Column(Float, nullable=False)
    crop_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    image = relationship("Image", back_populates="detections")
    prediction = relationship("Prediction", uselist=False, back_populates="detection", cascade="all, delete-orphan")


class Prediction(Base):
    """SKU classification predictions for detected bottles."""
    __tablename__ = "predictions"

    prediction_id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    detection_id = Column(String(36), ForeignKey("detections.detection_id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    sku_id = Column(String(100), ForeignKey("skus.sku_id"), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    top_k_predictions = Column(JSON, default=list, nullable=False)
    model_version = Column(String(50), nullable=False, index=True)
    review_status = Column(String(50), default="accepted", nullable=False, index=True)
    is_accepted = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    detection = relationship("Detection", back_populates="prediction")
    sku = relationship("SKU", back_populates="predictions")


class Feedback(Base):
    """Human corrections and feedback records."""
    __tablename__ = "feedbacks"

    feedback_id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    image_id = Column(String(36), nullable=True, index=True)
    detection_id = Column(String(36), nullable=True, index=True)
    predicted_sku_id = Column(String(100), nullable=True)
    corrected_sku_id = Column(String(100), ForeignKey("skus.sku_id"), nullable=False, index=True)
    comments = Column(Text, nullable=True)
    is_processed_for_training = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TrainingSample(Base):
    """Verified training sample queue and replay buffer storage."""
    __tablename__ = "training_samples"

    sample_id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    sku_id = Column(String(100), ForeignKey("skus.sku_id"), nullable=False, index=True)
    crop_path = Column(String(500), nullable=False)
    source = Column(String(50), default="feedback", nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False, index=True)
    is_replay_candidate = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    sku = relationship("SKU", back_populates="training_samples")


class TrainingJob(Base):
    """Continual learning training job records and metrics."""
    __tablename__ = "training_jobs"

    job_id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    status = Column(String(50), default="queued", nullable=False, index=True)
    progress = Column(Float, default=0.0, nullable=False)
    samples_count = Column(Integer, default=0, nullable=False)
    target_version = Column(String(50), nullable=False)
    base_version = Column(String(50), nullable=True)
    validation_status = Column(String(50), nullable=True)
    metrics = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ModelVersion(Base):
    """Model registry for version management, validation status, and deployment."""
    __tablename__ = "model_versions"

    version = Column(String(50), primary_key=True, index=True)
    is_active = Column(Boolean, default=False, nullable=False, index=True)
    number_of_skus = Column(Integer, default=0, nullable=False)
    training_samples_count = Column(Integer, default=0, nullable=False)
    validation_metrics = Column(JSON, default=dict, nullable=True)
    status = Column(String(50), default="candidate", nullable=False, index=True)
    model_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    deployed_at = Column(DateTime, nullable=True)
