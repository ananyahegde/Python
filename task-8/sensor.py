import random
import asyncio
from datetime import datetime

SENSORS = ["T1", "T2"]

BASELINE = {
    "T1": {"temp": 72.0, "vibration": 0.12},
    "T2": {"temp": 68.0, "vibration": 0.10},
}

async def generate_readings():
   while True:
        for sensor_id in SENSORS:
            base = BASELINE[sensor_id]

            temp = base["temp"] + random.uniform(-2, 2)
            vibration = base["vibration"] + random.uniform(-0.02, 0.02)

            # ~5% chance of spike to simulate anomaly
            if random.random() < 0.05:
                temp += random.uniform(14, 22)
                vibration += random.uniform(0.3, 0.6)

            yield {
                "sensor_id": sensor_id,
                "temperature": round(temp, 2),
                "vibration": round(vibration, 3),
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }

        await asyncio.sleep(1)
