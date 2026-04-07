import sqlite3
import csv
from datetime import date, timedelta
from database import get_connection
from rich.console import Console
from rich.table import Table

console = Console()

def get_price_changes():
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        today = date.today()
        yesterday = today - timedelta(days=1)

        cursor.execute("""
            SELECT b.name, y.price, t.price
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

def export_csv(changes):
    filename = f"price_changes_{date.today()}.csv"
    try:
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "yesterday_price", "today_price", "change"])
            for name, yesterday_price, today_price in changes:
                change = round(today_price - yesterday_price, 2)
                writer.writerow([name, yesterday_price, today_price, change])
        print(f"Report saved to {filename}")
    except IOError as e:
        print(f"[ERROR] Could not write CSV: {e}")

def print_report(changes):
    table = Table(title="=== Price Change Report ===")
    table.add_column("Product", style="cyan")
    table.add_column("Old Price", style="white")
    table.add_column("New Price", style="white")
    table.add_column("Change", style="green")

    for name, yesterday_price, today_price in changes:
        change = round(today_price - yesterday_price, 2)
        change_str = f"+{change}" if change > 0 else str(change)
        table.add_row(name, f"£{yesterday_price}", f"£{today_price}", change_str)

    console.print(table)
    console.print(f"{len(changes)} price changes detected.")

def export_report():
    changes = get_price_changes()

    if not changes:
        print("No price changes found for today.")
        return

    print_report(changes)
    export_csv(changes)
