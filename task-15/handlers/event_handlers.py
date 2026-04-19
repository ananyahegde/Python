from domains.events import OrderPlaced


class OrderDashboardProjection:
    def __init__(self, read_store):
        self.read_store = read_store

    async def handle(self, event):
        if isinstance(event, OrderPlaced):
            print(f"\n[HANDLER: OrderDashboardProjection] OrderPlaced -> updating read model...")
            item_count = sum(i["qty"] for i in event.items)
            data = {
                "order_id": event.order_id,
                "customer_id": event.customer_id,
                "status": "PLACED",
                "total": event.total,
                "item_count": item_count,
                "placed_at": event.timestamp
            }
            self.read_store.upsert(event.order_id, data)
            print(f"Read DB: INSERT INTO order_summary (id, customer, total, status, item_count)")
            print(f"         VALUES ('{event.order_id}', '{event.customer_id}', {event.total}, 'PLACED', {item_count})")


class NotificationService:
    async def handle(self, event):
        if isinstance(event, OrderPlaced):
            print(f"\n[HANDLER: NotificationService] OrderPlaced -> sending confirmation email...")
            print(f"Email sent to customer {event.customer_id} OK")


class AnalyticsProjection:
    def __init__(self):
        self.daily_revenue = 12607.36

    async def handle(self, event):
        if isinstance(event, OrderPlaced):
            print(f"\n[HANDLER: AnalyticsProjection] OrderPlaced -> updating daily stats...")
            self.daily_revenue = round(self.daily_revenue + event.total, 2)
            print(f"Today's revenue: ${self.daily_revenue} (+${event.total})")
