"""
seed_db.py — Creates and populates querymind.db
Usage: python seed_db.py
Also called automatically by app.py on Streamlit Cloud if DB not found.
"""

import sqlite3
import os
import random
from datetime import date, timedelta

# Always resolve DB path relative to this file — works locally and on Streamlit Cloud
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "querymind.db")


def seed(silent: bool = False):
    """
    Creates and seeds the database.
    silent=True suppresses all print output (used when called from app.py).
    """
    def log(msg):
        if not silent:
            print(msg)

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        log(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE customers (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            city       TEXT,
            created_at TEXT DEFAULT CURRENT_DATE
        );

        CREATE TABLE products (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT NOT NULL,
            category TEXT,
            price    REAL NOT NULL,
            stock    INTEGER DEFAULT 0
        );

        CREATE TABLE orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER REFERENCES customers(id),
            product_id  INTEGER REFERENCES products(id),
            quantity    INTEGER NOT NULL,
            amount      REAL NOT NULL,
            order_date  TEXT DEFAULT CURRENT_DATE,
            status      TEXT DEFAULT 'pending'
        );
    """)

    customers = [
        ("Aarav Shah",   "aarav@example.com",   "Mumbai"),
        ("Priya Nair",   "priya@example.com",   "Pune"),
        ("Rohan Mehta",  "rohan@example.com",   "Delhi"),
        ("Sneha Patil",  "sneha@example.com",   "Bangalore"),
        ("Vikram Singh", "vikram@example.com",  "Chennai"),
        ("Ananya Iyer",  "ananya@example.com",  "Hyderabad"),
        ("Karan Gupta",  "karan@example.com",   "Kolkata"),
        ("Meera Joshi",  "meera@example.com",   "Ahmedabad"),
        ("Arjun Rao",    "arjun@example.com",   "Jaipur"),
        ("Divya Sharma", "divya@example.com",   "Lucknow"),
    ]
    cursor.executemany(
        "INSERT INTO customers (name, email, city) VALUES (?, ?, ?)",
        customers
    )

    products = [
        ("Laptop Stand",        "Accessories",   799.0,  45),
        ("Mechanical Keyboard", "Accessories",  2499.0,  30),
        ("USB-C Hub",           "Accessories",   999.0,  60),
        ("Monitor 24 inch",     "Electronics", 12999.0,  10),
        ("Wireless Mouse",      "Accessories",   599.0,  80),
        ("Webcam HD",           "Electronics",  2199.0,  20),
        ("Desk Lamp",           "Furniture",     399.0,  55),
        ("Notebook Set",        "Stationery",    149.0, 200),
        ("Headphones",          "Electronics",  1899.0,  35),
        ("Phone Stand",         "Accessories",   299.0,   0),
    ]
    cursor.executemany(
        "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
        products
    )

    statuses = ["completed", "completed", "completed", "pending", "cancelled"]
    base_date = date.today() - timedelta(days=90)
    orders = []
    random.seed(42)
    for i in range(50):
        customer_id = random.randint(1, 10)
        product_id  = random.randint(1, 10)
        quantity    = random.randint(1, 5)
        cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
        price      = cursor.fetchone()[0]
        amount     = round(price * quantity, 2)
        order_date = (base_date + timedelta(days=random.randint(0, 89))).isoformat()
        status     = random.choice(statuses)
        orders.append((customer_id, product_id, quantity, amount, order_date, status))

    cursor.executemany(
        "INSERT INTO orders (customer_id, product_id, quantity, amount, order_date, status) VALUES (?, ?, ?, ?, ?, ?)",
        orders
    )

    conn.commit()
    conn.close()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM customers")
    log(f"Customers : {c.fetchone()[0]}")
    c.execute("SELECT COUNT(*) FROM products")
    log(f"Products  : {c.fetchone()[0]}")
    c.execute("SELECT COUNT(*) FROM orders")
    log(f"Orders    : {c.fetchone()[0]}")
    conn.close()
    log(f"\nDatabase ready: {DB_PATH}")


if __name__ == "__main__":
    seed(silent=False)