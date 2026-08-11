"""Tests for bottle detection, SKU prediction, feedback, and model status."""
import io
from PIL import Image
from fastapi.testclient import TestClient


def create_test_image_bytes() -> bytes:
    """Helper to generate dummy RGB image in memory."""
    img = Image.new("RGB", (640, 480), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_predict_endpoint(client: TestClient):
    """Test POST /predict with a valid image file."""
    # 1. Seed at least one SKU so classification succeeds
    sku_payload = {
        "sku_id": "COCA_COLA_500ML_PET",
        "sku_name": "Coca-Cola Original 500ml PET",
        "brand": "Coca-Cola",
        "category": "soft_drink",
    }
    client.post("/skus", json=sku_payload)

    img_bytes = create_test_image_bytes()
    files = {"file": ("test_fridge.jpg", img_bytes, "image/jpeg")}
    
    response = client.post("/predict", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "model_version" in data
    assert "image_id" in data
    assert "total_bottles" in data
    assert "detections" in data
    assert "sku_counts" in data
    assert len(data["detections"]) > 0


def test_feedback_endpoint(client: TestClient):
    """Test POST /feedback submission and training sample enqueueing."""
    # Register SKU first
    sku_payload = {
        "sku_id": "SPRITE_500ML_PET",
        "sku_name": "Sprite Lemon Lime 500ml PET",
        "brand": "Sprite",
        "category": "soft_drink",
    }
    client.post("/skus", json=sku_payload)

    fb_payload = {
        "image_id": "test-img-123",
        "detection_id": "test-det-123",
        "predicted_sku_id": "COCA_COLA_500ML_PET",
        "corrected_sku_id": "SPRITE_500ML_PET",
        "comments": "Glare caused miss-classification",
    }

    res = client.post("/feedback", json=fb_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "queued_for_training"
    assert data["corrected_sku_id"] == "SPRITE_500ML_PET"


def test_model_status_endpoint(client: TestClient):
    """Test GET /model/status returns active version and validation metrics."""
    res = client.get("/model/status")
    assert res.status_code == 200
    data = res.json()
    assert "current_model_version" in data
    assert "validation_metrics" in data
