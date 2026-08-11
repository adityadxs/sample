"""Tests for SKU registry API and service."""
from fastapi.testclient import TestClient


def test_create_and_get_sku(client: TestClient):
    """Test creating a new SKU and retrieving it."""
    payload = {
        "sku_id": "COCA_COLA_500ML_PET",
        "sku_name": "Coca-Cola Original 500ml PET",
        "brand": "Coca-Cola",
        "category": "soft_drink",
        "variant": "Original",
        "pack_type": "PET",
        "volume_ml": 500.0,
        "metadata_json": {"sugar_content": "standard", "barcode": "8901234567890"},
        "active": True,
    }

    # 1. Create SKU
    res = client.post("/skus", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["sku_id"] == "COCA_COLA_500ML_PET"
    assert created["brand"] == "Coca-Cola"
    assert created["volume_ml"] == 500.0
    assert created["metadata_json"]["barcode"] == "8901234567890"

    # 2. Get SKU by ID
    res_get = client.get("/skus/COCA_COLA_500ML_PET")
    assert res_get.status_code == 200
    fetched = res_get.json()
    assert fetched["sku_id"] == "COCA_COLA_500ML_PET"
    assert fetched["sku_name"] == "Coca-Cola Original 500ml PET"


def test_create_duplicate_sku_fails(client: TestClient):
    """Test that registering duplicate SKU ID returns 409 Conflict."""
    payload = {
        "sku_id": "PEPSI_500ML_PET",
        "sku_name": "Pepsi 500ml PET",
        "brand": "Pepsi",
        "category": "soft_drink",
    }
    res1 = client.post("/skus", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/skus", json=payload)
    assert res2.status_code == 409
    assert "already exists" in res2.json()["detail"]


def test_filter_skus(client: TestClient):
    """Test listing SKUs with brand, category, and active status filters."""
    skus_to_seed = [
        {
            "sku_id": "COKE_300ML_CAN",
            "sku_name": "Coca-Cola 300ml Can",
            "brand": "Coca-Cola",
            "category": "soft_drink",
            "active": True,
        },
        {
            "sku_id": "SPRITE_500ML_PET",
            "sku_name": "Sprite 500ml PET",
            "brand": "Sprite",
            "category": "soft_drink",
            "active": True,
        },
        {
            "sku_id": "MINUTE_MAID_ORANGE_1L",
            "sku_name": "Minute Maid Orange 1L",
            "brand": "Minute Maid",
            "category": "juice",
            "active": False,
        },
    ]

    for s in skus_to_seed:
        r = client.post("/skus", json=s)
        assert r.status_code == 201

    # Filter by brand
    res_brand = client.get("/skus?brand=Coca")
    assert res_brand.status_code == 200
    coke_list = res_brand.json()
    assert len(coke_list) == 1
    assert coke_list[0]["sku_id"] == "COKE_300ML_CAN"

    # Filter by category
    res_cat = client.get("/skus?category=juice")
    assert res_cat.status_code == 200
    juice_list = res_cat.json()
    assert len(juice_list) == 1
    assert juice_list[0]["sku_id"] == "MINUTE_MAID_ORANGE_1L"

    # Filter by active
    res_active = client.get("/skus?active=true")
    assert res_active.status_code == 200
    active_list = res_active.json()
    assert len(active_list) == 2


def test_update_and_delete_sku(client: TestClient):
    """Test updating and deleting an SKU."""
    payload = {
        "sku_id": "TEST_SKU_1",
        "sku_name": "Test SKU",
        "brand": "Test Brand",
        "category": "water",
        "active": True,
    }
    client.post("/skus", json=payload)

    # Update
    update_payload = {"sku_name": "Updated Test SKU Name", "active": False}
    res_up = client.put("/skus/TEST_SKU_1", json=update_payload)
    assert res_up.status_code == 200
    assert res_up.json()["sku_name"] == "Updated Test SKU Name"
    assert res_up.json()["active"] is False

    # Delete
    res_del = client.delete("/skus/TEST_SKU_1")
    assert res_del.status_code == 200

    # Verify not found
    res_get = client.get("/skus/TEST_SKU_1")
    assert res_get.status_code == 404
