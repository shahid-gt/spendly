# Spec: Login and Logout

## Overview

This step implements session-based **login** and **logout** for Spendly.

After registering, a user must be able to sign in with their email and password.
On success, their user_id is stored in the Flask session so subsequent requests
can identify who is logged in. Logout clears the session and redirects to the
landing page.

This is a prerequisite for every authenticated feature (profile, expense
management, dashboard). Without a session, the app cannot know which user is
making a request.

---

## Depends on

- Step 1 — Database Setup: users table and get_db() must exist.
- Step 2 — User Registration: at least one real user must exist in the DB.

---

## Routes

```
POST /login    — Verify credentials and start session        — Guest-only
GET  /login    — Display login form                          — Guest-only   (already exists, stub only)
GET  /logout   — Clear session and redirect to /             — Authenticated
GET  /register — Display registration form                   — Guest-only   (already exists; guard added here)
```

The `GET /login` route already exists but only renders the template.
The `GET /logout` route already exists but returns a placeholder string.
Both handlers must be replaced/upgraded in this step.

**Guest-only** means: if the user is already logged in (`session.get('user_id')` is set),
visiting `GET /login` or `GET /register` must **redirect to `url_for('profile')`** immediately,
without rendering the form.

---

## Database Changes

No schema changes required.

The users table (from Step 1) already has:

| Column        | Type | Notes                                         |
|---------------|------|-----------------------------------------------|
| id            | INTEGER | Used as the session key after login        |
| email         | TEXT    | Used to look up the user                   |
| password_hash | TEXT    | Verified with check_password_hash        |

No new tables, columns, indexes, or constraints needed.

---

## Templates

### Create

None — the login template already exists.

### Modify

#### 	emplates/login.html

The form already has email and password fields with method=POST and
ction=/login, and includes {% if error %} error rendering.

No structural changes needed — only the route handler is missing.

#### 	emplates/base.html

The navbar currently always shows **Sign in** and **Get started** links.
It must become session-aware:

- When session.user_id is **not set** (logged-out state):
  - Show: Sign in → /login
  - Show: Get started → /register
- When session.user_id **is set** (logged-in state):
  - Hide Sign in and Get started
  - Show: Sign out → /logout

Use session.get('user_id') inside the Jinja template to make this decision.

---

## Files to Modify

| File                    | Change Required                                                                                                                      |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| `app.py`                | Add `secret_key`; import `session`, `check_password_hash`; implement `POST /login` handler; implement `GET /logout` handler; add guest-only guards to `GET /login` and `GET /register` |
| `templates/base.html`   | Make navbar session-aware (conditional Sign in / Sign out links)                                                                     |

---

## Files to Create

None.

---

## New Dependencies

No new pip packages.

Uses packages already installed:

- lask — session (add to existing import)
- werkzeug.security — check_password_hash (add to existing import)
- sqlite3 — via get_db() from database/db.py

---

## Implementation Rules

- Use raw SQLite only (no SQLAlchemy or ORM).
- Always use parameterized SQL queries.
- Hash passwords using werkzeug.security.generate_password_hash.
- Reuse get_db() from database/db.py.
- All templates must extend ase.html.
- Reuse existing layouts and styling whenever possible.
- Use CSS variables; never hardcode hex colors.
- Keep business logic outside templates.
- Follow existing project structure and naming conventions.

### Login/Logout-Specific Rules

- **pp.secret_key must be set** before any session can be used.
  Use a hard-coded dev string for now (e.g. spendly-dev-secret).
  Do NOT use os.urandom or environment variables in this step.
- **Never store plaintext passwords** in the session or anywhere else.
- Store only user_id (integer) in session after a successful login.
- Use check_password_hash(row[password_hash], password) for verification.
- Lookup user by email with a **parameterized** SELECT query.
- If the email does not exist **or** the password is wrong, show the same
  generic error: Invalid email or password. — do not reveal which field
  failed.
- On successful login, redirect to `url_for('profile')` (Step 4 placeholder).
- `GET /logout` must call `session.clear()` then redirect to `url_for('landing')`.
- Always close the database connection after use.
- **Guest-only guard**: at the top of the `GET /login` and `GET /register` handlers,
  check `session.get('user_id')`. If it is set, immediately
  `return redirect(url_for('profile'))` — do not render the form.

---

## Definition of Done

- [ ] GET /login renders the login form without errors.
- [ ] Submitting valid credentials stores user_id in session and redirects to /profile.
- [ ] Submitting a wrong password shows Invalid email or password. and re-renders the form.
- [ ] Submitting a non-existent email shows Invalid email or password. and re-renders the form.
- [ ] Submitting empty email or password shows All fields are required. and re-renders the form.
- [ ] `GET /logout` clears the session and redirects to `/`.
- [ ] After logout, visiting `/logout` again redirects cleanly (session is already empty — no crash).
- [ ] Navbar shows **Sign in / Get started** when logged out.
- [ ] Navbar shows **Sign out** when logged in.
- [ ] While logged in, visiting `GET /login` redirects to `/profile` (form is not shown).
- [ ] While logged in, visiting `GET /register` redirects to `/profile` (form is not shown).
- [ ] No console or server errors on any path.
- [ ] Mobile layout is responsive and matches existing design.
- [ ] All SQL queries use parameterized syntax.
