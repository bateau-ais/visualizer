"""
NOVA Visualizer Backend - Redis Service

Handles all Redis operations for vessel positions and caching.
"""

import redis.asyncio as aioredis
import json
from typing import Optional, List, Set
from datetime import datetime, timedelta
from config import settings
from models.vessel import VesselPosition, TrajectoryPoint, AnomalyDetail
from models.anomaly import AnomalyEvent, DashboardStats
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
                decode_responses=True,
                max_connections=50,        # Limit connection pool
                socket_timeout=5.0,        # Fail fast on network issues
                socket_connect_timeout=5.0 # Fail fast on connection
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

    async def get_vessels_summary(self) -> List[dict]:
        """
        Get simplified vessel data for fast loading.
        Includes only: mmsi, lat, lon, name, type, is_anomaly, anomaly_score.
        """
        vessels = await self.get_all_vessels()
        summary = []
        for v in vessels:
            summary.append({
                "mmsi": v.get("mmsi"),
                "lat": v.get("lat"),
                "lon": v.get("lon"),
                "name": v.get("name"),
                "type": v.get("type"),
                "is_anomaly": v.get("is_anomaly", False),
                "anomaly_score": v.get("anomaly_score", 0.0)
            })
        return summary
    
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
        """Get vessel trajectory for last N hours (relative to latest point)."""
        key = f"vessel:trajectory:{mmsi}"
        
        # 1. Get latest point score to handle historical data
        latest = await self.redis.zrange(key, -1, -1, withscores=True)
        if latest:
            max_ts = latest[0][1]
            cutoff = max_ts - (hours * 3600)
        else:
            cutoff = (datetime.utcnow() - timedelta(hours=hours)).timestamp()
        
        points = await self.redis.zrangebyscore(key, cutoff, "+inf")
        # Limit to last 2000 points to prevent payload explosion
        if len(points) > 2000:
             # Take every Nth point to downsample if needed, or just last 2000
             # For now, just taking the last 2000
             points = points[-2000:]
        if not points:
            return []
            
        # Downsampling simple (décimation) si trop de points
        MAX_POINTS = 500
        if len(points) > MAX_POINTS:
            step = len(points) // MAX_POINTS
            points = points[::step]
            
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
        
        # Cleanup global (keep a healthy buffer, e.g. last 10000 anomalies or 7 days)
        # For historical data, absolute time cleanup is dangerous. 
        # Better: keep last 10000 or use a very large sliding window if not specified.
        await self.redis.zremrangebyrank("anomalies:recent", 0, -10001)

        # Also store in vessel-specific history
        vessel_key = f"vessel:anomalies:{anomaly_data['mmsi']}"
        await self.redis.zadd(
            vessel_key,
            {json.dumps(anomaly_data): score}
        )
        # Keep only last 50 anomalies per vessel
        await self.redis.zremrangebyrank(vessel_key, 0, -51)

    async def update_anomaly_status(self, mmsi: int, is_anomaly: bool, threshold: int) -> bool:
        """
        Update anomaly status with hysteresis.
        Returns the effective status (True for anomaly, False for normal).
        If existing anomaly:
          - New anomaly frame -> reset clean counter -> True
          - Clean frame -> increment clean counter. If < threshold -> True. If >= threshold -> False (and clear).
        If no existing anomaly:
          - New anomaly frame -> stored as anomaly -> True
          - Clean frame -> False
        """
        key = f"vessel:clean_frames:{mmsi}"
        
        if is_anomaly:
            # Reset clean frames counter and mark as anomaly
            await self.redis.set(key, 0)
            await self.redis.expire(key, settings.vessel_position_ttl)
            return True
        else:
            # Check if we are in recovery mode
            if await self.redis.exists(key):
                count = await self.redis.incr(key)
                await self.redis.expire(key, settings.vessel_position_ttl)
                
                if count < threshold:
                    return True  # Still in anomaly state (recovering)
                else:
                    # Recovery complete
                    await self.redis.delete(key)
                    return False
            else:
                return False
    
    async def get_recent_anomalies(self, hours: int = 24, limit: int = 100) -> List[dict]:
        """Get recent anomalies (relative to latest anomaly or absolute time)."""
        # 1. Get the latest anomaly timestamp to handle historical datasets
        latest = await self.redis.zrange("anomalies:recent", -1, -1, withscores=True)
        
        if latest:
            # Relative window based on data
            max_ts = latest[0][1]
            cutoff = max_ts - (hours * 3600)
        else:
            # Fallback to absolute time
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

    async def get_vessel_anomalies(self, mmsi: int, limit: int = 50) -> List[dict]:
        """Get anomalies for a specific vessel."""
        key = f"vessel:anomalies:{mmsi}"
        
        # Get all anomalies for this vessel (newest first)
        results = await self.redis.zrevrange(
            key,
            0,
            limit - 1
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
    
    # --- Acknowledgments ---
    
    async def store_acknowledgment(self, mmsi: int, timestamp: datetime):
        """Store vessel acknowledgment in Redis."""
        key = f"vessel:acknowledged:{mmsi}"
        await self.redis.set(key, timestamp.isoformat())
        
        # Add to set of all acknowledged vessels
        await self.redis.sadd("vessels:all_acknowledged", str(mmsi))
    
    async def remove_acknowledgment(self, mmsi: int):
        """Remove vessel acknowledgment from Redis."""
        key = f"vessel:acknowledged:{mmsi}"
        await self.redis.delete(key)
        
        # Remove from set of all acknowledged vessels
        await self.redis.srem("vessels:all_acknowledged", str(mmsi))
    
    async def is_acknowledged(self, mmsi: int) -> bool:
        """Check if vessel is acknowledged."""
        key = f"vessel:acknowledged:{mmsi}"
        return await self.redis.exists(key) > 0
    
    async def get_acknowledgment_time(self, mmsi: int) -> Optional[datetime]:
        """Get time when vessel was acknowledged."""
        key = f"vessel:acknowledged:{mmsi}"
        timestamp_str = await self.redis.get(key)
        if timestamp_str:
            return datetime.fromisoformat(timestamp_str)
        return None
    
    async def get_all_acknowledged_mmsis(self) -> Set[int]:
        """Get set of all acknowledged MMSIs."""
        mmsis = await self.redis.smembers("vessels:all_acknowledged")
        return {int(m) for m in mmsis}

    async def get_all_acknowledged(self) -> List[dict]:
        """Get all acknowledged vessels."""
        mmsis = await self.redis.smembers("vessels:all_acknowledged")
        if not mmsis:
            return []
        
        result = []
        for mmsi_str in mmsis:
            mmsi = int(mmsi_str)
            ack_time = await self.get_acknowledgment_time(mmsi)
            if ack_time:
                result.append({
                    "mmsi": mmsi,
                    "acknowledged_at": ack_time.isoformat()
                })
        
        return result
    
    # --- Stats ---
    
    async def get_vessel_count(self) -> int:
        """Get count of active vessels."""
        return await self.redis.hlen("vessels:active")


# Global instance
redis_service = RedisService()
