import sqlite3
from datetime import date

def get_connection():
    try:
        conn = sqlite3.connect("books_db.db")
        return conn
    except sqlite3.Error as e:
        print(f"[ERROR] Could not connect to database: {e}")
        return None

def create_tables():
    conn = get_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                sku TEXT UNIQUE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                price REAL,
                scraped_at DATE,
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
        """)
        conn.commit()
        print("Tables created.")
    except sqlite3.Error as e:
        print(f"[ERROR] Could not create tables: {e}")
    finally:
        conn.close()

def is_books_empty():
    conn = get_connection()
    if not conn:
        return True
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM books")
        count = cursor.fetchone()[0]
        return count == 0
    except sqlite3.Error as e:
        print(f"[ERROR] Could not check books table: {e}")
        return True
    finally:
        conn.close()

def has_todays_prices():
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM price_history WHERE scraped_at = ?", (date.today(),))
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.Error as e:
        print(f"[ERROR] Could not check today's prices: {e}")
        return False
    finally:
        conn.close()

def insert_books(data):
    conn = get_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        for _, row in data.iterrows():
            cursor.execute("""
                INSERT OR IGNORE INTO books (name, sku)
                VALUES (?, ?)
            """, (row["name"], row["sku"]))
        conn.commit()
        print(f"Inserted {len(data)} books.")
    except sqlite3.Error as e:
        print(f"[ERROR] Could not insert books: {e}")
        conn.rollback()
    finally:
        conn.close()

def insert_prices(data):
    conn = get_connection()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        today = date.today()
        inserted = 0
        for _, row in data.iterrows():
            cursor.execute("SELECT id FROM books WHERE sku = ?", (row["sku"],))
            result = cursor.fetchone()
            if result:
                cursor.execute("""
                    INSERT INTO price_history (book_id, price, scraped_at)
                    VALUES (?, ?, ?)
                """, (result[0], row["price"], today))
                inserted += 1
        conn.commit()
        print(f"Inserted {inserted} price records for {today}.")
    except sqlite3.Error as e:
        print(f"[ERROR] Could not insert prices: {e}")
        conn.rollback()
    finally:
        conn.close()
