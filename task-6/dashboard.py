import redis
import json
from tabulate import tabulate

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def dashboard():
    rows = []
    for service in ["users", "orders", "products"]:
        raw = r.get(f"stats:{service}")
        if raw:
            stats = json.loads(raw)
            avg_latency = (stats['total_latency'] / stats['request_count'] * 1000) if stats['request_count'] > 0 else 0
            rows.append([
                service,
                stats['status'],
                f"{avg_latency:.0f}ms",
                "OPEN" if stats['open'] else "CLOSED",
                stats['cache_hits'],
                stats['failures'],
            ])
        else:
            rows.append([service, "NO DATA", "-", "-", "-", "-"])
    print(tabulate(rows, headers=["Service", "Status", "Latency", "Circuit", "Cache Hits", "Failures"], tablefmt="grid"))

if __name__ == "__main__":
    dashboard()
