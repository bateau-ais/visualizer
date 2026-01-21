"""
NOVA Visualizer Backend - NATS Subscriber
=========================================

Listens to nova.fused topic and updates Redis with vessel positions.
"""

import asyncio
import json
import msgpack
from almanach.models.ais_messages import FusionResult
from almanach.subscription.subscriber import Subscriber
from config import settings
from api.websocket import broadcast_vessel_update, broadcast_anomaly
import logging

logger = logging.getLogger(__name__)


class NATSSubscriber:
    """NATS subscriber for fused AIS data."""
    
    def __init__(self):
        self.subscriber = Subscriber()
        self.pending_updates = {}
        self.batch_size = 50  # Broadcast every 50 vessels
        self.batch_interval = 0.5  # Or every 500ms
        self.last_flush = 0
        self._flush_task = None
    
    async def flush_batch(self):
        """Flush pending updates to WebSocket clients."""
        if not self.pending_updates:
            return

        try:
            # Convert values to list for broadcasting
            updates = list(self.pending_updates.values())
            
            # To avoid breaking existing API if backend doesn't support list, 
            # we iterate. But for real optimization, we should send the list.
            # Assuming broadcast_vessel_update handles single item.
            for update in updates:
                 await broadcast_vessel_update(update)
            
            self.pending_updates.clear()
            
        except Exception as e:
            logger.error(f"Error flushing batch: {e}")

    async def _scheduled_flush(self):
        """Flush batch periodically."""
        await asyncio.sleep(self.batch_interval)
        await self.flush_batch()
    
    async def message_handler(self, vessel_data: FusionResult):
        """Handle incoming NATS message from Fusioner."""
        try:
            # Broadcast update to WebSocket clients
            # Use model_dump to convert Pydantic model to dict
            data_dict = vessel_data.model_dump()
            # Ensure timestamp is string for JSON broadcasting
            if hasattr(vessel_data.timestamp, 'isoformat'):
                data_dict['timestamp'] = vessel_data.timestamp.isoformat()
            
            # Batching logic
            self.pending_updates[vessel_data.mmsi] = data_dict

            # Check if batch size reached
            if len(self.pending_updates) >= self.batch_size:
                await self.flush_batch()
            
            # Start time-based flush if not running
            if not self._flush_task or self._flush_task.done():
                self._flush_task = asyncio.create_task(self._scheduled_flush())
            
            # If anomaly, broadcast it IMMEDIATELLY (Fusioner already handled hysteresis & persistence)
            if vessel_data.is_anomaly:
                anomaly_data = {
                    "data_id": vessel_data.data_id,
                    "mmsi": vessel_data.mmsi,
                    "timestamp": data_dict['timestamp'],
                    "score": vessel_data.anomaly_score,
                    "reasons": vessel_data.reasons,
                    "confidence": vessel_data.confidence,
                    "vessel_name": vessel_data.name,
                    "lat": vessel_data.lat,
                    "lon": vessel_data.lon
                }
                
                await broadcast_anomaly(anomaly_data)
                logger.info(f"Anomaly broadcast: {vessel_data.mmsi} (score={vessel_data.anomaly_score:.2f})")
            
        except Exception as e:
            logger.error(f"Error processing NATS message: {e}")
    
    async def run(self):
        """Run subscriber (blocking)."""
        # Subscribe using Almanach Subscriber
        topic = f"{settings.nats_url}/{settings.nats_subject}"
        self.subscriber.subscribe(topic, validator=FusionResult, key="mmsi")(self.message_handler)

        logger.info(f"Visualizer subscribed to {settings.nats_subject} via Subscriber")
        
        # We need to run the pipeline. Since the Visualizer might already have a loop,
        # and we don't want to use Subscriber.run() which calls asyncio.run(),
        # we call the pipeline directly.
        pipeline = self.subscriber._pipelines[0]
        await pipeline()
    
    async def stop(self):
        """Stop subscriber."""
        # Current Subscriber doesn't expose a clean stop/close for its pipelines easily
        # but the process shutdown will handle it.
        logger.info("NATS subscriber stopping (handled by process shutdown)")


# Global instance
nats_subscriber = NATSSubscriber()
