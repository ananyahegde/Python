import redis
import json
import time
import datetime
from tasks import (
        send_welcome_email, 
        resize_product_image, 
        process_payment, 
        backup_database, 
        send_slack_notification, 
        sync_to_crm
    )

r = redis.Redis(decode_responses=True)

map_tasks = {
    "send_welcome_email": send_welcome_email,
    "resize_product_image": resize_product_image,
    "process_payment": process_payment,
    "backup_database": backup_database,
    "send_slack_notification": send_slack_notification,
    "sync_to_crm": sync_to_crm,
}

print("[WORKER] Listening for tasks...")

while True:
    task_data = r.brpop("task_queue")[1]
    task = json.loads(task_data)

    task_id = task['id'][:8]
    func_name = task['func']

    print(f"[WORKER] Picked up task {task_id} ({func_name})")

    func = map_tasks[func_name]
    args = task["args"]

    start_time = time.time()
    print()

    try:
        res = func(*args)
        duration = time.time() - start_time
        r.hset(f"task:{task['id']}", mapping={"name": func_name, "status": "SUCCESS", "duration": duration, "remark": str(res), "timestamp": str(datetime.datetime.now())})
        print(f"[WORKER] Task {task_id} completed in {duration:.2f}s — result: {str(res)[:50]}")

    except Exception as e:
        duration = time.time() - start_time
        r.hset(f"task:{task['id']}", mapping={"name": func_name, "status": "FAILED", "duration": duration, "remark": str(e), "timestamp": str(datetime.datetime.now())})
        print(f"[WORKER] Task {task_id} FAILED ({str(e)[:30]})")
