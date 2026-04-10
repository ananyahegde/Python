import aiohttp
from fastapi import Depends, FastAPI, HTTPException
from dependencies import get_api_key
import redis 
import json
import time
import asyncio

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
app = FastAPI()

service_stats = {
    "users": {"failures": 0, "status": "UP", "open": False, "last_failure": None, "cache_hits": 0, "total_latency": 0, "request_count": 0},
    "orders": {"failures": 0, "status": "UP", "open": False, "last_failure": None, "cache_hits": 0, "total_latency": 0, "request_count": 0},
    "products": {"failures": 0, "status": "UP", "open": False, "last_failure": None, "cache_hits": 0, "total_latency": 0, "request_count": 0},
}


@app.get("/api/users/{path:path}")
async def forward_users(path: str, _=Depends(get_api_key)):
    async with aiohttp.ClientSession() as session:
        result = r.get(f"cache:{path}")
        if result:
            service_stats['users']['cache_hits'] += 1
            r.set("stats:users", json.dumps(service_stats['users']))
            return json.loads(result)
        try:
            if service_stats['users']['open'] and time.time() - service_stats['users']['last_failure'] < 60:
                raise HTTPException(status_code=503, detail="Service unavailable")
            else:
                start_time = time.time()
                await asyncio.sleep(3)
                async with session.get(f"http://localhost:8000/users/{path}") as response:
                    data = await response.json()
                    r.set(f"cache:{path}", json.dumps(data), ex=60)
                    service_stats['users']['failures'] = 0
                    service_stats['users']['status'] = "UP"
                    service_stats['users']['open'] = False
                    service_stats['users']['request_count'] += 1
                    service_stats['users']['total_latency'] += time.time() - start_time
                    r.set("stats:users", json.dumps(service_stats['users']))
                    return data

        except aiohttp.client_exceptions.ClientConnectorError as e:
            service_stats['users']['failures'] += 1
            if service_stats['users']['failures'] > 4: 
                service_stats['users']['last_failure'] = time.time()
                service_stats['users']['status'] = "DOWN"
                service_stats['users']['open'] = True
            r.set("stats:users", json.dumps(service_stats['users']))
            raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/api/orders/{path:path}")
async def forward_orders(path: str, _=Depends(get_api_key)):
    async with aiohttp.ClientSession() as session:
        result = r.get(f"cache:{path}")
        if result:
            service_stats['orders']['cache_hits'] += 1
            r.set("stats:orders", json.dumps(service_stats['orders']))
            return json.loads(result)
        try:
            if service_stats['orders']['open'] and time.time() - service_stats['orders']['last_failure'] < 60:
                raise HTTPException(status_code=503, detail="Service unavailable")
            else:
                start_time = time.time()
                await asyncio.sleep(3)
                async with session.get(f"http://localhost:8002/orders/{path}") as response:
                    data = await response.json()
                    r.set(f"cache:{path}", json.dumps(data), ex=60)
                    service_stats['orders']['failures'] = 0
                    service_stats['orders']['status'] = "UP"
                    service_stats['orders']['open'] = False
                    service_stats['orders']['request_count'] += 1
                    service_stats['orders']['total_latency'] += time.time() - start_time
                    r.set("stats:orders", json.dumps(service_stats['orders']))
                    return data

        except aiohttp.client_exceptions.ClientConnectorError as e:
            service_stats['orders']['failures'] += 1
            if service_stats['orders']['failures'] > 4:
                service_stats['orders']['last_failure'] = time.time()
                service_stats['orders']['status'] = "DOWN"
                service_stats['orders']['open'] = True
            r.set("stats:orders", json.dumps(service_stats['orders']))
            raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/api/products/{path:path}")
async def forward_products(path: str, _=Depends(get_api_key)):
    async with aiohttp.ClientSession() as session:
        result = r.get(f"cache:{path}")
        if result:
            service_stats['products']['cache_hits'] += 1
            r.set("stats:products", json.dumps(service_stats['products']))
            return json.loads(result)
        try:
            if service_stats['products']['open'] and time.time() - service_stats['products']['last_failure'] < 60:
                raise HTTPException(status_code=503, detail="Service unavailable")
            else:
                start_time = time.time()
                await asyncio.sleep(3)
                async with session.get(f"http://localhost:8001/products/{path}") as response:
                    data = await response.json()
                    r.set(f"cache:{path}", json.dumps(data), ex=60)
                    service_stats['products']['failures'] = 0
                    service_stats['products']['status'] = "UP"
                    service_stats['products']['open'] = False
                    service_stats['products']['request_count'] += 1
                    service_stats['products']['total_latency'] += time.time() - start_time
                    r.set("stats:products", json.dumps(service_stats['products']))
                    return data

        except aiohttp.client_exceptions.ClientConnectorError as e:
            service_stats['products']['failures'] += 1
            if service_stats['products']['failures'] > 4:
                service_stats['products']['last_failure'] = time.time()
                service_stats['products']['status'] = "DOWN"
                service_stats['products']['open'] = True
            r.set("stats:products", json.dumps(service_stats['products']))
            raise HTTPException(status_code=503, detail="Service unavailable")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
