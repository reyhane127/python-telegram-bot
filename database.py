import sqlite3
from datetime import datetime


def create_database():
    connection = sqlite3.connect("customers.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            first_name TEXT,
            username TEXT,
            message TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        message TEXT,
        created_at TEXT
    )
""")

    connection.commit()
    connection.close()


def save_customer(telegram_id, first_name, username, message):
    connection = sqlite3.connect("customers.db")
    cursor = connection.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO customers
        (telegram_id, first_name, username, message, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        telegram_id,
        first_name,
        username,
        message,
        "New",
        now,
        now
    ))

    connection.commit()
    connection.close()


def find_customer(telegram_id):
    connection = sqlite3.connect("customers.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM customers WHERE telegram_id = ?",
        (telegram_id,)
    )

    customer = cursor.fetchone()

    connection.close()

    return customer


def update_customer(telegram_id, first_name, username, message):
    connection = sqlite3.connect("customers.db")
    cursor = connection.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE customers
        SET
            first_name = ?,
            username = ?,
            message = ?,
            updated_at = ?
        WHERE telegram_id = ?
    """, (
        first_name,
        username,
        message,
        now,
        telegram_id
    ))

    connection.commit()
    connection.close()


def change_status(telegram_id, status):
    connection = sqlite3.connect("customers.db")
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE customers
        SET status = ?
        WHERE telegram_id = ?
    """, (
        status,
        telegram_id
    ))

    connection.commit()
    connection.close()


def show_customers():
    connection = sqlite3.connect("customers.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM customers")

    customers = cursor.fetchall()

    for customer in customers:
        print(customer)

    connection.close()

def get_all_customers():
    connection = sqlite3.connect("customers.db")
    cursor = connection.cursor()

    cursor.execute("""
       SELECT telegram_id, first_name, username, message, status, updated_at
       FROM customers
       ORDER BY updated_at DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return rows

def save_message(telegram_id, message):
    connection = sqlite3.connect("customers.db")
    cursor = connection.cursor()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO messages
        (telegram_id, message, created_at)
        VALUES (?, ?, ?)
    """, (
        telegram_id,
        message,
        now
    ))

    connection.commit()
    connection.close()
    

def get_messages(telegram_id):
    connection = sqlite3.connect("customers.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT message, created_at
        FROM messages
        WHERE telegram_id = ?
        ORDER BY created_at
    """, (telegram_id,))

    messages = cursor.fetchall()

    connection.close()

    return messages