"""
NOVA Visualizer - User Models
==============================

Pydantic models for user management and authentication.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, Literal
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    VIEWER = "viewer"  # Read-only access
    OPERATOR = "operator"  # Can acknowledge anomalies
    ADMIN = "admin"  # Full access


class User(BaseModel):
    """User model for authentication."""
    username: str = Field(..., min_length=3, max_length=50)
    hashed_password: str
    role: UserRole = UserRole.VIEWER
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must be alphanumeric (with _ and - allowed)')
        return v.lower()


class UserCreate(BaseModel):
    """Model for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.VIEWER


class UserLogin(BaseModel):
    """Model for user login."""
    username: str
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: dict


class TokenData(BaseModel):
    """Token payload data."""
    username: str
    role: str


class AnomalyAcknowledgement(BaseModel):
    """Model for anomaly acknowledgement with traceability."""
    id: str  # UUID generated on creation
    mmsi: int
    anomaly_id: str  # Reference to the anomaly
    acknowledged_by: str  # Username
    acknowledged_at: datetime = Field(default_factory=datetime.utcnow)
    action_taken: Literal["investigate", "ignore", "escalate", "resolved"]
    comment: Optional[str] = None
    resolution_time: Optional[datetime] = None


class AcknowledgeRequest(BaseModel):
    """Request model for acknowledging an anomaly."""
    mmsi: int
    action_taken: Literal["investigate", "ignore", "escalate", "resolved"]
    comment: Optional[str] = Field(None, max_length=500)
