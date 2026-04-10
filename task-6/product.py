from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
import redis
import json

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class Product(BaseModel):
    name: str
    price: float
    category: str

@app.get("/products", status_code=status.HTTP_403_FORBIDDEN)
def get_products():
    return {"message": "Access Forbidden"}

@app.get("/products/{product_id}", status_code=status.HTTP_200_OK)
def get_product(product_id: int):
    product = r.get(f"product:{product_id}")
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**json.loads(product))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
