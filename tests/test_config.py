"""Tests for application configuration."""
from pathlib import Path
from app.config import Settings


def test_settings_defaults():
    """Test configuration default values and directory paths."""
    config = Settings()
    assert config.APP_NAME == "Beverage Bottle Vision & Continual Learning System"
    assert config.DETECTION_CONFIDENCE_THRESHOLD == 0.40
    assert config.CLASSIFICATION_HIGH_CONFIDENCE == 0.90
    assert config.CLASSIFICATION_REVIEW_THRESHOLD == 0.50
    assert config.TRAINING_MIN_NEW_SAMPLES >= 1
    assert config.REPLAY_BUFFER_SIZE >= 10


def test_settings_init_directories(tmp_path: Path):
    """Test directory initialization."""
    config = Settings(
        DATA_DIR=tmp_path / "data",
        RAW_IMAGE_DIR=tmp_path / "data" / "raw",
        CROP_IMAGE_DIR=tmp_path / "data" / "crops",
        TRAINING_DATA_DIR=tmp_path / "data" / "training",
        REPLAY_BUFFER_DIR=tmp_path / "data" / "replay",
        VALIDATION_DATA_DIR=tmp_path / "data" / "validation",
        MODEL_DIR=tmp_path / "models" / "versions",
    )
    config.init_directories()
    assert config.RAW_IMAGE_DIR.exists()
    assert config.CROP_IMAGE_DIR.exists()
    assert config.TRAINING_DATA_DIR.exists()
    assert config.REPLAY_BUFFER_DIR.exists()
    assert config.VALIDATION_DATA_DIR.exists()
    assert config.MODEL_DIR.exists()
