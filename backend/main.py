"""
NOVA Visualizer Backend - Main FastAPI Application

Maritime anomaly detection visualization backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from config import settings
from api import vessels, anomalies, websocket
from services.redis_service import redis_service
from services.nats_subscriber import nats_subscriber

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events.
    """
    # Startup
    logger.info("🚀 Starting NOVA Visualizer Backend")
    
    try:
        # Connect to Redis
        await redis_service.connect()
        
        # Start NATS subscriber in background
        asyncio.create_task(nats_subscriber.run())
        
        logger.info("✅ All services started")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down gracefully...")
    
    await nats_subscriber.stop()
    await redis_service.disconnect()
    
    logger.info("👋 Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Maritime AIS Anomaly Detection Visualization API",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(vessels.router)
app.include_router(anomalies.router)
app.include_router(websocket.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    vessel_count = await redis_service.get_vessel_count()
    
    return {
        "status": "healthy",
        "redis": "connected",
        "nats": "connected",
        "vessels_tracked": vessel_count
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
