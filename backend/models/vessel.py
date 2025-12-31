"""
NOVA Visualizer Backend - Pydantic Models

Data models for vessels and anomalies.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VesselPosition(BaseModel):
    """Current vessel position."""
    mmsi: int
    name: Optional[str] = None
    imo: Optional[int] = None
    type: str = "unknown"
    flag: Optional[str] = None
    lat: float
    lon: float
    sog: float  # Speed over ground (knots)
    cog: float  # Course over ground (degrees)
    heading: Optional[int] = None
    timestamp: datetime
    anomaly_score: float = 0.0
    is_anomaly: bool = False
    status: Optional[str] = None


class TrajectoryPoint(BaseModel):
    """Single point in vessel trajectory."""
    lat: float
    lon: float
    timestamp: datetime
    sog: Optional[float] = None
    cog: Optional[float] = None


class VesselDimensions(BaseModel):
    """Vessel physical dimensions."""
    length: int  # meters
    beam: int  # meters
    draft: int  # meters


class AnomalyDetail(BaseModel):
    """Detailed anomaly information."""
    timestamp: datetime
    score: float
    reasons: list[str]
    details: Optional[str] = None
    confidence: float


class VesselDetails(VesselPosition):
    """Extended vessel information."""
    dimensions: Optional[VesselDimensions] = None
    trajectory: list[TrajectoryPoint] = []
    anomalies: list[AnomalyDetail] = []
    photo_url: Optional[str] = None


class VesselsResponse(BaseModel):
    """Response for GET /vessels."""
    vessels: list[VesselPosition]
    total: int
    timestamp: datetime
