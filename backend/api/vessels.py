"""
NOVA Visualizer Backend - Vessels API

REST endpoints for vessel data.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
from models.vessel import VesselPosition, VesselsResponse, VesselDetails, TrajectoryPoint, AnomalyDetail
from services.redis_service import redis_service
from services.vessel_api import vessel_api
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/vessels", tags=["vessels"])


@router.get("", response_model=VesselsResponse)
async def get_vessels(
    vessel_type: Optional[str] = Query(None, description="Filter by vessel type"),
    min_speed: Optional[float] = Query(None, description="Minimum speed (knots)"),
    max_speed: Optional[float] = Query(None, description="Maximum speed (knots)"),
    anomaly_only: bool = Query(False, description="Only anomalous vessels")
):
    """
    Get all active vessels with optional filters.
    """
    try:
        vessels_data = await redis_service.get_all_vessels()
        
        # Apply filters
        filtered = vessels_data
        
        if vessel_type:
            filtered = [v for v in filtered if v.get("type") == vessel_type]
        
        if min_speed is not None:
            filtered = [v for v in filtered if v.get("sog", 0) >= min_speed]
        
        if max_speed is not None:
            filtered = [v for v in filtered if v.get("sog", 0) <= max_speed]
        
        if anomaly_only:
            filtered = [v for v in filtered if v.get("is_anomaly", False)]
        
        # Convert to Pydantic models
        vessels = [VesselPosition(**v) for v in filtered]
        
        return VesselsResponse(
            vessels=vessels,
            total=len(vessels),
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Error fetching vessels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{mmsi}", response_model=VesselDetails)
async def get_vessel_details(mmsi: int):
    """
    Get detailed information for a specific vessel.
    """
    try:
        # Get current position
        vessel_data = await redis_service.get_vessel_position(mmsi)
        if not vessel_data:
            raise HTTPException(status_code=404, detail=f"Vessel {mmsi} not found")
        
        # Get trajectory (last 24h)
        trajectory_data = await redis_service.get_trajectory(mmsi, hours=24)
        trajectory = [TrajectoryPoint(**t) for t in trajectory_data]
        
        # Get anomalies
        # TODO: Query anomalies specific to this vessel from Redis
        anomalies = []
        
        # Get photo
        photo_url = await vessel_api.get_vessel_photo(mmsi)
        
        # Combine into VesselDetails
        details = VesselDetails(
            **vessel_data,
            trajectory=trajectory,
            anomalies=anomalies,
            photo_url=photo_url
        )
        
        return details
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vessel {mmsi}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
