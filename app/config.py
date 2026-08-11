"""Application configuration and settings management."""
from pathlib import Path
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration management for the system."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # General App Information
    APP_NAME: str = "Beverage Bottle Vision & Continual Learning System"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Storage and Security
    MAX_UPLOAD_SIZE_MB: int = 25
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp"]

    # Database
    DATABASE_URL: str = "sqlite:///./data/app.db"

    # Base Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = Path("./data")
    RAW_IMAGE_DIR: Path = Path("./data/raw")
    CROP_IMAGE_DIR: Path = Path("./data/crops")
    TRAINING_DATA_DIR: Path = Path("./data/training")
    REPLAY_BUFFER_DIR: Path = Path("./data/replay")
    VALIDATION_DATA_DIR: Path = Path("./data/validation")
    MODEL_DIR: Path = Path("./models/versions")

    # Detection & Classification Thresholds
    DETECTION_CONFIDENCE_THRESHOLD: float = Field(default=0.40, ge=0.0, le=1.0)
    CLASSIFICATION_HIGH_CONFIDENCE: float = Field(default=0.90, ge=0.0, le=1.0)
    CLASSIFICATION_REVIEW_THRESHOLD: float = Field(default=0.50, ge=0.0, le=1.0)
    CONFIDENCE_MARGIN_THRESHOLD: float = Field(default=0.15, ge=0.0, le=1.0)

    # Continual Learning & Replay Parameters
    TRAINING_MIN_NEW_SAMPLES: int = Field(default=10, ge=1)
    REPLAY_BUFFER_SIZE: int = Field(default=500, ge=10)
    REPLAY_SAMPLES_PER_CLASS: int = Field(default=20, ge=1)
    INCREMENTAL_BATCH_SIZE: int = Field(default=32, ge=1)
    LEARNING_RATE: float = Field(default=0.0005, gt=0.0)

    # Anti-Catastrophic Forgetting Thresholds
    MAX_OLD_SKU_ACCURACY_DROP: float = Field(default=0.05, ge=0.0, le=1.0)
    MIN_NEW_SKU_ACCURACY: float = Field(default=0.75, ge=0.0, le=1.0)

    def init_directories(self) -> None:
        """Create necessary storage directories if they do not exist."""
        directories = [
            self.DATA_DIR,
            self.RAW_IMAGE_DIR,
            self.CROP_IMAGE_DIR,
            self.TRAINING_DATA_DIR,
            self.REPLAY_BUFFER_DIR,
            self.VALIDATION_DATA_DIR,
            self.MODEL_DIR,
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
