import aiohttp
from fastapi import Depends, FastAPI, HTTPException
from dependencies import get_api_key
import redis 
import json
import time

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
app = FastAPI()

circuit_breakers = {
    "users": {"failures": 0, "open": False, "last_failure": None},
    "orders": {"failures": 0, "open": False, "last_failure": None},
    "products": {"failures": 0, "open": False, "last_failure": None},
}


@app.get("/api/users/{path:path}")
async def forward_users(path: str, _=Depends(get_api_key)):
    async with aiohttp.ClientSession() as session:
        result = r.get(f"cache:{path}")
        if result:
            return json.loads(result)
        try:
            if circuit_breakers['users']['open'] and time.time() - circuit_breakers['users']['last_failure'] < 60:
                raise HTTPException(status_code=503, detail="Service unavailable")
            else:
                time.sleep(3)
                async with session.get(f"http://localhost:8000/users/{path}") as response:
                    data = await response.json()
                    r.set(f"cache:{path}", json.dumps(data), ex=60)
                    circuit_breakers['users']['failures'] = 0
                    circuit_breakers['users']['open'] = False
                    return data

        except aiohttp.client_exceptions.ClientConnectorError as e:
            circuit_breakers['users']['failures'] += 1
            if circuit_breakers['users']['failures'] > 4: 
                circuit_breakers['users']['last_failure'] = time.time()
                circuit_breakers['users']['open'] = True
            raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/api/orders/{path:path}")
async def forward_orders(path: str, _=Depends(get_api_key)):
    async with aiohttp.ClientSession() as session:
        result = r.get(f"cache:{path}")
        if result:
            return json.loads(result)
        try:
            if circuit_breakers['orders']['open'] and time.time() - circuit_breakers['orders']['last_failure'] < 60:
                raise HTTPException(status_code=503, detail="Service unavailable")
            else:
                time.sleep(3)
                async with session.get(f"http://localhost:8002/orders/{path}") as response:
                    data = await response.json()
                    r.set(f"cache:{path}", json.dumps(data), ex=60)
                    circuit_breakers['orders']['failures'] = 0
                    circuit_breakers['orders']['open'] = False
                    return data
        except aiohttp.client_exceptions.ClientConnectorError as e:
            circuit_breakers['orders']['failures'] += 1
            if circuit_breakers['orders']['failures'] > 4:
                circuit_breakers['orders']['last_failure'] = time.time()
                circuit_breakers['orders']['open'] = True
            raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/api/products/{path:path}")
async def forward_products(path: str, _=Depends(get_api_key)):
    async with aiohttp.ClientSession() as session:
        result = r.get(f"cache:{path}")
        if result:
            return json.loads(result)
        try:
            if circuit_breakers['products']['open'] and time.time() - circuit_breakers['products']['last_failure'] < 60:
                raise HTTPException(status_code=503, detail="Service unavailable")
            else:
                time.sleep(3)
                async with session.get(f"http://localhost:8001/products/{path}") as response:
                    data = await response.json()
                    r.set(f"cache:{path}", json.dumps(data), ex=60)
                    circuit_breakers['products']['failures'] = 0
                    circuit_breakers['products']['open'] = False
                    return data
        except aiohttp.client_exceptions.ClientConnectorError as e:
            circuit_breakers['products']['failures'] += 1
            if circuit_breakers['products']['failures'] > 4:
                circuit_breakers['products']['last_failure'] = time.time()
                circuit_breakers['products']['open'] = True
            raise HTTPException(status_code=503, detail="Service unavailable")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
