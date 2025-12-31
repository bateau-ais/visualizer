"""
NOVA Visualizer Backend - NATS Subscriber

Listens to nova.fused topic and updates Redis with vessel positions.
"""

import asyncio
import json
from nats.aio.client import Client as NATS
from config import settings
from services.redis_service import redis_service
import logging

logger = logging.getLogger(__name__)


class NATSSubscriber:
    """NATS subscriber for fused AIS data."""
    
    def __init__(self):
        self.nc = NATS()
        self.running = False
    
    async def connect(self):
        """Connect to NATS."""
        try:
            await self.nc.connect(settings.nats_url)
            logger.info(f"✅ Connected to NATS at {settings.nats_url}")
        except Exception as e:
            logger.error(f"❌ NATS connection failed: {e}")
            raise
    
    async def message_handler(self, msg):
        """Handle incoming NATS message."""
        try:
            data = json.loads(msg.data.decode())
            
            # Extract vessel position
            vessel_data = {
                "mmsi": data.get("mmsi"),
                "name": data.get("name"),
                "imo": data.get("imo"),
                "type": data.get("type", "unknown"),
                "flag": data.get("flag"),
                "lat": data["lat"],
                "lon": data["lon"],
                "sog": data["sog"],
                "cog": data["cog"],
                "heading": data.get("heading"),
                "timestamp": data["timestamp"],
                "anomaly_score": data.get("anomaly_score", 0.0),
                "is_anomaly": data.get("is_anomaly", False),
                "status": data.get("status")
            }
            
            # Store in Redis
            await redis_service.store_vessel_position(
                data["mmsi"],
                vessel_data
            )
            
            # Store trajectory point
            await redis_service.store_trajectory_point(
                data["mmsi"],
                data["lat"],
                data["lon"],
                data["timestamp"]
            )
            
            # If anomaly, store it
            if data.get("is_anomaly"):
                anomaly_data = {
                    "data_id": data.get("data_id"),
                    "mmsi": data["mmsi"],
                    "timestamp": data["timestamp"],
                    "score": data.get("anomaly_score", 0.0),
                    "reasons": data.get("anomaly_reasons", []),
                    "confidence": data.get("confidence", 0.0),
                    "vessel_name": data.get("name"),
                    "lat": data["lat"],
                    "lon": data["lon"]
                }
                await redis_service.store_anomaly(anomaly_data)
                logger.info(f"🔴 Anomaly detected: {data['mmsi']} (score={anomaly_data['score']:.2f})")
            
        except Exception as e:
            logger.error(f"Error processing NATS message: {e}")
    
    async def subscribe(self):
        """Subscribe to NATS subject."""
        try:
            await self.nc.subscribe(
                settings.nats_subject,
                cb=self.message_handler
            )
            logger.info(f"📡 Subscribed to {settings.nats_subject}")
            self.running = True
        except Exception as e:
            logger.error(f"NATS subscription failed: {e}")
            raise
    
    async def run(self):
        """Run subscriber (blocking)."""
        await self.connect()
        await self.subscribe()
        
        # Keep running
        while self.running:
            await asyncio.sleep(1)
    
    async def stop(self):
        """Stop subscriber."""
        self.running = False
        await self.nc.drain()
        await self.nc.close()
        logger.info("NATS subscriber stopped")


# Global instance
nats_subscriber = NATSSubscriber()
