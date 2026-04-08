import sqlite3

connection = sqlite3.connect("x.db")
connection.row_factory = sqlite3.Row

def get_connection():
    return connection

def execute(sql, values=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, values or [])
    conn.commit()
    return cursor
