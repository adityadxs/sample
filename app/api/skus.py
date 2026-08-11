"""SKU Registry API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.schemas import SKUCreate, SKUResponse, SKUUpdate
from app.services.sku_service import sku_service

router = APIRouter(prefix="/skus", tags=["SKU Registry"])


@router.get(
    "",
    response_model=List[SKUResponse],
    status_code=status.HTTP_200_OK,
    summary="List SKUs",
    description="Retrieve all registered SKUs with optional filtering by brand, category, and active status.",
)
def list_skus(
    brand: Optional[str] = Query(None, description="Filter by brand name (case-insensitive substring)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    active: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
) -> List[SKUResponse]:
    """Return all matching SKUs."""
    return sku_service.get_skus(
        db=db,
        brand=brand,
        category=category,
        active=active,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=SKUResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new SKU",
    description="Register a new SKU in the registry. Validates uniqueness of sku_id.",
)
def create_sku(
    sku_in: SKUCreate,
    db: Session = Depends(get_db),
) -> SKUResponse:
    """Add a new SKU to the catalog."""
    try:
        return sku_service.create_sku(db=db, sku_in=sku_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get(
    "/{sku_id}",
    response_model=SKUResponse,
    status_code=status.HTTP_200_OK,
    summary="Get SKU by ID",
    description="Retrieve detailed SKU metadata by unique SKU identifier.",
)
def get_sku(
    sku_id: str,
    db: Session = Depends(get_db),
) -> SKUResponse:
    """Fetch single SKU details."""
    sku = sku_service.get_sku_by_id(db=db, sku_id=sku_id)
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU with ID '{sku_id}' not found.",
        )
    return sku


@router.put(
    "/{sku_id}",
    response_model=SKUResponse,
    status_code=status.HTTP_200_OK,
    summary="Update SKU",
    description="Update an existing SKU's attributes and metadata.",
)
def update_sku(
    sku_id: str,
    sku_in: SKUUpdate,
    db: Session = Depends(get_db),
) -> SKUResponse:
    """Update SKU information."""
    sku = sku_service.update_sku(db=db, sku_id=sku_id, sku_in=sku_in)
    if not sku:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU with ID '{sku_id}' not found.",
        )
    return sku


@router.delete(
    "/{sku_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete SKU",
    description="Remove an SKU from the registry.",
)
def delete_sku(
    sku_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """Delete an SKU record."""
    deleted = sku_service.delete_sku(db=db, sku_id=sku_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SKU with ID '{sku_id}' not found.",
        )
    return {"message": f"SKU '{sku_id}' deleted successfully"}
