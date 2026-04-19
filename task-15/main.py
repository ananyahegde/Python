from domain.commands import PlaceOrderCommand, GetOrderSummary
from domain.events import OrderPlaced, OrderUpdated, PaymentProcessed, OrderShipped
from infrastructure.event_store import EventStore
from infrastructure.read_store import ReadStore
from infrastructure.message_bus import MessageBus
from handlers.command_handlers import PlaceOrderCommandHandler
from handlers.event_handlers import OrderDashboardProjection, NotificationService, AnalyticsProjection
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


event_store = EventStore()
read_store = ReadStore()
bus = MessageBus()

dashboard = OrderDashboardProjection(read_store)
notification = NotificationService()
analytics = AnalyticsProjection()

command_handler = PlaceOrderCommandHandler(event_store, bus)
bus.register_command(PlaceOrderCommand, command_handler)

bus.register_event(OrderPlaced, dashboard)
bus.register_event(OrderPlaced, notification)
bus.register_event(OrderPlaced, analytics)


print("=== Command Side (Write) ===")
cmd = PlaceOrderCommand(
    customer_id="C-42",
    items=[
        {"sku": "WIDGET-01", "qty": 3, "price": 29.99},
        {"sku": "GADGET-05", "qty": 1, "price": 149.99}
    ]
)
bus.dispatch(cmd)

order_id = list(event_store._store.keys())[0]

print("\n=== Query Side (Read) ===")
query = GetOrderSummary(order_id=order_id)
result = read_store.execute(query)
print(result)

print("\n=== Event Replay (Audit) ===")

extra_events = [
    OrderUpdated(order_id=order_id, removed_sku="GADGET-05", new_total=89.97, timestamp="2026-02-24T14:45:22Z"),
    PaymentProcessed(order_id=order_id, amount=89.97, method="card_ending_4242", timestamp="2026-02-24T14:46:01Z"),
    OrderShipped(order_id=order_id, tracking="1Z999AA10123456784", timestamp="2026-02-24T15:10:33Z"),
]

for e in extra_events:
    event_store._store[order_id].append({
        "seq": event_store._sequence + 1,
        "aggregate_id": order_id,
        "type": type(e).__name__,
        "payload": e.__dict__,
        "timestamp": e.timestamp
    })
    event_store._sequence += 1

events = event_store.get_events(order_id)
print(f">>> events = event_store.get_events(aggregate_id=\"{order_id}\")")
event_store.replay(order_id)
