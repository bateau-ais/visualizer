"""
NOVA Visualizer Backend - Anomaly Models
"""

from pydantic import BaseModel
from datetime import datetime


class AnomalyEvent(BaseModel):
    """Real-time anomaly event."""
    data_id: str
    mmsi: int
    timestamp: datetime
    score: float
    reasons: list[str]
    confidence: float
    vessel_name: str | None = None
    lat: float | None = None
    lon: float | None = None


class HeatmapCell(BaseModel):
    """Heatmap grid cell."""
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float
    count: int
    avg_score: float
    top_types: list[str]


class HeatmapResponse(BaseModel):
    """Response for GET /heatmap."""
    cells: list[HeatmapCell]
    resolution: float
    period: str
    timestamp: datetime


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    vessels_active: int
    anomalies_24h: int
    detection_rate: float
    critical_count: int
    timestamp: datetime
