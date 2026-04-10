import redis
import json
import random
import time
import uuid

r = redis.Redis(decode_responses=True)

tasks = [
    {"func": "send_welcome_email", "args": ["We are thrilled to inform you that you won 1 million lottery!"], "retries": 0},
    {"func": "resize_product_image", "args": [42, 999, 999], "retries": 0},
    {"func": "process_payment", "args": [100000, "credit card"], "retries": 0},
    {"func": "backup_database", "args": [], "retries": 0},
    {"func": "send_slack_notification", "args": ["Tee-Hee!"], "retries": 0},
    {"func": "sync_to_crm", "args": [999], "retries": 0},
]

print("[PRODUCER] Queueing tasks...")
start_time = time.time()
r.set("global_start_time", start_time)

for task in tasks:
    time.sleep(random.randint(0, 3))

    task_id = str(uuid.uuid4())[:8]
    task["id"] = task_id

    r.lpush("task_queue", json.dumps(task))
    print(f"[PRODUCER] Task queued: <Task id={task_id} func={task['func']} status=PENDING>")
