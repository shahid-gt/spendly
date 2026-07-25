---
description: create a single dummy user in the database
---

# Seed User

Read `database/db.py` to understand the `users` table schema and the `get_db()` helper for obtaining the SQLite connection.

## Task

Create a Python script that inserts **one** user into the `users` table, then execute the script using a Bash command.

## Requirements

1. Read the `users` table schema from `database/db.py`.
2. Obtain the database connection using the existing `get_db()` function.
3. Generate a realistic Indian user with:
   - **Name:** Realistic Indian full name (`First Name Last Name`).
   - **Email:** Derived from the name with a random 2–3 digit numeric suffix (e.g., `rahulsharma123@gmail.com`).
   - **Password:** `"password123"` hashed using `werkzeug.security.generate_password_hash`.
   - **created_at:** Current date and time.
4. Before inserting, check whether the generated email already exists.
   - If it exists, regenerate the numeric suffix until the email is unique.
5. Insert the user using the same `get_db()` database pattern used in `database/db.py`.
6. Execute the script via a Bash command.

## Output

After a successful insert, print:

- ID
- Name
- Email