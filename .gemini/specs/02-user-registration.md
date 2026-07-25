# Spec: User Registration

## Overview

This step implements the **user registration flow** for Spendly.

A visitor can create a new account by providing their full name, email address, and a password. On success the user is redirected to the login page. On failure (duplicate email, validation error) the registration form is re-displayed with a descriptive error message.

This is the first authentication-related feature and is a prerequisite for login, profile management, and all expense-related features.

---

## Depends on

- Step 1 — Database Setup (`database_setup.md`)
  - `users` table must exist
  - `get_db()` must be available from `database/db.py`

---

## Routes

```
POST /register — Handle registration form submission — Public
GET  /register — Display registration form            — Public (already exists)
```

The `GET /register` route already exists in `app.py` and renders `register.html`.
Only the `POST /register` route handler needs to be added.

---

## Database Changes

No schema changes required. The `users` table already contains all needed columns:

| Column        | Type    | Notes                                              |
|---------------|---------|----------------------------------------------------|
| id            | INTEGER | Primary key, autoincrement                         |
| name          | TEXT    | Stores the user's full name                        |
| email         | TEXT    | UNIQUE — enforced at DB level; catches duplicates  |
| password_hash | TEXT    | Stored using `generate_password_hash`              |
| created_at    | TEXT    | Set automatically by SQLite `datetime('now')`      |

No new tables, columns, indexes, or constraints needed.

---

## Templates

### Create

None — the registration template already exists.

### Modify

#### `templates/register.html`

The form already has `name`, `email`, and `password` fields with `method="POST" action="/register"`.

Required changes:

1. Ensure the form method is `POST` and action is `/register` (already correct)
2. Confirm the `{% if error %}` block renders the `{{ error }}` variable (already present)
3. No structural changes required — only the route handler is missing

---

## Files to Modify

| File       | Change Required                                                     |
|------------|---------------------------------------------------------------------|
| `app.py`   | Add `POST /register` handler; import `generate_password_hash`; import `redirect`, `request`, `url_for` from Flask |

---

## Files to Create

None.

---

## New Dependencies

No new dependencies.

Uses packages already installed:

- `flask` — `request`, `redirect`, `url_for`, `render_template`
- `werkzeug.security` — `generate_password_hash`
- `sqlite3` — via `get_db()` from `database/db.py`

---

## Implementation Rules

- Use raw SQLite only (no SQLAlchemy or ORM).
- Always use parameterized SQL queries.
- Hash passwords using `werkzeug.security.generate_password_hash`.
- Reuse `get_db()` from `database/db.py`.
- All templates must extend `base.html`.
- Reuse existing layouts and styling whenever possible.
- Use CSS variables; never hardcode hex colors.
- Keep business logic outside templates.
- Follow existing project structure and naming conventions.

### Registration-Specific Rules

- **Server-side validation** is required — do not rely on HTML `required` alone.
- Validate that `name`, `email`, and `password` are all non-empty after stripping whitespace.
- Validate that `password` is at least **8 characters** long.
- Catch `sqlite3.IntegrityError` to detect duplicate email, and re-render the form with the error message: `"An account with that email already exists."`
- On success, redirect to `url_for('login')` — do **not** auto-login the user in this step.
- Always close the database connection after use.

---

## Definition of Done

- [ ] `GET /register` renders the registration form without errors.
- [ ] Submitting the form with valid data creates a new row in the `users` table.
- [ ] The stored `password_hash` is a Werkzeug hash, not plaintext.
- [ ] Duplicate email submission re-renders the form with the error: `"An account with that email already exists."`
- [ ] Empty name, email, or password re-renders the form with an appropriate validation error.
- [ ] Password shorter than 8 characters is rejected with an appropriate error.
- [ ] Successful registration redirects to `/login`.
- [ ] No console or server errors on any path.
- [ ] Mobile layout is responsive and matches existing design.
- [ ] All SQL queries use parameterized syntax (no f-strings or `%` formatting in SQL).
