import redis
import json
import random

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry",
         "Iris", "Jack", "Karen", "Leo", "Mia", "Noah", "Olivia", "Paul",
         "Quinn", "Rose", "Sam", "Tina"]

items = ["Laptop", "Phone", "Headphones", "Monitor", "Keyboard", "Mouse",
         "Tablet", "Camera", "Speaker", "Charger"]

statuses = ["pending", "shipped", "delivered", "cancelled"]

categories = ["Electronics", "Accessories", "Audio", "Computing", "Mobile"]

for i, name in enumerate(names, start=1):
    user = {"id": i, "name": name, "email": f"{name.lower()}@example.com", "age": random.randint(18, 60)}
    r.set(f"user:{i}", json.dumps(user))

for i in range(1, 21):
    order = {
        "id": i,
        "user_id": random.randint(1, 20),
        "item": random.choice(items),
        "status": random.choice(statuses),
        "total": round(random.uniform(20, 1500), 2)
    }
    r.set(f"order:{i}", json.dumps(order))

for i, item in enumerate(items * 2, start=1):
    product = {
        "id": i,
        "name": item,
        "category": random.choice(categories),
        "price": round(random.uniform(10, 2000), 2),
        "stock": random.randint(0, 500)
    }
    r.set(f"product:{i}", json.dumps(product))

print("Seeded 20 users, 20 orders, 20 products into Redis")
