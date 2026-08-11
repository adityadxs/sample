"""Health check and system status endpoint."""
from datetime import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.models.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check API runtime status and database connectivity.",
)
def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """Validate database connectivity and return overall health status."""
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        database_connected=db_connected,
        timestamp=datetime.utcnow(),
    )
