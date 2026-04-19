"""
Set of Events.
Write model publish events when it updates the database, which the Read model uses to refresh its data.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class OrderPlaced:
    order_id: str
    customer_id: str
    total: float
    items: List[Dict]
    timestamp: str


@dataclass
class InventoryReserved:
    order_id: str
    sku: str
    qty: int
    timestamp: str


@dataclass
class OrderUpdated:
    order_id: str
    removed_sku: str
    new_total: float
    timestamp: str


@dataclass
class PaymentProcessed:
    order_id: str
    amount: float
    method: str
    timestamp: str


@dataclass
class OrderShipped:
    order_id: str
    tracking: str
    timestamp: str
