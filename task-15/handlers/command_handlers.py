from domain.aggregates import Order


class PlaceOrderCommandHandler:
    def __init__(self, event_store, bus):
        self.event_store = event_store
        self.bus = bus

    def handle(self, command):
        order = Order()
        events = order.place(command)
        print(f"[WRITE] Aggregate Order#{order.order_id} created")
        self.event_store.append(order.order_id, events)
        print(f"[BUS] Published {len(events)} events to \"orders\" topic")
        self.bus.publish(events)
