from scraper import scrape_all
from book_parser import parse
from database import has_todays_prices, create_tables, is_books_empty, insert_books, insert_prices

if __name__ == "__main__":
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

    print("Done.")
