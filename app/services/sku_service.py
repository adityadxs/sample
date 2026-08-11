"""SKU Registry service providing business logic and database operations for SKUs."""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.database_models import SKU
from app.models.schemas import SKUCreate, SKUUpdate
from app.utils.logging import logger


class SKUService:
    """Service layer for SKU management in the registry."""

    @staticmethod
    def get_sku_by_id(db: Session, sku_id: str) -> Optional[SKU]:
        """Fetch a single SKU by its unique identifier."""
        statement = select(SKU).where(SKU.sku_id == sku_id)
        return db.scalar(statement)

    @staticmethod
    def get_skus(
        db: Session,
        brand: Optional[str] = None,
        category: Optional[str] = None,
        active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SKU]:
        """Query SKUs with optional filtering."""
        query = select(SKU)
        if brand is not None:
            query = query.where(SKU.brand.ilike(f"%{brand}%"))
        if category is not None:
            query = query.where(SKU.category.ilike(f"%{category}%"))
        if active is not None:
            query = query.where(SKU.active == active)
        
        query = query.order_by(SKU.brand, SKU.sku_name).offset(offset).limit(limit)
        return list(db.scalars(query).all())

    @staticmethod
    def create_sku(db: Session, sku_in: SKUCreate) -> SKU:
        """Create a new SKU with uniqueness validation."""
        existing = SKUService.get_sku_by_id(db, sku_in.sku_id)
        if existing:
            raise ValueError(f"SKU with ID '{sku_in.sku_id}' already exists.")

        sku = SKU(
            sku_id=sku_in.sku_id,
            sku_name=sku_in.sku_name,
            brand=sku_in.brand,
            category=sku_in.category,
            variant=sku_in.variant,
            pack_type=sku_in.pack_type,
            volume_ml=sku_in.volume_ml,
            metadata_json=sku_in.metadata_json or {},
            active=sku_in.active,
        )
        db.add(sku)
        db.commit()
        db.refresh(sku)
        logger.info(f"Registered new SKU: {sku.sku_id} ({sku.sku_name} - {sku.brand})")
        return sku

    @staticmethod
    def update_sku(db: Session, sku_id: str, sku_in: SKUUpdate) -> Optional[SKU]:
        """Update an existing SKU."""
        sku = SKUService.get_sku_by_id(db, sku_id)
        if not sku:
            return None

        update_data = sku_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(sku, field, value)

        db.commit()
        db.refresh(sku)
        logger.info(f"Updated SKU: {sku.sku_id}")
        return sku

    @staticmethod
    def delete_sku(db: Session, sku_id: str) -> bool:
        """Delete an SKU record if found."""
        sku = SKUService.get_sku_by_id(db, sku_id)
        if not sku:
            return False

        db.delete(sku)
        db.commit()
        logger.info(f"Deleted SKU: {sku_id}")
        return True

    @staticmethod
    def count_active_skus(db: Session) -> int:
        """Count the total number of active SKUs."""
        query = select(SKU).where(SKU.active.is_(True))
        return len(list(db.scalars(query).all()))


sku_service = SKUService()
