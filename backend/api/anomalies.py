"""
NOVA Visualizer Backend - Anomalies API

REST endpoints for anomaly data and heatmaps.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Optional
from models.anomaly import AnomalyEvent, DashboardStats, HeatmapResponse, HeatmapCell
from services.redis_service import redis_service
from collections import defaultdict
from config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/anomalies", tags=["anomalies"])

# Import mock data if in demo mode
if settings.demo_mode:
    from services.mock_data import mock_generator


@router.get("", response_model=list[AnomalyEvent])
async def get_anomalies(
    hours: int = Query(24, description="Time window in hours"),
    min_score: float = Query(0.0, description="Minimum anomaly score"),
    limit: int = Query(100, description="Maximum results")
):
    """
    Get recent anomalies.
    """
    try:
        # Demo mode: use mock data
        if settings.demo_mode:
            anomalies_data = [a.model_dump() for a in mock_generator.get_anomalies(hours)]
        else:
            anomalies_data = await redis_service.get_recent_anomalies(hours=hours, limit=limit)
        
        # Filter by score
        filtered = [a for a in anomalies_data if a.get("score", 0) >= min_score]
        
        # Convert to Pydantic models
        anomalies = []
        
        # Import ack_service inside function to avoid circular imports if any
        from services.ack_service import ack_service
        
        for a in filtered:
            # Check if acknowledged
            mmsi = a.get("mmsi")
            is_acked = await ack_service.is_acknowledged(mmsi) if mmsi else False
            
            # Create model with acknowledged status
            anomaly = AnomalyEvent(
                **a,
                acknowledged=is_acked
            )
            anomalies.append(anomaly)
        
        return anomalies
    
    except Exception as e:
        logger.error(f"Error fetching anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_heatmap(
    resolution: float = Query(0.1, description="Grid resolution in degrees"),
    period: str = Query("24h", description="Time period: 24h, 7d, 30d"),
    anomaly_type: Optional[str] = Query(None, description="Filter by anomaly type")
):
    """
    Get heatmap of anomaly distribution.
    """
    try:
        # Parse period
        period_hours = {
            "24h": 24,
            "7d": 168,
            "30d": 720
        }.get(period, 24)
        
        # Demo mode: generate mock heatmap data
        if settings.demo_mode:
            anomalies_data = [a.model_dump() for a in mock_generator.get_anomalies(period_hours)]
        else:
            # Check cache
            cache_key = f"{resolution}:{period}:{anomaly_type or 'all'}"
            cached = await redis_service.get_heatmap_cache(cache_key)
            
            if cached:
                return HeatmapResponse(**cached)
            
            # Get anomalies from Redis
            anomalies_data = await redis_service.get_recent_anomalies(hours=period_hours, limit=10000)
        
        # Filter by type if specified
        if anomaly_type and anomaly_type != 'all':
            anomalies_data = [
                a for a in anomalies_data
                if any(anomaly_type in str(reason) for reason in a.get("reasons", []))
            ]
        
        # Build grid
        grid = defaultdict(lambda: {"count": 0, "scores": [], "types": []})
        
        for anomaly in anomalies_data:
            if anomaly.get("lat") is None or anomaly.get("lon") is None:
                continue
            
            lat = anomaly["lat"]
            lon = anomaly["lon"]
            
            # Snap to grid
            lat_cell = int(lat / resolution) * resolution
            lon_cell = int(lon / resolution) * resolution
            
            cell_key = (lat_cell, lon_cell)
            grid[cell_key]["count"] += 1
            grid[cell_key]["scores"].append(anomaly.get("score", 0))
            grid[cell_key]["types"].extend(anomaly.get("reasons", []))
        
        # Convert to HeatmapCells
        cells = []
        for (lat_min, lon_min), data in grid.items():
            # Calculate top types
            type_counts = defaultdict(int)
            for t in data["types"]:
                type_counts[str(t)] += 1
            top_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            
            cell = HeatmapCell(
                lat_min=lat_min,
                lat_max=lat_min + resolution,
                lon_min=lon_min,
                lon_max=lon_min + resolution,
                count=data["count"],
                avg_score=sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0,
                top_types=[t[0] for t in top_types]
            )
            cells.append(cell)
        
        # Build response
        response_data = {
            "cells": [c.model_dump() for c in cells],
            "resolution": resolution,
            "period": period,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Cache it (only in production mode)
        if not settings.demo_mode:
            await redis_service.set_heatmap_cache(cache_key, response_data)
        
        return HeatmapResponse(**response_data)
    
    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """
    Get dashboard statistics.
    """
    try:
        # Demo mode: use mock data
        if settings.demo_mode:
            stats = mock_generator.get_stats()
            return DashboardStats(**stats)
        
        # Count active vessels
        vessels_active = await redis_service.get_vessel_count()
        
        # Count anomalies in last 24h
        anomalies_data = await redis_service.get_recent_anomalies(hours=24, limit=10000)
        anomalies_24h = len(anomalies_data)
        
        # Detection rate
        detection_rate = (anomalies_24h / vessels_active * 100) if vessels_active > 0 else 0
        
        # Critical count (score > 0.8)
        critical_count = len([a for a in anomalies_data if a.get("score", 0) > 0.8])
        
        return DashboardStats(
            vessels_active=vessels_active,
            anomalies_24h=anomalies_24h,
            detection_rate=round(detection_rate, 2),
            critical_count=critical_count,
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
