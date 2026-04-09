import redis
from tabulate import tabulate

r = redis.Redis()
keys = r.keys("task:*")

rows = []

for key in keys:
    data = r.hgetall(key)
    rows.append([
        key.decode('utf-8'),
        data.get(b"status", b"").decode('utf-8') if data.get(b"status") else "",
        data.get(b"duration", b"").decode('utf-8') if data.get(b"duration") else "",
        data.get(b"remark", b"").decode('utf-8') if data.get(b"remark") else "",
        data.get(b"timestamp", b"").decode('utf-8') if data.get(b"timestamp") else ""
    ])

print(tabulate(rows, headers=["task_id", "status", "duration", "remark", "timestamp"], tablefmt="grid"))
