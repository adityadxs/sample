"""Pydantic schemas for API request and response models."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Health Schemas
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(default="healthy", description="Application operational status")
    app_name: str
    version: str
    environment: str
    database_connected: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# SKU Registry Schemas
# ---------------------------------------------------------------------------

class SKUBase(BaseModel):
    """Base SKU schema."""
    sku_name: str = Field(..., min_length=1, max_length=255, description="Human readable SKU name")
    brand: str = Field(..., min_length=1, max_length=100, description="Brand name derived from SKU")
    category: Optional[str] = Field(None, max_length=100, description="Category e.g. soft_drink, juice, water")
    variant: Optional[str] = Field(None, max_length=100, description="Variant/flavor e.g. Diet, Zero, Orange")
    pack_type: Optional[str] = Field(None, max_length=50, description="Packaging type e.g. PET, Can, Glass")
    volume_ml: Optional[float] = Field(None, gt=0, description="Volume in milliliters")
    metadata_json: Dict[str, Any] = Field(default_factory=dict, description="Extensible product metadata")
    active: bool = Field(default=True, description="Whether this SKU is actively sold/classified")


class SKUCreate(SKUBase):
    """Schema for registering a new SKU."""
    sku_id: str = Field(..., min_length=1, max_length=100, description="Unique SKU identifier")


class SKUUpdate(BaseModel):
    """Schema for updating an existing SKU."""
    sku_name: Optional[str] = Field(None, min_length=1, max_length=255)
    brand: Optional[str] = Field(None, min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=100)
    variant: Optional[str] = Field(None, max_length=100)
    pack_type: Optional[str] = Field(None, max_length=50)
    volume_ml: Optional[float] = Field(None, gt=0)
    metadata_json: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None


class SKUResponse(SKUBase):
    """Schema for returning SKU information."""
    model_config = ConfigDict(from_attributes=True)

    sku_id: str
    created_at: datetime
    updated_at: datetime


class SKUFilterParams(BaseModel):
    """Query parameter filter for SKU listing."""
    brand: Optional[str] = None
    category: Optional[str] = None
    active: Optional[bool] = None


# ---------------------------------------------------------------------------
# Prediction & Detection Schemas (Foundation for Phase 2)
# ---------------------------------------------------------------------------

class TopKPrediction(BaseModel):
    """Item in top-k classifier prediction list."""
    sku_id: str
    sku_name: str
    brand: str
    confidence: float


class DetectionItem(BaseModel):
    """Single bottle detection and SKU classification result."""
    detection_id: str
    bbox: List[float] = Field(..., description="[x1, y1, x2, y2] coordinates")
    object_class: str = "bottle"
    sku_id: str
    sku_name: str
    brand: str
    confidence: float
    review_status: str = "accepted"
    top_k: List[TopKPrediction] = Field(default_factory=list)


class PredictionResponse(BaseModel):
    """Response payload for image prediction endpoint."""
    model_version: str
    image_id: str
    total_bottles: int
    detections: List[DetectionItem]
    sku_counts: Dict[str, int]


# ---------------------------------------------------------------------------
# Feedback Schemas (Foundation for Phase 3)
# ---------------------------------------------------------------------------

class FeedbackCreate(BaseModel):
    """Human feedback submission payload."""
    image_id: Optional[str] = None
    detection_id: Optional[str] = None
    predicted_sku_id: Optional[str] = None
    corrected_sku_id: str = Field(..., min_length=1, max_length=100)
    comments: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Response payload after feedback submission."""
    feedback_id: str
    status: str = "queued_for_training"
    corrected_sku_id: str
    created_at: datetime


# ---------------------------------------------------------------------------
# Model & Training Status Schemas (Foundation for Phase 4-5)
# ---------------------------------------------------------------------------

class ModelStatusResponse(BaseModel):
    """Model status and registry metadata response."""
    current_model_version: str
    number_of_skus: int
    training_samples: int
    replay_buffer_size: int
    last_training_time: Optional[datetime] = None
    validation_metrics: Dict[str, Any] = Field(default_factory=dict)
    model_status: str = "active"


class TrainingTriggerRequest(BaseModel):
    """Request schema for triggering a continual learning job."""
    force: bool = Field(default=False, description="Force training even if min sample requirement is not met")
    target_version: Optional[str] = None


class TrainingJobStatusResponse(BaseModel):
    """Training job execution status schema."""
    job_id: str
    status: str
    progress: float
    samples_used: int
    model_version_being_trained: str
    validation_status: Optional[str] = None
    validation_metrics: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
