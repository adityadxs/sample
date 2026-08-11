"""FastAPI main application entry point."""
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.config import settings
from app.db.base import Base
from app.db.seed import seed_database
from app.db.session import SessionLocal, engine
from app.utils.logging import logger

STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan event handler."""
    logger.info(f"Starting up {settings.APP_NAME} v{settings.APP_VERSION} [{settings.APP_ENV}]...")
    # Initialize storage directories
    settings.init_directories()
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    # Seed default SKUs if database is empty
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    logger.info("Storage directories, database schema, and initial SKU registry verified.")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production-oriented API system for detecting bottles inside transparent beverage refrigerators "
        "and identifying exact product SKUs with continual/online learning and catastrophic forgetting protection."
    ),
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Middleware for assigning request UUID and logging execution latency."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000.0
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} -> {response.status_code} ({process_time:.2f}ms)"
    )
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Centralized uncaught exception handler."""
    logger.error(f"Unhandled server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred.", "error": str(exc)},
    )


# Mount static assets directory
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# Include API routes (both root and versioned prefixes)
app.include_router(api_router)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["UI"])
def root_ui():
    """Serve the Web UI dashboard on root."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "health_url": "/health",
    }


@app.get("/dashboard", tags=["UI"])
def dashboard_ui():
    """Serve the Web UI dashboard."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"detail": "Dashboard template not found"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
