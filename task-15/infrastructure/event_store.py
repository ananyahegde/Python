from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class EventStore:
    def __init__(self):
        self._store = {}
        self._sequence = 0

    def append(self, aggregate_id, events):
        if aggregate_id not in self._store:
            self._store[aggregate_id] = []

        print(f"[EVENT STORE] Appended events:")
        for event in events:
            self._sequence += 1
            record = {
                "seq": self._sequence,
                "aggregate_id": aggregate_id,
                "type": type(event).__name__,
                "payload": event.__dict__,
                "timestamp": now()
            }
            self._store[aggregate_id].append(record)
            self._print_event(record)

    def _print_event(self, record):
        t = record["type"]
        p = record["payload"]
        seq = record["seq"]

        if t == "OrderPlaced":
            print(f"  {seq}. OrderPlaced {{order_id: \"{p['order_id']}\", customer: \"{p['customer_id']}\", total: ${p['total']}}}")
        elif t == "InventoryReserved":
            print(f"  {seq}. InventoryReserved {{sku: \"{p['sku']}\", qty: {p['qty']}}}")

    def get_events(self, aggregate_id):
        return self._store.get(aggregate_id, [])

    def replay(self, aggregate_id):
        events = self.get_events(aggregate_id)
        if not events:
            print(f"No events found for {aggregate_id}")
            return None

        state = {
            "id": aggregate_id,
            "status": None,
            "total": 0.0,
            "items": [],
        }

        print(f"\n[Event Replay]")
        for record in events:
            t = record["type"]
            p = record["payload"]
            ts = record["timestamp"]
            seq = record["seq"]

            if t == "OrderPlaced":
                print(f"[Event #{seq}] OrderPlaced @ {ts[11:19]} {{total: {p['total']}, status: PLACED}}")
                state["status"] = "PLACED"
                state["total"] = p["total"]
                state["items"] = p["items"]

            elif t == "InventoryReserved":
                pass

            elif t == "OrderUpdated":
                print(f"[Event #{seq}] OrderUpdated @ {ts[11:19]} {{removed: \"{p['removed_sku']}\", new_total: {p['new_total']}}}")
                state["total"] = p["new_total"]
                state["items"] = [i for i in state["items"] if i["sku"] != p["removed_sku"]]
                state["status"] = "UPDATED"

            elif t == "PaymentProcessed":
                print(f"[Event #{seq}] PaymentProcessed @ {ts[11:19]} {{amount: {p['amount']}, method: \"{p['method']}\"}}")
                state["status"] = "PAID"

            elif t == "OrderShipped":
                print(f"[Event #{seq}] OrderShipped @ {ts[11:19]} {{tracking: \"{p['tracking']}\"}}")
                state["status"] = "SHIPPED"

        item_count = sum(i["qty"] for i in state["items"])
        print(f"\nReconstructed state: Order(id={state['id']}, status={stte['status']}, total={state['total']}, items={item_count})")
        return state
