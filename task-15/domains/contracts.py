from dataclasses import dataclass
from typing import List, Dict


@dataclass
class OrderItem:
    """Value object. Represents a single order."""
    sku: str
    qty: int
    price: float


@dataclass
class PlaceOrderCommand:
    """place order command for write operation."""
    customer_id: str
    items: List[Dict]


@dataclass
class GetOrderSummary:
    """Query that reads from data store."""
    order_id: str
