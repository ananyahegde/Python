import sqlite3

connection = sqlite3.connect("db.sqlite3")
connection.row_factory = sqlite3.Row

def get_connection():
    return connection
