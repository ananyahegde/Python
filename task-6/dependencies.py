from fastapi import HTTPException, status, Security, FastAPI
from fastapi.security import APIKeyHeader
import time

API_KEYS = {
    "api_key_a1b2c3": {"usage": 0, "last_reset": time.time()},
    "api_key_x9y8z7": {"usage": 0, "last_reset": time.time()},
    "api_key_m4n5o6": {"usage": 0, "last_reset": time.time()},
    "api_key_p7q8r9": {"usage": 0, "last_reset": time.time()},
    "api_key_j2k3l4": {"usage": 0, "last_reset": time.time()},
    "api_key_f5g6h7": {"usage": 0, "last_reset": time.time()},
    "api_key_t1u2v3": {"usage": 0, "last_reset": time.time()},
    "api_key_w4x5y6": {"usage": 0, "last_reset": time.time()},
    "api_key_n7o8p9": {"usage": 0, "last_reset": time.time()},
    "api_key_q1r2s3": {"usage": 0, "last_reset": time.time()},
    "api_key_b4c5d6": {"usage": 0, "last_reset": time.time()},
    "api_key_e7f8g9": {"usage": 0, "last_reset": time.time()},
    "api_key_h1i2j3": {"usage": 0, "last_reset": time.time()},
    "api_key_k4l5m6": {"usage": 0, "last_reset": time.time()},
    "api_key_z7a8b9": {"usage": 0, "last_reset": time.time()},
    "api_key_c1d2e3": {"usage": 0, "last_reset": time.time()},
    "api_key_r4s5t6": {"usage": 0, "last_reset": time.time()},
    "api_key_u7v8w9": {"usage": 0, "last_reset": time.time()},
    "api_key_y1z2a3": {"usage": 0, "last_reset": time.time()},
    "api_key_i4j5k6": {"usage": 0, "last_reset": time.time()},
}

api_key_header = APIKeyHeader(name="api-key")


def rate_limit_exceeded(api_key):
    if API_KEYS[api_key]["usage"] > 20:
        if time.time() - API_KEYS[api_key]["last_reset"] < 60:
            return True
        else:
            API_KEYS[api_key]["usage"] = 0
            API_KEYS[api_key]["last_reset"] = time.time()
            return False
    else:
        return False


def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header is None or api_key_header not in API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )

    if rate_limit_exceeded(api_key_header):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate Limit Exceeded",
        )

    API_KEYS[api_key_header]["usage"] += 1
    return api_key_header
