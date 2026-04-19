import time
from domains.contracts import GetOrderSummary


class ReadStore:
    def __init__(self):
        self._store = {}

    def upsert(self, order_id, data):
        self._store[order_id] = data

    def execute(self, query):
        if isinstance(query, GetOrderSummary):
            start = time.time()
            result = self._store.get(query.order_id)
            elapsed = (time.time() - start) * 1000
            print(f"\nResponse time: {elapsed:.1f}ms (denormalized read model)")
            return result
