import sys
import os
import unittest
from unittest.mock import MagicMock, AsyncMock

# Adjust path to include backend
# Assuming we run from project root or backend dir
current_dir = os.getcwd()
if "visualizer" not in current_dir:
     sys.path.append(os.path.join(current_dir, "visualizer", "backend"))
elif "backend" not in current_dir:
     sys.path.append(os.path.join(current_dir, "backend"))
else:
     sys.path.append(current_dir)

# Try imports
try:
    from services.redis_service import RedisService
    from config import settings
except ImportError:
    # If generic path failed, try specific absolute path assuming standard structure
    sys.path.append(r".")
    from services.redis_service import RedisService
    from config import settings

class TestAnomalyLogic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.service = RedisService()
        self.service.redis = AsyncMock()
        
    async def test_hysteresis(self):
        mmsi = 123456789
        threshold = 3
        key = f"vessel:clean_frames:{mmsi}"
        
        print("\nTesting Normal Frame (No History)...")
        # 1. Normal frame, no history
        self.service.redis.exists.return_value = 0
        status = await self.service.update_anomaly_status(mmsi, False, threshold)
        self.assertFalse(status, "Should be Normal")
        self.service.redis.set.assert_not_called()
        
        print("Testing Anomaly Frame...")
        # 2. Anomaly frame
        status = await self.service.update_anomaly_status(mmsi, True, threshold)
        self.assertTrue(status, "Should be Anomaly")
        self.service.redis.set.assert_called_with(key, 0)
        
        print("Testing Recovery Frame 1/3...")
        # 3. Recovering - Frame 1 (Clean)
        # Mock that key exists and incr returns 1
        self.service.redis.exists.return_value = 1
        self.service.redis.incr.return_value = 1
        
        status = await self.service.update_anomaly_status(mmsi, False, threshold)
        self.assertTrue(status, "Should still be Anomaly (1/3)")
        
        print("Testing Recovery Frame 2/3...")
        # 4. Recovering - Frame 2 (Clean)
        self.service.redis.incr.return_value = 2
        status = await self.service.update_anomaly_status(mmsi, False, threshold)
        self.assertTrue(status, "Should still be Anomaly (2/3)")
        
        print("Testing Recovery Frame 3/3 (Recovered)...")
        # 5. Recovering - Frame 3 (Clean) -> Recovered
        self.service.redis.incr.return_value = 3
        status = await self.service.update_anomaly_status(mmsi, False, threshold)
        self.assertFalse(status, "Should be Normal (3/3)")
        self.service.redis.delete.assert_called_with(key)
        
        print("Testing Anomaly Recurrence...")
        # 6. New Anomaly
        self.service.redis.set.reset_mock()
        status = await self.service.update_anomaly_status(mmsi, True, threshold)
        self.assertTrue(status, "Should be Anomaly again")
        self.service.redis.set.assert_called_with(key, 0)

if __name__ == '__main__':
    unittest.main()
