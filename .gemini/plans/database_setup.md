# Implementation Plan — Database Setup (Step 1)

## Goal

Replace the stub `database/db.py` with a full SQLite implementation that creates
the schema, seeds demo data, and wires into `app.py` on startup.

---

## Files Changed

| File                | Change Type |
|---------------------|-------------|
| `database/db.py`    | Implement   |
| `app.py`            | Modify      |

---

## Step 1 — Implement `database/db.py`

Replace the entire file (currently only comments) with three functions.

---

### 1.1 `get_db()`

**Purpose:** Open and return a configured SQLite connection.

```python
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'spendly.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
```

**Key decisions:**
- `DB_PATH` resolves to the project root (one level above `database/`) so the
  `.db` file sits alongside `app.py`, not inside the package folder.
- `sqlite3.Row` enables dictionary-like access: `row["email"]` instead of `row[2]`.
- `PRAGMA foreign_keys = ON` must be set on **every** new connection (SQLite
  does not persist this setting).

---

### 1.2 `init_db()`

**Purpose:** Create both tables idempotently.

```python
def init_db():
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
```

**Key decisions:**
- `CREATE TABLE IF NOT EXISTS` makes this safe to call on every startup.
- `REFERENCES users(id)` is the FK declaration; enforcement is activated by
  the `PRAGMA` in `get_db()`.
- `executescript()` runs both DDL statements in one call and commits automatically.

---

### 1.3 `seed_db()`

**Purpose:** Insert demo user + 8 sample expenses — once only.

```python
from werkzeug.security import generate_password_hash

def seed_db():
    conn = get_db()

    # Guard: exit early if data already exists
    existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing > 0:
        conn.close()
        return

    # Insert demo user
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", generate_password_hash("demo123"))
    )
    conn.commit()

    user_id = conn.execute(
        "SELECT id FROM users WHERE email = ?", ("demo@spendly.com",)
    ).fetchone()["id"]

    # 8 sample expenses — one per category (7 categories) + one extra
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
```

**Key decisions:**
- The guard `SELECT COUNT(*) FROM users` is checked before any insert; if any
  user rows exist the function returns immediately — safe for repeated restarts.
- `executemany()` is used for the 8 expense rows (clean, DRY).
- All SQL uses `?` placeholders — no f-strings or `.format()` in SQL.
- Dates are hardcoded in `YYYY-MM-DD` format as required by the spec.
- Categories match the fixed list exactly: Food, Transport, Bills, Health,
  Entertainment, Shopping, Other.

---

## Step 2 — Modify `app.py`

### 2.1 Add imports

At the top of `app.py`, after the existing `from flask import ...` line:

```python
from database.db import get_db, init_db, seed_db
```

### 2.2 Call init + seed on startup

Before `if __name__ == "__main__":`, add:

```python
# ------------------------------------------------------------------ #
# Database initialisation                                             #
# ------------------------------------------------------------------ #
with app.app_context():
    init_db()
    seed_db()
```

**Why `app.app_context()`?**  
Flask requires an active application context for certain operations. Wrapping
the DB calls in `app.app_context()` is the idiomatic pattern and ensures the
DB is ready before any request is handled — even in production WSGI servers
that do not use `__main__`.

---

## Step 3 — Verify

After implementation, run these manual checks:

### 3.1 Start the app

```
python app.py
```

Expected output — no errors, app starts on port 5001.

### 3.2 Confirm DB file exists

Check that `spendly.db` appears in the project root after first run.

### 3.3 Inspect via SQLite CLI

```bash
sqlite3 spendly.db
.tables              -- should show: users  expenses
SELECT * FROM users;
SELECT COUNT(*) FROM expenses;  -- should return 8
```

### 3.4 Test idempotency

Restart the app a second time. Row counts must remain 1 user / 8 expenses.

### 3.5 Test FK enforcement

```sql
INSERT INTO expenses (user_id, amount, category, date)
VALUES (999, 10.0, 'Food', '2026-07-01');
-- Expected: FOREIGN KEY constraint failed
```

### 3.6 Test UNIQUE constraint

```sql
INSERT INTO users (name, email, password_hash)
VALUES ('Another', 'demo@spendly.com', 'x');
-- Expected: UNIQUE constraint failed: users.email
```

---

## Definition of Done Checklist

- [ ] `spendly.db` created on first `python app.py`
- [ ] `users` table has all 5 columns with correct types & constraints
- [ ] `expenses` table has all 7 columns with correct types & constraints
- [ ] Demo user `demo@spendly.com` exists with hashed (not plain) password
- [ ] Exactly 8 expense rows across all 7 categories
- [ ] Second app start does **not** add duplicate rows
- [ ] FK insert of invalid `user_id` is rejected
- [ ] Duplicate email insert is rejected
- [ ] App starts without Python errors
- [ ] Zero raw SQL strings — all queries use `?` parameterized form
