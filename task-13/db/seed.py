import sqlite3
import random
from datetime import date, timedelta
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from config import DB_PATH, REGIONS

SEED_START = date(2025, 1, 1)
SEED_END = date(2026, 3, 31)

PRODUCTS = [
    ("SKU-001", "Widget Alpha", 32000.00),
    ("SKU-002", "Widget Beta", 9800.00),
    ("SKU-003", "Gadget Pro", 12999.00),
    ("SKU-004", "Gadget Lite", 9999.00),
    ("SKU-005", "Super Widget", 8999.00),
]

def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sales (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_date   TEXT NOT NULL,        -- YYYY-MM-DD
            region      TEXT NOT NULL,
            product_sku TEXT NOT NULL,
            product_name TEXT NOT NULL,
            units       INTEGER NOT NULL,
            unit_price  REAL NOT NULL,
            revenue     REAL NOT NULL         -- units * unit_price (pre-computed)
        );

        CREATE INDEX IF NOT EXISTS idx_sale_date ON sales(sale_date);
        CREATE INDEX IF NOT EXISTS idx_region    ON sales(region);
    """)
    conn.commit()

def seed_data(conn: sqlite3.Connection) -> None:
    # Check if already seeded
    cursor = conn.execute("SELECT COUNT(*) FROM sales")
    if cursor.fetchone()[0] > 0:
        print("DB already seeded. Skipping.")
        return

    rows = []
    current = SEED_START

    while current <= SEED_END:
        # 3-8 transactions per day per region
        for region in REGIONS:
            num_transactions = random.randint(3, 8)
            for _ in range(num_transactions):
                sku, name, base_price = random.choice(PRODUCTS)
                units = random.randint(1, 20)

                # Add some noise to price
                price_noise = random.uniform(0.9, 1.1)

                region_factor = 0.75 if region == "West" else 1.0
                unit_price = round(base_price * price_noise * region_factor, 2)
                revenue = round(units * unit_price, 2)

                rows.append((
                    current.isoformat(),
                    region,
                    sku,
                    name,
                    units,
                    unit_price,
                    revenue,
                ))

        current += timedelta(days=1)

    conn.executemany("""
        INSERT INTO sales (sale_date, region, product_sku, product_name, units, unit_price, revenue)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    print(f"Seeded {len(rows)} records from {SEED_START} to {SEED_END}.")

def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    try:
        create_schema(conn)
        seed_data(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
