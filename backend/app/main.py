from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.projects import router as projects_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.governance import router as governance_router
from app.api.v1.admin import router as admin_router
from app.api.v1.submissions import router as submissions_router
from app.api.v1.network import router as network_router
from app.api.v1.positive_deviance import router as positive_deviance_router
from app.api.v1.simulate import router as simulate_router
from app.api.v1.imports import router as imports_router
from app.api.v1.data_health import router as data_health_router
from app.api.v1.audit import router as audit_router
from app.api.v1.reports import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    from app.scheduler import start_scheduler
    from pathlib import Path
    from app.services.model_loader import initialize_model_loader
    from app.core.config import settings
    
    # Initialize model loader with trained ML artifacts
    initialize_model_loader(Path(settings.data_dir))
    
    start_scheduler()
    yield
    # Shutdown
    from app.scheduler import stop_scheduler
    stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="PAIMANA-AI: Proactive AI-driven Infrastructure Monitoring and Anomaly Navigation System",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all v1 routers
app.include_router(projects_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(governance_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(submissions_router, prefix="/api/v1")
app.include_router(network_router, prefix="/api/v1")
app.include_router(positive_deviance_router, prefix="/api/v1")
app.include_router(simulate_router, prefix="/api/v1")
app.include_router(imports_router, prefix="/api/v1")
app.include_router(data_health_router, prefix="/api/v1")
app.include_router(audit_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name}
