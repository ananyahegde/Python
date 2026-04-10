import redis
import json
import time
import datetime
from multiprocessing import Process
from tasks import (
        send_welcome_email, 
        resize_product_image, 
        process_payment, 
        backup_database, 
        send_slack_notification, 
        sync_to_crm
    )

r = redis.Redis(decode_responses=True)

MAX_RETRIES = 2
map_tasks = {
    "send_welcome_email": send_welcome_email,
    "resize_product_image": resize_product_image,
    "process_payment": process_payment,
    "backup_database": backup_database,
    "send_slack_notification": send_slack_notification,
    "sync_to_crm": sync_to_crm,
}

def worker(num):
    print(f"[WORKER {num}] Listening for tasks...")

    while True:
        task_data = r.brpop("task_queue")[1]
        task = json.loads(task_data)

        task_id = task['id'][:8]
        func_name = task['func']

        print(f"[WORKER {num}] Picked up task {task_id} ({func_name})")

        func = map_tasks[func_name]
        args = task["args"]

        start_time = time.time()

        try:
            res = func(*args)
            duration = time.time() - start_time
            r.hset(f"task:{task['id']}", mapping={"name": func_name, "status": "success", "duration": duration, "retries": task['retries'], "remark": str(res), "timestamp": str(datetime.datetime.now())})
            print(f"[worker {num}] task {task_id} completed in {duration:.2f}s")

        except Exception as e:
            if task['retries'] < MAX_RETRIES:
                time.sleep(2**task['retries'])
                t = {"id": task['id'], "func": task['func'], "args": task["args"], "retries": task['retries']+1}
                r.lpush("task_queue", json.dumps(t))
            else:
                duration = time.time() - start_time
                r.lpush("dead_queue", json.dumps(task))
                r.hset(f"task:{task['id']}", mapping={"name": func_name, "status": "failed", "duration": duration, "retries": task['retries'], "remark": str(e), "timestamp": str(datetime.datetime.now())})
                print(f"[worker {num}] task {task_id} failed ({str(e)[:30]})")

            print()

if __name__ == "__main__":
    for i in range(4):
        p = Process(target=worker, args=(i+1,))
        p.start()
