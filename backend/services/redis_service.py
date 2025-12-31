"""
NOVA Visualizer Backend - Redis Service

Handles all Redis operations for vessel positions and caching.
"""

import redis.asyncio as aioredis
import json
from typing import Optional, List
from datetime import datetime, timedelta
from config import settings
import logging

logger = logging.getLogger(__name__)


class RedisService:
    """Redis service for vessel data storage."""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis = await aioredis.from_url(
                f"redis://{settings.redis_host}:{settings.redis_port}",
                password=settings.redis_password,
                db=settings.redis_db,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")
    
    # --- Vessel Positions ---
    
    async def store_vessel_position(self, mmsi: int, data: dict):
        """Store vessel position with TTL."""
        key = f"vessel:position:{mmsi}"
        await self.redis.setex(
            key,
            settings.vessel_position_ttl,
            json.dumps(data)
        )
        
        # Add to active vessels set
        await self.redis.hset(
            "vessels:active",
            str(mmsi),
            datetime.utcnow().isoformat()
        )
    
    async def get_vessel_position(self, mmsi: int) -> Optional[dict]:
        """Get vessel position by MMSI."""
        key = f"vessel:position:{mmsi}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def get_all_vessels(self) -> List[dict]:
        """Get all active vessel positions."""
        mmsis = await self.redis.hkeys("vessels:active")
        if not mmsis:
            return []
        
        pipeline = self.redis.pipeline()
        for mmsi in mmsis:
            pipeline.get(f"vessel:position:{mmsi}")
        
        results = await pipeline.execute()
        vessels = []
        for data in results:
            if data:
                try:
                    vessels.append(json.loads(data))
                except json.JSONDecodeError:
                    continue
        
        return vessels
    
    # --- Trajectories ---
    
    async def store_trajectory_point(self, mmsi: int, lat: float, lon: float, timestamp: str):
        """Add point to vessel trajectory (ZSET with timestamp as score)."""
        key = f"vessel:trajectory:{mmsi}"
        point = json.dumps({"lat": lat, "lon": lon, "timestamp": timestamp})
        
        # Use timestamp as score
        ts = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        score = ts.timestamp()
        
        await self.redis.zadd(key, {point: score})
        
        # Keep only last 24h of trajectory
        cutoff = (datetime.utcnow() - timedelta(hours=24)).timestamp()
        await self.redis.zremrangebyscore(key, 0, cutoff)
    
    async def get_trajectory(self, mmsi: int, hours: int = 24) -> List[dict]:
        """Get vessel trajectory for last N hours."""
        key = f"vessel:trajectory:{mmsi}"
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).timestamp()
        
        points = await self.redis.zrangebyscore(key, cutoff, "+inf")
        return [json.loads(p) for p in points]
    
    # --- Anomalies ---
    
    async def store_anomaly(self, anomaly_data: dict):
        """Store anomaly in sorted set (recent anomalies)."""
        ts = datetime.fromisoformat(anomaly_data['timestamp'].replace('Z', '+00:00'))
        score = ts.timestamp()
        
        await self.redis.zadd(
            "anomalies:recent",
            {json.dumps(anomaly_data): score}
        )
        
        # Keep only last 7 days
        cutoff = (datetime.utcnow() - timedelta(days=7)).timestamp()
        await self.redis.zremrangebyscore("anomalies:recent", 0, cutoff)
    
    async def get_recent_anomalies(self, hours: int = 24, limit: int = 100) -> List[dict]:
        """Get recent anomalies."""
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).timestamp()
        
        results = await self.redis.zrangebyscore(
            "anomalies:recent",
            cutoff,
            "+inf",
            start=0,
            num=limit,
            withscores=False
        )
        
        return [json.loads(r) for r in results]
    
    # --- Heatmap Cache ---
    
    async def get_heatmap_cache(self, key: str) -> Optional[dict]:
        """Get cached heatmap."""
        data = await self.redis.get(f"heatmap:{key}")
        return json.loads(data) if data else None
    
    async def set_heatmap_cache(self, key: str, data: dict):
        """Cache heatmap with TTL."""
        await self.redis.setex(
            f"heatmap:{key}",
            settings.heatmap_cache_ttl,
            json.dumps(data)
        )
    
    # --- Stats ---
    
    async def get_vessel_count(self) -> int:
        """Get count of active vessels."""
        return await self.redis.hlen("vessels:active")


# Global instance
redis_service = RedisService()
