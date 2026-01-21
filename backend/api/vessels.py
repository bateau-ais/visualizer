from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
from models.vessel import VesselPosition, VesselsResponse, VesselDetails, TrajectoryPoint, AnomalyDetail
from services.redis_service import redis_service
from services.vessel_api import vessel_api
from services.ack_service import ack_service
from config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/vessels", tags=["vessels"])

# Import mock data if in demo mode
if settings.demo_mode:
    from services.mock_data import mock_generator


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
        # Demo mode: use mock data
        if settings.demo_mode:
            vessels_data = [v.model_dump() for v in mock_generator.get_vessels()]
        else:
            vessels_data = await redis_service.get_all_vessels()
        
        # Add acknowledgement status to each vessel
        for vessel in vessels_data:
            vessel['acknowledged'] = await ack_service.is_acknowledged(vessel['mmsi'])
        
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
        
        return VesselsResponse(
            vessels=[VesselPosition(**v) for v in filtered],
            total=len(filtered),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error fetching vessels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=VesselsResponse)
async def search_vessels(q: str = Query(..., description="Search query (MMSI or name)")):
    """
    Search vessels by MMSI or name.
    """
    try:
        # Demo mode: use mock data
        if settings.demo_mode:
            vessels_data = [v.model_dump() for v in mock_generator.get_vessels()]
        else:
            vessels_data = await redis_service.get_all_vessels()
        
        # Add acknowledgement status to each vessel
        for vessel in vessels_data:
            vessel['acknowledged'] = await ack_service.is_acknowledged(vessel['mmsi'])
        
        # Filter by search query
        query = q.lower().strip()
        filtered = []
        
        for vessel in vessels_data:
            # Search by MMSI (exact or partial match)
            if query in str(vessel['mmsi']):
                filtered.append(vessel)
                continue
            
            # Search by name (case-insensitive partial match)
            vessel_name = vessel.get('name', '').lower()
            if vessel_name and query in vessel_name:
                filtered.append(vessel)
                continue
        
        # Limit results to 10 for dropdown
        filtered = filtered[:10]
        
        return VesselsResponse(
            vessels=[VesselPosition(**v) for v in filtered],
            total=len(filtered),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Error searching vessels: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{mmsi}", response_model=VesselDetails)
async def get_vessel_details(mmsi: int):
    """
    Get detailed information for a specific vessel.
    """
    try:
        # Demo mode: use mock data
        if settings.demo_mode:
            vessel = mock_generator.get_vessel_by_mmsi(mmsi)
            if not vessel:
                raise HTTPException(status_code=404, detail=f"Vessel {mmsi} not found")
            
            vessel_data = vessel.model_dump()
            # Mock trajectory (last 24h positions)
            trajectory = mock_generator.get_vessel_trajectory(mmsi, hours=24)
            # Mock anomalies
            anomalies = []
        else:
            # Get current position
            vessel_data = await redis_service.get_vessel_position(mmsi)
            if not vessel_data:
                raise HTTPException(status_code=404, detail=f"Vessel {mmsi} not found")
            
            # Get trajectory (last 24h)
            trajectory_data = await redis_service.get_trajectory(mmsi, hours=24)
            trajectory = [TrajectoryPoint(**t) for t in trajectory_data]
            
            # Get anomalies
            anomalies_data = await redis_service.get_vessel_anomalies(mmsi)
            anomalies = [AnomalyDetail(**a) for a in anomalies_data]
        
        # Get photo
        photo_url = await vessel_api.get_vessel_photo(mmsi)
        
        # Add acknowledgement status
        vessel_data['acknowledged'] = await ack_service.is_acknowledged(mmsi)
        ack_time = await ack_service.get_acknowledgement_time(mmsi)
        if ack_time:
            vessel_data['acknowledged_at'] = ack_time.isoformat()
        
        return VesselDetails(
            **vessel_data,
            trajectory=trajectory,
            anomalies=anomalies,
            photo_url=photo_url
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vessel details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{mmsi}/acknowledge")
async def acknowledge_vessel(mmsi: int):
    """
    Acknowledge a vessel anomaly.
    """
    try:
        newly_acknowledged = await ack_service.acknowledge_vessel(mmsi)
        
        return {
            "mmsi": mmsi,
            "acknowledged": True,
            "newly_acknowledged": newly_acknowledged,
            "acknowledged_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error acknowledging vessel {mmsi}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{mmsi}/acknowledge")
async def unacknowledge_vessel(mmsi: int):
    """
    Remove acknowledgement from a vessel.
    """
    try:
        was_acknowledged = await ack_service.unacknowledge_vessel(mmsi)
        
        return {
            "mmsi": mmsi,
            "acknowledged": False,
            "was_acknowledged": was_acknowledged
        }
        
    except Exception as e:
        logger.error(f"Error unacknowledging vessel {mmsi}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/acknowledged/list")
async def get_acknowledged_vessels():
    """
    Get list of all acknowledged vessels.
    """
    try:
        acknowledged_list = await ack_service.get_all_acknowledged()
        return {
            "acknowledged_vessels": acknowledged_list,
            "total": len(acknowledged_list)
        }
        
    except Exception as e:
        logger.error(f"Error getting acknowledged vessels: {e}")
        raise HTTPException(status_code=500, detail=str(e))
