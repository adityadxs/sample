"""Initial SKU registry seeder with representative beverage products."""
from sqlalchemy.orm import Session
from app.models.database_models import SKU, ModelVersion
from app.utils.logging import logger

DEFAULT_SKUS = [
    {
        "sku_id": "COCA_COLA_500ML_PET",
        "sku_name": "Coca-Cola Original 500ml PET",
        "brand": "Coca-Cola",
        "category": "soft_drink",
        "variant": "Original",
        "pack_type": "PET",
        "volume_ml": 500.0,
        "metadata_json": {"sugar_free": False, "barcode": "5449000000996"},
        "active": True,
    },
    {
        "sku_id": "COCA_COLA_300ML_CAN",
        "sku_name": "Coca-Cola Original 300ml Can",
        "brand": "Coca-Cola",
        "category": "soft_drink",
        "variant": "Original",
        "pack_type": "Can",
        "volume_ml": 300.0,
        "metadata_json": {"sugar_free": False, "barcode": "5449000014528"},
        "active": True,
    },
    {
        "sku_id": "COCA_COLA_ZERO_500ML_PET",
        "sku_name": "Coca-Cola Zero Sugar 500ml PET",
        "brand": "Coca-Cola",
        "category": "soft_drink",
        "variant": "Zero Sugar",
        "pack_type": "PET",
        "volume_ml": 500.0,
        "metadata_json": {"sugar_free": True, "barcode": "5449000131805"},
        "active": True,
    },
    {
        "sku_id": "PEPSI_500ML_PET",
        "sku_name": "Pepsi Cola 500ml PET",
        "brand": "Pepsi",
        "category": "soft_drink",
        "variant": "Original",
        "pack_type": "PET",
        "volume_ml": 500.0,
        "metadata_json": {"sugar_free": False, "barcode": "012000000133"},
        "active": True,
    },
    {
        "sku_id": "PEPSI_BLACK_500ML_PET",
        "sku_name": "Pepsi Black Max Taste 500ml PET",
        "brand": "Pepsi",
        "category": "soft_drink",
        "variant": "Black / Zero",
        "pack_type": "PET",
        "volume_ml": 500.0,
        "metadata_json": {"sugar_free": True, "barcode": "012000163357"},
        "active": True,
    },
    {
        "sku_id": "MOUNTAIN_DEW_500ML_PET",
        "sku_name": "Mountain Dew Citrus Blast 500ml PET",
        "brand": "Mountain Dew",
        "category": "soft_drink",
        "variant": "Citrus",
        "pack_type": "PET",
        "volume_ml": 500.0,
        "metadata_json": {"flavor": "Citrus", "barcode": "012000001291"},
        "active": True,
    },
    {
        "sku_id": "7UP_500ML_PET",
        "sku_name": "7UP Lemon Lime 500ml PET",
        "brand": "7UP",
        "category": "soft_drink",
        "variant": "Lemon Lime",
        "pack_type": "PET",
        "volume_ml": 500.0,
        "metadata_json": {"caffeine_free": True, "barcode": "078000000308"},
        "active": True,
    },
    {
        "sku_id": "SPRITE_500ML_PET",
        "sku_name": "Sprite Refreshing Lemon-Lime 500ml PET",
        "brand": "Sprite",
        "category": "soft_drink",
        "variant": "Lemon-Lime",
        "pack_type": "PET",
        "volume_ml": 500.0,
        "metadata_json": {"caffeine_free": True, "barcode": "049000000450"},
        "active": True,
    },
    {
        "sku_id": "STING_ENERGY_250ML_PET",
        "sku_name": "Sting Energy Drink Gold Rush 250ml PET",
        "brand": "Sting",
        "category": "energy_drink",
        "variant": "Gold Rush",
        "pack_type": "PET",
        "volume_ml": 250.0,
        "metadata_json": {"energy_boost": True, "barcode": "890208000120"},
        "active": True,
    },
    {
        "sku_id": "TROPICANA_ORANGE_1L_TETRA",
        "sku_name": "Tropicana 100% Orange Juice 1L Tetra",
        "brand": "Tropicana",
        "category": "juice",
        "variant": "100% Pure Orange",
        "pack_type": "Tetra",
        "volume_ml": 1000.0,
        "metadata_json": {"pure_juice": True, "barcode": "048500001234"},
        "active": True,
    },
]


def seed_database(db: Session) -> None:
    """Seed initial catalog of SKUs and default active model version."""
    if db.query(SKU).count() == 0:
        logger.info("Seeding initial SKU registry catalog...")
        for item in DEFAULT_SKUS:
            sku = SKU(**item)
            db.add(sku)
        db.commit()
        logger.info(f"Seeded {len(DEFAULT_SKUS)} default SKUs successfully.")

    if db.query(ModelVersion).count() == 0:
        initial_version = ModelVersion(
            version="v1.0.0",
            is_active=True,
            number_of_skus=len(DEFAULT_SKUS),
            training_samples_count=1200,
            validation_metrics={
                "top1_accuracy": 0.945,
                "top5_accuracy": 0.991,
                "macro_f1": 0.940,
                "old_sku_retention": 0.972,
            },
            status="active",
        )
        db.add(initial_version)
        db.commit()
        logger.info("Initialized default active model version v1.0.0.")
