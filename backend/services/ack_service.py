"""
Acknowledgement service for managing acknowledged vessels.
Now uses Redis for persistence instead of in-memory storage.
"""

from datetime import datetime
from services.redis_service import redis_service


class AcknowledgementService:
    """Manage acknowledged vessels using Redis for persistence."""
    
    def __init__(self):
        """Initialize service. No in-memory storage needed."""
        pass
    
    async def acknowledge_vessel(self, mmsi: int) -> bool:
        """
        Mark a vessel as acknowledged.
        
        Args:
            mmsi: Vessel MMSI number
            
        Returns:
            True if newly acknowledged, False if already acknowledged
        """
        # Check if already acknowledged
        is_already_acked = await redis_service.is_acknowledged(mmsi)
        if is_already_acked:
            return False
        
        # Store in Redis
        await redis_service.store_acknowledgment(mmsi, datetime.utcnow())
        return True
    
    async def unacknowledge_vessel(self, mmsi: int) -> bool:
        """
        Remove acknowledgement from a vessel.
        
        Args:
            mmsi: Vessel MMSI number
            
        Returns:
            True if was acknowledged, False otherwise
        """
        # Check if was acknowledged
        is_acked = await redis_service.is_acknowledged(mmsi)
        if not is_acked:
            return False
        
        # Remove from Redis
        await redis_service.remove_acknowledgment(mmsi)
        return True
    
    async def is_acknowledged(self, mmsi: int) -> bool:
        """Check if vessel is acknowledged."""
        return await redis_service.is_acknowledged(mmsi)
    
    async def get_acknowledgement_time(self, mmsi: int) -> datetime | None:
        """Get time when vessel was acknowledged."""
        return await redis_service.get_acknowledgment_time(mmsi)
    
    async def get_all_acknowledged(self) -> list[dict]:
        """Get all acknowledged vessels."""
        return await redis_service.get_all_acknowledged()
    
    async def clear_all(self):
        """Clear all acknowledgements."""
        # Get all acknowledged vessels and remove them
        all_acked = await redis_service.get_all_acknowledged()
        for vessel in all_acked:
            await redis_service.remove_acknowledgment(vessel["mmsi"])


# Global instance
ack_service = AcknowledgementService()
