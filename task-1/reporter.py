import sqlite3
import csv
from datetime import date, timedelta
from database import get_connection

def get_price_changes():
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        today = date.today()
        yesterday = today - timedelta(days=1)

        cursor.execute("""
            SELECT b.name, t.price as today_price, y.price as yesterday_price
            FROM price_history t
            JOIN price_history y ON t.book_id = y.book_id
            JOIN books b ON t.book_id = b.id
            WHERE t.scraped_at = ?
            AND y.scraped_at = ?
            AND t.price != y.price
        """, (today, yesterday))

        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"[ERROR] Could not fetch price changes: {e}")
        return []
    finally:
        conn.close()

def export_csv():
    changes = get_price_changes()

    if not changes:
        print("No price changes found for today.")
        return

    filename = f"price_changes_{date.today()}.csv"
    try:
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "yesterday_price", "today_price", "change"])
            for name, today_price, yesterday_price in changes:
                change = round(today_price - yesterday_price, 2)
                writer.writerow([name, yesterday_price, today_price, change])
        print(f"Report exported: {filename}")
    except IOError as e:
        print(f"[ERROR] Could not write CSV: {e}")
