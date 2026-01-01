"""
NOVA Visualizer - Mock Data Generator

Generates realistic fake vessel data for demo mode.
"""

import random
from datetime import datetime, timedelta
from typing import List
from models.vessel import VesselPosition
from models.anomaly import AnomalyEvent


# Vessel names and types
VESSEL_NAMES = [
    "MAERSK ESSEX", "MSC FLORIDA", "CMA CGM PARIS", "EVER GIVEN", "COSCO SHIPPING",
    "APL CHINA", "HAPAG LLOYD", "ONE INNOVATION", "YANG MING MARINE", "ZIM KINGSTON",
    "SEA-LAND MERCURY", "HYUNDAI CONFIDENT", "MOL TRIUMPH", "NYK ARTEMIS", "K-LINE PEGASUS",
    "ATLANTIC STAR", "PACIFIC PEARL", "NORDIC OCEAN", "BALTIC SEA", "ARCTIC VOYAGER"
]

VESSEL_TYPES = ["cargo", "tanker", "passenger", "fishing", "unknown"]

# Geographic zones (European waters - WATER ONLY)
ZONES = {
    "english_channel": {"lat": (49.5, 50.5), "lon": (-2.0, 1.5)},  # Between UK and France
    "north_sea": {"lat": (54.0, 57.5), "lon": (2.5, 6.0)},  # North Sea proper
    "mediterranean": {"lat": (41.5, 43.0), "lon": (4.0, 8.0)},  # Western Mediterranean
    "atlantic": {"lat": (45.5, 48.5), "lon": (-10.0, -6.5)},  # Atlantic Ocean
    "baltic": {"lat": (55.5, 58.0), "lon": (16.0, 20.0)}  # Baltic Sea
}


class MockDataGenerator:
    """Generate realistic mock vessel data."""
    
    def __init__(self, num_vessels: int = 50):
        self.num_vessels = num_vessels
        self.vessels: List[VesselPosition] = []
        self.anomalies: List[AnomalyEvent] = []
        self._generate_vessels()
    
    def _generate_vessels(self):
        """Generate initial vessel fleet."""
        for i in range(self.num_vessels):
            # Random zone
            zone = random.choice(list(ZONES.values()))
            
            # Random position in zone
            lat = random.uniform(zone["lat"][0], zone["lat"][1])
            lon = random.uniform(zone["lon"][0], zone["lon"][1])
            
            # Random vessel properties
            mmsi = 200000000 + i  # Valid MMSI range
            vessel_type = random.choice(VESSEL_TYPES)
            
            # Realistic speeds based on type
            speed_ranges = {
                "cargo": (8, 18),
                "tanker": (10, 16),
                "passenger": (18, 25),
                "fishing": (5, 12),
                "unknown": (5, 20)
            }
            sog = random.uniform(*speed_ranges.get(vessel_type, (5, 20)))
            
            # Random heading
            cog = random.uniform(0, 360)
            heading = int(cog + random.uniform(-5, 5)) % 360
            
            # 20% chance of anomaly
            is_anomaly = random.random() < 0.2
            anomaly_score = random.uniform(0.5, 0.95) if is_anomaly else random.uniform(0, 0.3)
            
            vessel = VesselPosition(
                mmsi=mmsi,
                name=f"{random.choice(VESSEL_NAMES)}-{i}" if random.random() > 0.1 else None,
                imo=random.randint(1000000, 9999999) if random.random() > 0.3 else None,
                type=vessel_type,
                flag=random.choice(["US", "GB", "FR", "DE", "NL", "DK", "NO"]),
                lat=lat,
                lon=lon,
                sog=sog,
                cog=cog,
                heading=heading,
                timestamp=datetime.utcnow(),
                anomaly_score=anomaly_score,
                is_anomaly=is_anomaly,
                status=random.choice(["underway", "anchored", "moored", "not_under_command"])
            )
            
            self.vessels.append(vessel)
            
            # Generate anomaly event if applicable
            if is_anomaly:
                reasons = []
                if anomaly_score > 0.8:
                    reasons.append(random.choice(["SPOOFING_TELEPORTATION_LIKELY", "SPOOFING_IMPOSSIBLE_SPEED"]))
                if anomaly_score > 0.6:
                    reasons.append(random.choice(["SPEED_SPIKE", "VELOCITY_VARIANCE_HIGH"]))
                if len(reasons) == 0:
                    reasons.append("HEADING_CHANGE")
                
                anomaly = AnomalyEvent(
                    data_id=f"demo-{mmsi}-{datetime.utcnow().timestamp()}",
                    mmsi=mmsi,
                    timestamp=datetime.utcnow(),
                    score=anomaly_score,
                    reasons=reasons,
                    confidence=anomaly_score,
                    vessel_name=vessel.name,
                    lat=lat,
                    lon=lon
                )
                self.anomalies.append(anomaly)
    
    def update_vessels(self):
        """Update vessel positions (simulate movement)."""
        for vessel in self.vessels:
            # Move vessel slightly
            speed_km_per_hour = vessel.sog * 1.852  # knots to km/h
            speed_km_per_second = speed_km_per_hour / 3600
            
            # Calculate new position (simplified, assumes flat earth for small distances)
            delta_lat = (speed_km_per_second * random.uniform(0.8, 1.2) * 
                        random.choice([-1, 1]) / 111.32)  # 1 degree lat ≈ 111.32 km
            delta_lon = (speed_km_per_second * random.uniform(0.8, 1.2) * 
                        random.choice([-1, 1]) / (111.32 * abs(vessel.lat)))
            
            vessel.lat += delta_lat
            vessel.lon += delta_lon
            
            # Occasionally change course slightly
            if random.random() < 0.1:
                vessel.cog = (vessel.cog + random.uniform(-10, 10)) % 360
                vessel.heading = int(vessel.cog + random.uniform(-5, 5)) % 360
            
            # Occasionally change speed
            if random.random() < 0.05:
                vessel.sog = max(0, vessel.sog + random.uniform(-2, 2))
            
            # Update timestamp
            vessel.timestamp = datetime.utcnow()
            
            # Small chance to create new anomaly
            if random.random() < 0.01:
                vessel.is_anomaly = True
                vessel.anomaly_score = random.uniform(0.6, 0.9)
    
    def get_vessels(self) -> List[VesselPosition]:
        """Get all vessels."""
        return self.vessels
    
    def get_vessel_by_mmsi(self, mmsi: int) -> VesselPosition | None:
        """Get specific vessel."""
        for vessel in self.vessels:
            if vessel.mmsi == mmsi:
                return vessel
        return None
    
    def get_vessel_trajectory(self, mmsi: int, hours: int = 24):
        """Generate mock trajectory for a vessel."""
        vessel = self.get_vessel_by_mmsi(mmsi)
        if not vessel:
            return []
        
        from models.vessel import TrajectoryPoint
        
        # Generate trajectory points (one per hour)
        trajectory = []
        for i in range(hours):
            # Simulate backward movement from current position
            lat_offset = (i * 0.01) * random.choice([-1, 1])
            lon_offset = (i * 0.01) * random.choice([-1, 1])
            
            point = TrajectoryPoint(
                lat=vessel.lat + lat_offset,
                lon=vessel.lon + lon_offset,
                timestamp=datetime.utcnow() - timedelta(hours=hours-i),
                sog=vessel.sog + random.uniform(-2, 2),
                cog=vessel.cog + random.uniform(-10, 10)
            )
            trajectory.append(point)
        
        return trajectory
    
    def get_anomalies(self, hours: int = 24) -> List[AnomalyEvent]:
        """Get recent anomalies."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [a for a in self.anomalies if a.timestamp >= cutoff]
    
    def get_stats(self):
        """Get dashboard stats."""
        return {
            "vessels_active": len(self.vessels),
            "anomalies_24h": len([v for v in self.vessels if v.is_anomaly]),
            "detection_rate": (len([v for v in self.vessels if v.is_anomaly]) / len(self.vessels) * 100),
            "critical_count": len([v for v in self.vessels if v.anomaly_score > 0.8]),
            "timestamp": datetime.utcnow()
        }


# Global instance
mock_generator = MockDataGenerator(num_vessels=50)
