from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
import redis
import json

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class Order(BaseModel):
    id: int
    user_id: int
    status: str
    total: float

@app.get("/orders", status_code=status.HTTP_403_FORBIDDEN)
def get_orders():
    return {"message": "Access Forbidden"}

@app.get("/orders/{order_id}", status_code=status.HTTP_200_OK)
def get_order(order_id: int):
    order = r.get(f"order:{order_id}")
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**json.loads(order))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
