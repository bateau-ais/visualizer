"""
Acknowledgement service for managing acknowledged vessels.
"""

from datetime import datetime
from typing import Set


class AcknowledgementService:
    """Manage acknowledged vessels in memory."""
    
    def __init__(self):
        self.acknowledged_vessels: Set[int] = set()
        self.acknowledgement_times: dict[int, datetime] = {}
    
    def acknowledge_vessel(self, mmsi: int) -> bool:
        """
        Mark a vessel as acknowledged.
        
        Args:
            mmsi: Vessel MMSI number
            
        Returns:
            True if newly acknowledged, False if already acknowledged
        """
        if mmsi in self.acknowledged_vessels:
            return False
        
        self.acknowledged_vessels.add(mmsi)
        self.acknowledgement_times[mmsi] = datetime.utcnow()
        return True
    
    def unacknowledge_vessel(self, mmsi: int) -> bool:
        """
        Remove acknowledgement from a vessel.
        
        Args:
            mmsi: Vessel MMSI number
            
        Returns:
            True if was acknowledged, False otherwise
        """
        if mmsi not in self.acknowledged_vessels:
            return False
        
        self.acknowledged_vessels.remove(mmsi)
        self.acknowledgement_times.pop(mmsi, None)
        return True
    
    def is_acknowledged(self, mmsi: int) -> bool:
        """Check if vessel is acknowledged."""
        return mmsi in self.acknowledged_vessels
    
    def get_acknowledgement_time(self, mmsi: int) -> datetime | None:
        """Get time when vessel was acknowledged."""
        return self.acknowledgement_times.get(mmsi)
    
    def get_all_acknowledged(self) -> list[dict]:
        """Get all acknowledged vessels."""
        return [
            {
                "mmsi": mmsi,
                "acknowledged_at": self.acknowledgement_times[mmsi].isoformat()
            }
            for mmsi in self.acknowledged_vessels
        ]
    
    def clear_all(self):
        """Clear all acknowledgements."""
        self.acknowledged_vessels.clear()
        self.acknowledgement_times.clear()


# Global instance
ack_service = AcknowledgementService()
