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
        1. VesselFinder Scraper (Best effort)
        2. MarineTraffic (paid API)
        3. Fallback placeholder
        """
        
        # Try VesselFinder scraping
        if url := await self._scrape_vesselfinder(mmsi):
            return url
        
        # Try MarineTraffic (if API key available)
        if settings.marinetraffic_api_key:
            if url := await self._try_marinetraffic(mmsi):
                return url
        
        # Fallback to placeholder (using valid placeholder service if via.placeholder is down/blocked)
        # Using placeholder.com as fallback
        return f"https://placehold.co/300x200?text=MMSI+{mmsi}"
    
    async def _scrape_vesselfinder(self, mmsi: int) -> Optional[str]:
        """Scrape VesselFinder for vessel photo."""
        try:
            # First, search for the vessel page
            search_url = f"https://www.vesselfinder.com/vessels?name={mmsi}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            
            async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
                response = await client.get(search_url, timeout=10.0)
                if response.status_code != 200:
                    return None
                
                # Look for the photo in the page source
                # VesselFinder often has the photo in a meta tag or a specific div
                import re
                
                # Check for og:image meta tag first
                og_image_match = re.search(r'<meta property="og:image" content="([^"]+)"', response.text)
                if og_image_match:
                    image_url = og_image_match.group(1)
                    if "ship-photo" in image_url or "vesselphoto" in image_url:
                        return image_url

                # Fallback to searching for the thumbnail in search results if redirected to search list
                img_match = re.search(r'img class="ship-img" src="([^"]+)"', response.text)
                if img_match:
                    return img_match.group(1)
                    
        except Exception as e:
            logger.error(f"Scraping VesselFinder failed for {mmsi}: {e}")
        
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
