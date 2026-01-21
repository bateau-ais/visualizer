"""
NOVA Visualizer Backend - NATS Subscriber

Listens to nova.fused topic and updates Redis with vessel positions.
"""

import asyncio
import json
import msgpack
from nats.aio.client import Client as NATS
from config import settings
# redis_service removed (Visualizer is now Read-Only for ingestion)
from models.vessel import VesselPosition
from api.websocket import broadcast_vessel_update, broadcast_anomaly
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
            logger.info(f"Connected to NATS at {settings.nats_url}")
        except Exception as e:
            logger.error(f"NATS connection failed: {e}")
            raise
    
    async def message_handler(self, msg):
        """Handle incoming NATS message."""
        try:
            # Parse MessagePack
            data = msgpack.unpackb(msg.data)
            
            # Map Almanach/Analyzer keys to Visualizer internal keys
            # EnrichedAISMessage/AnalysisResult -> Visualizer Schema
            vessel_name = data.get("vessel_name") or data.get("name")
            vessel_type = data.get("vessel_type") or data.get("type", "unknown")
            nav_status = data.get("nav_status") or data.get("status")
            
            # Raw anomaly status
            raw_is_anomaly = data.get("anomaly_detected") or data.get("is_anomaly", False)
            anomaly_score = data.get("anomaly_score", 0.0)
            
            # Apply hysteresis logic
            mmsi = data.get("mmsi")
            is_anomaly = raw_is_anomaly
            if mmsi:
                is_anomaly = await redis_service.update_anomaly_status(
                    mmsi,
                    raw_is_anomaly,
                    settings.anomaly_clean_frames_threshold
                )
            
            # Extract vessel position
            vessel_data = {
                "mmsi": data.get("mmsi"),
                "name": vessel_name,
                "imo": data.get("imo"),
                "type": str(vessel_type),
                "flag": data.get("flag"), # Usually derived or enriched elsewhere
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "sog": data.get("sog"),
                "cog": data.get("cog"),
                "heading": data.get("heading"),
                "timestamp": data.get("timestamp"),
                "anomaly_score": anomaly_score,
                "is_anomaly": is_anomaly,
                "status": nav_status
            }
            
            # Basic validation
            if not vessel_data["lat"] or not vessel_data["lon"]:
                return

            # Wrapper for existing WebSocket broadcast
            # We don't write to Redis anymore (Fusioner does it)
            
            # Broadcast update to WebSocket clients
            await broadcast_vessel_update(vessel_data)
            
            # If anomaly, broadcast it
            if is_anomaly:
                anomaly_data = {
                    "data_id": data.get("data_id"),
                    "mmsi": data["mmsi"],
                    "timestamp": data["timestamp"],
                    "score": anomaly_score,
                    "reasons": data.get("anomaly_reasons", []),
                    "confidence": data.get("confidence", 0.0),
                    "vessel_name": vessel_name,
                    "lat": data["lat"],
                    "lon": data["lon"]
                }
                
                # Broadcast anomaly
                await broadcast_anomaly(anomaly_data)
                
                logger.info(f"Anomaly detected (broadcast only): {data['mmsi']} (score={anomaly_data['score']:.2f})")
            
        except Exception as e:
            logger.error(f"Error processing NATS message: {e}")
    
    async def subscribe(self):
        """Subscribe to NATS subject."""
        try:
            await self.nc.subscribe(
                settings.nats_subject,
                cb=self.message_handler
            )
            logger.info(f"Subscribed to {settings.nats_subject}")
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
