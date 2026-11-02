"""Main FastAPI application entry point."""

from fastapi import FastAPI
from app.core.config import settings
from app.api.v1 import telemetry, copilot

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Hyper-Local Smallholder Crop & Irrigation Copilot",
)

# Include routers
app.include_router(telemetry.router, prefix=settings.API_V1_STR)
app.include_router(copilot.router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.PROJECT_NAME}