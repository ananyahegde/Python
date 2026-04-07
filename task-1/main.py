from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from scraper import scrape_all
from book_parser import parse
from database import is_books_empty, has_todays_prices, insert_books, insert_prices, create_tables
from reporter import export_report

def job():
    print(f"\n[{datetime.now()}] Starting nightly scrape...")
    create_tables()
    data = parse(scrape_all())

    if is_books_empty():
        print("Populating books table for the first time...")
        insert_books(data)

    if not has_todays_prices():
        print("Inserting today's prices...")
        insert_prices(data)
    else:
        print("Today's prices already exist, skipping...")

    export_report()
    print(f"[{datetime.now()}] Done.")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(job, "cron", hour=10, minute=22)
    print("Scheduler started. Waiting for 2:00 AM...")
    scheduler.start()
