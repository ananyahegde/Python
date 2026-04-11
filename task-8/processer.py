from collections import deque
import statistics


WINDOW_SIZE = 20

ZSCORE_THRESHOLD = 2.5
TEMP_THRESHOLD = 38       # temperature (in celsius) threshold
VIBRATION_THRESHOLD = 0.5 # vibration (g-force) threshold

windows = {
    "T1": {"temp": deque(maxlen=WINDOW_SIZE), "vibration": deque(maxlen=WINDOW_SIZE)},
    "T2": {"temp": deque(maxlen=WINDOW_SIZE), "vibration": deque(maxlen=WINDOW_SIZE)},
}

def process(reading):
    w = windows[reading["sensor_id"]]
    w["temp"].append(reading["temperature"])
    w["vibration"].append(reading["vibration"])

    if len(w["temp"]) < 2:
        return None

    moving_avg_temp = statistics.mean(w["temp"])
    moving_avg_vibration = statistics.mean(w["vibration"])

    stdev_temp = statistics.stdev(w["temp"])
    stdev_vibration = statistics.stdev(w["vibration"])

    z_score_temp = (reading["temperature"] - moving_avg_temp) / stdev_temp
    z_score_vibration = (reading["vibration"] - moving_avg_vibration) / stdev_vibration

    return {
        "sensor_id": reading["sensor_id"],
        "timestamp": reading["timestamp"],
        "temperature": reading["temperature"],
        "vibration": reading["vibration"],
        "avg_temp": moving_avg_temp,
        "avg_vibration": moving_avg_vibration,
        "z_temp": z_score_temp,
        "z_vibration": z_score_vibration,
    }
