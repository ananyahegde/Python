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
        data.get(b"retries", b"").decode('utf-8') if data.get(b"retries") else "",
        data.get(b"remark", b"").decode('utf-8') if data.get(b"remark") else "",
        data.get(b"timestamp", b"").decode('utf-8') if data.get(b"timestamp") else ""
    ])

print("\n=== TASKS STATUS ===")
print(tabulate(rows, headers=["task_id", "status", "retries", "duration", "remark", "timestamp"], tablefmt="grid"))

dead_keys = r.lrange("dead_queue", 0, -1)
dead_rows = []
for item in dead_keys:
    task = json.loads(item)
    dead_rows.append([task.get("id"), task.get("func"), task.get("retries"), "DEAD"])

print("\n=== DEAD LETTER QUEUE ===")
print(tabulate(dead_rows, headers=["task_id", "func", "retries", "status"], tablefmt="grid"))
