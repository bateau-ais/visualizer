"""
NOVA Visualizer Backend - Configuration

Centralized settings using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # App
    app_name: str = "NOVA Visualizer"
    app_version: str = "1.0.0"
    debug: bool = False
    demo_mode: bool = False  # Enable demo mode with mock data
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # NATS
    nats_url: str = "nats://localhost:4222"
    nats_subject: str = "nova.fused"
    
    # External APIs
    vesselfinder_api_key: Optional[str] = None
    marinetraffic_api_key: Optional[str] = None
    
    # CORS
    cors_origins_str: str = "http://localhost:5173,http://localhost:8000"
    
    @property
    def cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins_str.split(",")]
    
    # JWT Authentication
    jwt_secret_key: str = "INSECURE_DEFAULT_KEY_CHANGE_IN_PRODUCTION"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60
    
    # WebSocket
    ws_heartbeat_interval: int = 30  # seconds
    
    # Cache TTL
    vessel_position_ttl: int = 1800  # 30 minutes
    heatmap_cache_ttl: int = 300  # 5 minutes
    
    # Anomaly Logic
    anomaly_clean_frames_threshold: int = 10  # Number of clean frames to recover from anomaly
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = ""  # No prefix, use exact variable names
        fields = {
            'cors_origins_str': {'env': 'CORS_ORIGINS'}
        }


settings = Settings()
