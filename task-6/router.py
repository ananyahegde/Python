import aiohttp
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/users/{path:path}")
async def forward_users(path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://localhost:8000/users/{path}") as response:
            return await response.json()

@app.get("/api/products/{path:path}")
async def forward_users(path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://localhost:8001/products/{path}") as response:
            return await response.json()

@app.get("/api/orders/{path:path}")
async def forward_users(path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://localhost:8002/orders/{path}") as response:
            return await response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
