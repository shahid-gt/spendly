---
description: seed realistic dummy expenses for a specific user
---

# Seed Expense

Generate dummy expense records for an existing user.

## Input

User Input: `$ARGUMENTS`

Expected format:

```text
/seed-expense <user_id> <count> <months>
```

Example:

```text
/seed-expense 2 8 6
```

Where:
- `user_id` (integer): User ID for whom expenses will be created.
- `count` (integer): Number of expense records to insert.
- `months` (integer): Number of past months across which expenses should be randomly distributed.

---

## Step 1: Validate Arguments

Parse `$ARGUMENTS` and extract:

- `user_id`
- `count`
- `months`

If any argument is missing, invalid, or not a positive integer, stop and print:

```text
Usage: /seed-expense <user_id> <count> <months>
Example: /seed-expense 2 8 6
```

---

## Step 2: Verify User

Before generating any expenses:

1. Read `database/db.py` to understand the database schema and obtain the SQLite connection using the existing `get_db()` function.
2. Verify that `user_id` exists in the `users` table.

If the user does not exist, stop and print:

```text
No User Found with ID <user_id>.
```

---

## Step 3: Generate and Insert Expenses

Create a Python script and execute it using a Bash command.

Requirements:

1. Insert exactly `count` expense records.
2. Randomly distribute expense dates across the previous `months` months.
3. Generate realistic Indian expense descriptions and amounts using the following categories:

| Category | Amount Range (₹) |
|----------|-----------------:|
| Food | 50–800 |
| Transport | 20–500 |
| Bills | 200–3000 |
| Health | 100–2000 |
| Entertainment | 100–1500 |
| Shopping | 200–5000 |
| Other | 50–1000 |

4. Category distribution should be weighted approximately as follows:
   - Food: Most frequent
   - Transport, Bills, Shopping: Medium frequency
   - Health, Entertainment: Least frequent
   - Other: Occasional
5. Use realistic Indian merchant/expense descriptions.
6. Use the existing `get_db()` connection pattern from `database/db.py`; never hardcode the database path.
7. Use parameterized SQL queries only.
8. Perform all inserts within a single transaction.
   - If any insert fails, roll back the entire transaction.

---

## Step 4: Confirmation

After a successful insert, print:

- Number of expenses inserted
- Date range covered (earliest → latest)
- Sample of any 5 inserted records including:
  - ID
  - Date
  - Category
  - Description
  - Amount