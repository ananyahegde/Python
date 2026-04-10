from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
import redis
import json

app = FastAPI()
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class User(BaseModel):
    name: str
    email: str
    age: int

@app.get("/users", status_code=status.HTTP_403_FORBIDDEN)
def get_users():
    return {"message": "Access Forbidden"}

@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
def get_user(user_id: int):
    user_data = r.get(f"user:{user_id}")
    
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    user_dict = json.loads(user_data)
    return User(**user_dict)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
