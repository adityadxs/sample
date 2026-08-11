"""Tests for database models and schema relationships."""
from sqlalchemy.orm import Session
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


def test_database_models_creation(db_session: Session):
    """Test creating and persisting all database entities."""
    # 1. SKU
    sku = SKU(
        sku_id="SKU_TEST_001",
        sku_name="Test Beverage 500ml",
        brand="Test Brand",
        category="energy_drink",
        variant="Zero",
        pack_type="Can",
        volume_ml=500.0,
        metadata_json={"barcode": "12345678"},
        active=True,
    )
    db_session.add(sku)
    db_session.commit()

    # 2. Image
    img = Image(file_path="/data/raw/test.jpg", width=1920, height=1080)
    db_session.add(img)
    db_session.commit()

    # 3. Detection
    det = Detection(
        image_id=img.image_id,
        bbox_x1=100.0,
        bbox_y1=150.0,
        bbox_x2=300.0,
        bbox_y2=600.0,
        object_class="bottle",
        confidence=0.95,
        crop_path="/data/crops/crop_001.jpg",
    )
    db_session.add(det)
    db_session.commit()

    # 4. Prediction
    pred = Prediction(
        detection_id=det.detection_id,
        sku_id=sku.sku_id,
        confidence=0.92,
        top_k_predictions=[{"sku_id": "SKU_TEST_001", "confidence": 0.92}],
        model_version="v1.0.0",
        review_status="accepted",
        is_accepted=True,
    )
    db_session.add(pred)
    db_session.commit()

    # 5. Feedback
    feedback = Feedback(
        image_id=img.image_id,
        detection_id=det.detection_id,
        predicted_sku_id=sku.sku_id,
        corrected_sku_id=sku.sku_id,
        comments="Confirmed label",
    )
    db_session.add(feedback)

    # 6. Training Sample
    sample = TrainingSample(
        sku_id=sku.sku_id,
        crop_path="/data/training/crop_001.jpg",
        source="feedback",
        is_verified=True,
    )
    db_session.add(sample)

    # 7. Training Job
    job = TrainingJob(
        status="queued",
        target_version="v1.1.0",
        base_version="v1.0.0",
    )
    db_session.add(job)

    # 8. Model Version
    version = ModelVersion(
        version="v1.0.0",
        is_active=True,
        number_of_skus=1,
        status="active",
    )
    db_session.add(version)

    db_session.commit()

    # Query and verify
    persisted_sku = db_session.query(SKU).filter_by(sku_id="SKU_TEST_001").first()
    assert persisted_sku is not None
    assert persisted_sku.brand == "Test Brand"
    assert len(persisted_sku.predictions) == 1
    assert persisted_sku.predictions[0].confidence == 0.92
    assert len(persisted_sku.training_samples) == 1
