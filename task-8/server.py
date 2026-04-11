import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sensor import generate_readings
from processor import process
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="app"), name="static")

connected_clients: list[WebSocket] = []

@app.get("/")
async def index():
    return FileResponse("app/index.html")

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    print(f"[INFO] Client connected — {len(connected_clients)} total")
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(ws)
        print(f"[INFO] Client disconnected — {len(connected_clients)} total")

async def broadcast():
    async for reading in generate_readings():
        result = process(reading)
        if result is None:
            continue
        data = json.dumps(result)
        for ws in connected_clients.copy():
            try:
                await ws.send_text(data)
            except:
                connected_clients.remove(ws)

@app.on_event("startup")
async def startup():
    print("[INFO] Stream processor started")
    asyncio.create_task(broadcast())

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True)
