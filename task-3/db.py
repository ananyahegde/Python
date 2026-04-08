import sqlite3

connection = sqlite3.connect("x.db")
connection.row_factory = sqlite3.Row

def get_connection():
    return connection

def execute_query(sql, values=None, silent=False):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, values or [])
    conn.commit()

    if values:
        display = sql
        for v in values:
            display = display.replace('?', repr(v), 1)
        if not silent:
            print(f"SQL: {display}")
    else:
        if not silent:
            print(f"SQL: {sql}")

    return cursor
