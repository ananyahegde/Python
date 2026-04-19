import uuid
from datetime import datetime, timezone
from domain.events import OrderPlaced, InventoryReserved


def generate_order_id():
    num = uuid.uuid4().int % 9000 + 1000
    return f"ORD-{num}"


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Order:
    def __init__(self):
        self.order_id = generate_order_id()
        self.status = None
        self.total = 0.0
        self.items = []

    def place(self, command):
        items = [{"sku": i["sku"], "qty": i["qty"], "price": i["price"]} for i in command.items]
        total = sum(i["qty"] * i["price"] for i in items)
        item_count = sum(i["qty"] for i in items)
        timestamp = now()

        self.status = "PLACED"
        self.total = total
        self.items = items

        events = []

        events.append(OrderPlaced(
            order_id=self.order_id,
            customer_id=command.customer_id,
            total=round(total, 2),
            items=items,
            timestamp=timestamp
        ))

        for item in items:
            events.append(InventoryReserved(
                order_id=self.order_id,
                sku=item["sku"],
                qty=item["qty"],
                timestamp=timestamp
            ))

        return events
