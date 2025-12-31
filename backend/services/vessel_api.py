"""
NOVA Visualizer Backend - Vessel API Service

External API calls for vessel photos and information.
"""

import httpx
from typing import Optional
from config import settings
import logging

logger = logging.getLogger(__name__)


class VesselAPIService:
    """External vessel API service."""
    
    async def get_vessel_photo(self, mmsi: int) -> Optional[str]:
        """
        Get vessel photo URL from external API.
        
        Priority:
        1. VesselFinder (free up to 1000/day)
        2. MarineTraffic (paid)
        3. Fallback placeholder
        """
        
        # Try VesselFinder (free)
        if url := await self._try_vesselfinder(mmsi):
            return url
        
        # Try MarineTraffic (if API key available)
        if settings.marinetraffic_api_key:
            if url := await self._try_marinetraffic(mmsi):
                return url
        
        # Fallback to placeholder
        return f"https://via.placeholder.com/300x200?text=MMSI+{mmsi}"
    
    async def _try_vesselfinder(self, mmsi: int) -> Optional[str]:
        """Try VesselFinder API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://www.vesselfinder.com/api/pub/vesselphoto/{mmsi}",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("url")
        except Exception as e:
            logger.debug(f"VesselFinder API failed for {mmsi}: {e}")
        
        return None
    
    async def _try_marinetraffic(self, mmsi: int) -> Optional[str]:
        """Try MarineTraffic API (requires paid key)."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.marinetraffic.com/api/exportvessel/v:5/{settings.marinetraffic_api_key}/MMSI:{mmsi}/protocol:jsono",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("PHOTO")
        except Exception as e:
            logger.debug(f"MarineTraffic API failed for {mmsi}: {e}")
        
        return None


# Global instance
vessel_api = VesselAPIService()
