import sqlite3
import os
# pyrefly: ignore [missing-import]
from werkzeug.security import generate_password_hash

# Resolve DB path to project root (one level above this file)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'spendly.db')


def get_db():
    """Open and return a configured SQLite connection.

    - row_factory = sqlite3.Row  → dictionary-like row access
    - PRAGMA foreign_keys = ON   → enforce FK constraints on this connection
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create both tables using CREATE TABLE IF NOT EXISTS.

    Safe to call multiple times — will not fail or duplicate on repeated runs.
    """
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            name          TEXT    NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password_hash TEXT    NOT NULL,
            created_at    TEXT    DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL REFERENCES users(id),
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            description TEXT,
            created_at  TEXT    DEFAULT (datetime('now'))
        );
    """)
    conn.commit()
    conn.close()


def seed_db():
    """Insert demo user and 8 sample expenses — once only.

    Guards against duplicate inserts by checking the users table first.
    """
    conn = get_db()

    # Guard: exit early if data already exists
    existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing > 0:
        conn.close()
        return

    # Insert demo user with hashed password
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123"))
    )
    conn.commit()

    # Fetch the new user's id
    user_id = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()["id"]

    # 8 sample expenses — covers all 7 categories, dates in current month
    expenses = [
        (user_id, 320.00,  "Food",          "2026-07-01", "Grocery run"),
        (user_id, 150.00,  "Transport",     "2026-07-03", "Uber rides"),
        (user_id, 1200.00, "Bills",         "2026-07-05", "Electricity bill"),
        (user_id, 500.00,  "Health",        "2026-07-08", "Pharmacy"),
        (user_id, 250.00,  "Entertainment", "2026-07-10", "Movie night"),
        (user_id, 890.00,  "Shopping",      "2026-07-14", "Clothes"),
        (user_id, 75.00,   "Other",         "2026-07-18", "Miscellaneous"),
        (user_id, 180.00,  "Food",          "2026-07-22", "Restaurant dinner"),
    ]

    conn.executemany(
        """INSERT INTO expenses (user_id, amount, category, date, description)
           VALUES (?, ?, ?, ?, ?)""",
        expenses
    )
    conn.commit()
    conn.close()
