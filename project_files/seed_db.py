"""
seed_db.py — Run this ONCE to create and populate querymind.db
Usage: python seed_db.py
"""

import sqlite3
import os
import random
from datetime import date, timedelta

DB_PATH = "querymind.db"


def seed():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- Create Tables ---
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

    # --- Seed Customers ---
    customers = [
        ("Aarav Shah",      "aarav@example.com",   "Mumbai"),
        ("Priya Nair",      "priya@example.com",   "Pune"),
        ("Rohan Mehta",     "rohan@example.com",   "Delhi"),
        ("Sneha Patil",     "sneha@example.com",   "Bangalore"),
        ("Vikram Singh",    "vikram@example.com",  "Chennai"),
        ("Ananya Iyer",     "ananya@example.com",  "Hyderabad"),
        ("Karan Gupta",     "karan@example.com",   "Kolkata"),
        ("Meera Joshi",     "meera@example.com",   "Ahmedabad"),
        ("Arjun Rao",       "arjun@example.com",   "Jaipur"),
        ("Divya Sharma",    "divya@example.com",   "Lucknow"),
    ]
    cursor.executemany(
        "INSERT INTO customers (name, email, city) VALUES (?, ?, ?)",
        customers
    )

    # --- Seed Products ---
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
        ("Phone Stand",         "Accessories",   299.0,   0),  # out of stock
    ]
    cursor.executemany(
        "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
        products
    )

    # --- Seed Orders ---
    statuses = ["completed", "completed", "completed", "pending", "cancelled"]
    base_date = date.today() - timedelta(days=90)

    orders = []
    random.seed(42)
    for i in range(50):
        customer_id = random.randint(1, 10)
        product_id  = random.randint(1, 10)
        quantity    = random.randint(1, 5)
        # fetch price
        cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
        price = cursor.fetchone()[0]
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

    # Verify
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM customers"); print(f"Customers : {c.fetchone()[0]}")
    c.execute("SELECT COUNT(*) FROM products");  print(f"Products  : {c.fetchone()[0]}")
    c.execute("SELECT COUNT(*) FROM orders");    print(f"Orders    : {c.fetchone()[0]}")
    conn.close()
    print(f"\nDatabase ready: {DB_PATH}")


if __name__ == "__main__":
    seed()
