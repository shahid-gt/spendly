# Spec: Profile Page

## Overview

The Profile Page is the authenticated home screen of Spendly. After a user logs
in, they are redirected to `/profile`. This step replaces the current stub
response with a real, fully-rendered page.

The page serves two purposes:

1. **Identity summary** — display the logged-in user's name, email, and account
   age so they can confirm they are in the right session.
2. **Spending snapshot** — show a high-level summary of their expense activity
   (total expenses logged, total amount spent this month, and top spending
   category) so the page is immediately useful, not just decorative.

It is the natural landing point after login and the foundation on which future
features (dashboard, expense list) will be linked.

---

## Depends on

- Step 1 — Database Setup: `users` and `expenses` tables and `get_db()` must exist.
- Step 2 — User Registration: at least one user must exist in the database.
- Step 3 — Login and Logout: session must store `user_id` after login; all authenticated
  routes depend on this.

---

## Routes

```
GET /profile — Render the authenticated user profile page — Authenticated
```

**Auth guard:** If `session.get('user_id')` is not set, redirect immediately to
`url_for('login')`. Do not render the template.

The route already exists as a stub in `app.py` (line 111–113). It must be
replaced with a real handler that:

1. Reads `user_id` from the session.
2. Queries the `users` table for the logged-in user's record.
3. Queries the `expenses` table for summary statistics (current-month total,
   all-time count, top category).
4. Passes the user object and stats dict to `profile.html`.

---

## Database Changes

No schema changes required.

The existing tables are sufficient:

| Table | Columns Used |
|---|---|
| `users` | `id`, `name`, `email`, `created_at` |
| `expenses` | `user_id`, `amount`, `category`, `date` |

**Queries needed (all parameterized):**

```sql
-- Fetch user record
SELECT id, name, email, created_at
FROM users
WHERE id = ?

-- Total amount spent in the current calendar month
SELECT COALESCE(SUM(amount), 0) AS month_total
FROM expenses
WHERE user_id = ?
  AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')

-- All-time expense count
SELECT COUNT(*) AS total_count
FROM expenses
WHERE user_id = ?

-- Top spending category (all time)
SELECT category, SUM(amount) AS cat_total
FROM expenses
WHERE user_id = ?
GROUP BY category
ORDER BY cat_total DESC
LIMIT 1
```

No new tables, columns, indexes, or constraints are needed.

---

## Templates

### Create

#### `templates/profile.html`

A new template that extends `base.html`.

**Sections:**

1. **Page header** — greeting with the user's first name and a short tagline.
2. **Account info card** — full name, email address, member since date
   (formatted as `DD Mon YYYY`).
3. **Spending snapshot row** — three stat cards side by side:
   - *This month* — total amount spent in the current calendar month (₹ format).
   - *Total expenses* — all-time count of expense records.
   - *Top category* — the category with the highest cumulative spend; shows
     "—" if no expenses exist yet.
4. **Quick-action links** — two buttons:
   - Add Expense → `url_for('add_expense')` (placeholder route, already exists)
   - Sign out → `url_for('logout')`
5. **Empty state** — displayed in the snapshot row only when the user has zero
   expenses: a brief prompt encouraging them to log their first expense.

### Modify

#### `templates/base.html`

No structural changes required. The navbar already conditionally shows
**Sign out** when `session.user_id` is set (implemented in Step 3).

---

## Files to Modify

| File | Change Required |
|---|---|
| `app.py` | Replace the `/profile` stub with a real route handler: auth guard, two DB queries, render `profile.html` with `user` and `stats` context variables |

---

## Files to Create

| File | Purpose |
|---|---|
| `templates/profile.html` | Authenticated profile page template |
| `static/css/profile.css` | Scoped styles for the profile page (stat cards, account card, quick-actions) |

---

## New Dependencies

No new dependencies.

Uses packages already installed:

- `flask` — `session`, `render_template`, `redirect`, `url_for` (existing imports)
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

### Profile-Specific Rules

- **Auth guard first:** the very first line of the route body must check
  `session.get('user_id')`. If absent, `return redirect(url_for('login'))`.
- **Always close the DB connection** after each query block (use `try/finally`).
- **Use `sqlite3.Row` access** (already configured in `get_db()`): access
  columns by name, e.g. `user['name']`, not by index.
- **Handle zero-expense state gracefully:** `COALESCE(SUM(amount), 0)` for
  totals; show `"—"` for top category when count is 0.
- **Do not expose `password_hash`** to the template — pass only `name`, `email`,
  `created_at`.
- **Format currency as ₹ in the template**, not in Python — pass raw numeric
  values and use Jinja2 filters or inline formatting.
- **Format `created_at`** from ISO `YYYY-MM-DD HH:MM:SS` to a human-readable
  string in Python before passing to the template (e.g. `"26 Jul 2026"`).
- **Link to placeholder routes** (`add_expense`) using `url_for()` — these
  routes already exist as stubs and must not be created again.
- Profile CSS must use only `var(--*)` tokens from `style.css` — no hard-coded
  hex values.

---

## Definition of Done

- [ ] `GET /profile` renders the profile page without errors when logged in.
- [ ] Visiting `GET /profile` while logged out redirects to `/login`.
- [ ] The page displays the correct user name and email from the database.
- [ ] The "Member since" date is displayed in a human-readable format.
- [ ] "This month" stat shows the correct total for the current calendar month.
- [ ] "Total expenses" stat shows the correct all-time count.
- [ ] "Top category" shows the correct category or "—" when no expenses exist.
- [ ] The empty state is shown in place of stats when the user has zero expenses.
- [ ] "Add Expense" link navigates to `/expenses/add` without a 404.
- [ ] "Sign out" link calls `/logout` and clears the session.
- [ ] Page is fully responsive at 900 px and 600 px breakpoints.
- [ ] Page uses only CSS variables — no hard-coded hex colors in `profile.css`.
- [ ] No console or server errors on any path through the page.
- [ ] All SQL queries use parameterized syntax (`?` placeholders).
