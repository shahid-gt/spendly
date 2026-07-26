# Implementation Plan: Profile Page (Step 4)

Based on [04-profile-page.md](file:///c:/Users/Hp/Downloads/expense-tracker/expense-tracker/.gemini/specs/04-profile-page.md)

## Background

Three files need changes. One file is modified, two are created from scratch. No schema changes.

| File | Status | Required Change |
|------|--------|-----------------|
| `app.py` | MODIFY | Replace 3-line stub at `/profile` with a full authenticated route handler |
| `templates/profile.html` | CREATE | New Jinja2 template extending `base.html` with 5 defined sections |
| `static/css/profile.css` | CREATE | Scoped styles for profile layout, account card, stat cards, quick-actions |

No changes required to `templates/base.html` — the session-aware navbar was already implemented in Step 3.

---

## Proposed Changes

### 1 — Application Layer

---

#### [MODIFY] [app.py](file:///c:/Users/Hp/Downloads/expense-tracker/expense-tracker/app.py)

**What changes:** Lines 111–113 contain the placeholder stub:

```python
@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"
```

Replace it entirely with a real handler that:
- Guards against unauthenticated access
- Runs 4 parameterised SQL queries
- Formats `created_at` to a human-readable string in Python
- Passes a safe `user` dict and a `stats` dict to the template

**Full replacement (diff format):**

```diff
- @app.route("/profile")
- def profile():
-     return "Profile page — coming in Step 4"
+ @app.route("/profile")
+ def profile():
+     # Auth guard — must be first
+     if not session.get("user_id"):
+         return redirect(url_for("login"))
+
+     user_id = session["user_id"]
+     conn = get_db()
+     try:
+         # 1. Fetch user record (safe columns only — no password_hash)
+         user_row = conn.execute(
+             "SELECT id, name, email, created_at FROM users WHERE id = ?",
+             (user_id,)
+         ).fetchone()
+
+         # 2. Total amount spent in the current calendar month
+         month_row = conn.execute(
+             """SELECT COALESCE(SUM(amount), 0) AS month_total
+                FROM expenses
+                WHERE user_id = ?
+                  AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')""",
+             (user_id,)
+         ).fetchone()
+
+         # 3. All-time expense count
+         count_row = conn.execute(
+             "SELECT COUNT(*) AS total_count FROM expenses WHERE user_id = ?",
+             (user_id,)
+         ).fetchone()
+
+         # 4. Top spending category (all time)
+         top_row = conn.execute(
+             """SELECT category, SUM(amount) AS cat_total
+                FROM expenses
+                WHERE user_id = ?
+                GROUP BY category
+                ORDER BY cat_total DESC
+                LIMIT 1""",
+             (user_id,)
+         ).fetchone()
+     finally:
+         conn.close()
+
+     # Format created_at: "YYYY-MM-DD HH:MM:SS" → "26 Jul 2026"
+     from datetime import datetime
+     raw_date = user_row["created_at"] or ""
+     try:
+         member_since = datetime.strptime(
+             raw_date[:10], "%Y-%m-%d"
+         ).strftime("%-d %b %Y")
+     except (ValueError, TypeError):
+         member_since = raw_date
+
+     # Build safe context dicts
+     user = {
+         "name":         user_row["name"],
+         "email":        user_row["email"],
+         "member_since": member_since,
+     }
+     stats = {
+         "month_total":   month_row["month_total"],
+         "total_count":   count_row["total_count"],
+         "top_category":  top_row["category"] if top_row else None,
+     }
+
+     return render_template("profile.html", user=user, stats=stats)
```

> **Note on `strftime("%-d %b %Y")`:** The `%-d` format (day without leading zero)
> works on Linux/macOS. On Windows use `%#d`. Since the dev server runs on Windows,
> use `%d` (zero-padded) as a safe cross-platform fallback, or strip the leading zero
> manually with `.lstrip("0")`. The simplest safe version:
> ```python
> member_since = datetime.strptime(raw_date[:10], "%Y-%m-%d").strftime("%d %b %Y")
> ```

**Also add the import at the top of `app.py`** (move `from datetime import datetime`
to the module top-level to keep imports clean, not inside the function):

```diff
  # pyrefly: ignore [missing-import]
  from flask import Flask, render_template, request, redirect, url_for, session
  from werkzeug.security import generate_password_hash, check_password_hash
+ from datetime import datetime
  from database.db import get_db, init_db, seed_db
```

And remove the inline `from datetime import datetime` inside the route function.

---

### 2 — Template Layer

---

#### [CREATE] [templates/profile.html](file:///c:/Users/Hp/Downloads/expense-tracker/expense-tracker/templates/profile.html)

Extends `base.html`. Loads `profile.css` in `{% block head %}`.

**Full template structure:**

```html
{% extends "base.html" %}

{% block title %}My Profile — Spendly{% endblock %}

{% block head %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/profile.css') }}">
{% endblock %}

{% block content %}
<div class="profile-page">

  <!-- ── Page Header ─────────────────────────────────────────── -->
  <header class="profile-header">
    <h1 class="profile-header__greeting">
      Hello, {{ user.name.split()[0] }} 👋
    </h1>
    <p class="profile-header__tagline">
      Here's a quick look at your Spendly account.
    </p>
  </header>

  <!-- ── Account Info Card ────────────────────────────────────── -->
  <section class="profile-section" aria-label="Account information">
    <h2 class="profile-section__title">Account</h2>
    <div class="account-card" id="account-info-card">
      <div class="account-card__row">
        <span class="account-card__label">Full name</span>
        <span class="account-card__value">{{ user.name }}</span>
      </div>
      <div class="account-card__row">
        <span class="account-card__label">Email</span>
        <span class="account-card__value">{{ user.email }}</span>
      </div>
      <div class="account-card__row">
        <span class="account-card__label">Member since</span>
        <span class="account-card__value">{{ user.member_since }}</span>
      </div>
    </div>
  </section>

  <!-- ── Spending Snapshot ─────────────────────────────────────── -->
  <section class="profile-section" aria-label="Spending snapshot">
    <h2 class="profile-section__title">Spending snapshot</h2>

    {% if stats.total_count == 0 %}
      <!-- Empty State -->
      <div class="empty-state" id="empty-expenses-state">
        <p class="empty-state__icon" aria-hidden="true">₹</p>
        <h3 class="empty-state__title">No expenses yet</h3>
        <p class="empty-state__body">
          Add your first expense to see your spending summary here.
        </p>
        <a href="{{ url_for('add_expense') }}" class="btn-primary" id="empty-state-add-btn">
          Add expense
        </a>
      </div>

    {% else %}
      <!-- Stat Cards Row -->
      <div class="stat-grid">

        <div class="stat-card" id="stat-month-total">
          <p class="stat-card__label">This month</p>
          <p class="stat-card__value">₹{{ "%.2f"|format(stats.month_total) }}</p>
          <p class="stat-card__sub">total spent</p>
        </div>

        <div class="stat-card" id="stat-total-count">
          <p class="stat-card__label">Total expenses</p>
          <p class="stat-card__value">{{ stats.total_count }}</p>
          <p class="stat-card__sub">all time</p>
        </div>

        <div class="stat-card" id="stat-top-category">
          <p class="stat-card__label">Top category</p>
          <p class="stat-card__value">
            {% if stats.top_category %}
              {{ stats.top_category }}
            {% else %}
              —
            {% endif %}
          </p>
          <p class="stat-card__sub">highest spend</p>
        </div>

      </div>
    {% endif %}
  </section>

  <!-- ── Quick Actions ─────────────────────────────────────────── -->
  <section class="profile-section" aria-label="Quick actions">
    <h2 class="profile-section__title">Actions</h2>
    <div class="quick-actions" id="quick-actions-row">
      <a href="{{ url_for('add_expense') }}" class="btn-primary" id="btn-add-expense">
        + Add Expense
      </a>
      <a href="{{ url_for('logout') }}" class="btn-ghost" id="btn-sign-out">
        Sign out
      </a>
    </div>
  </section>

</div>
{% endblock %}
```

**Template decisions:**
- `user.name.split()[0]` extracts the first name for the greeting — safe even for single-word names.
- `"%.2f"|format(stats.month_total)` formats the float to 2 decimal places via Jinja2's `format` filter.
- The empty-state block is shown when `stats.total_count == 0`; the stat grid is shown otherwise.
- No JS required — fully server-rendered.

---

### 3 — Styling Layer

---

#### [CREATE] [static/css/profile.css](file:///c:/Users/Hp/Downloads/expense-tracker/expense-tracker/static/css/profile.css)

Scoped to the `.profile-page` wrapper. Uses only `var(--*)` design tokens from `style.css`.

```css
/* ------------------------------------------------------------------ */
/* Profile Page Layout                                                  */
/* ------------------------------------------------------------------ */

.profile-page {
    max-width: 760px;
    margin: 0 auto;
    padding: 3rem 2rem 5rem;
    display: flex;
    flex-direction: column;
    gap: 2.5rem;
}

/* ------------------------------------------------------------------ */
/* Page Header                                                          */
/* ------------------------------------------------------------------ */

.profile-header__greeting {
    font-family: var(--font-display);
    font-size: clamp(1.75rem, 4vw, 2.5rem);
    color: var(--ink);
    margin-bottom: 0.4rem;
}

.profile-header__tagline {
    font-size: 1rem;
    color: var(--ink-muted);
}

/* ------------------------------------------------------------------ */
/* Section                                                              */
/* ------------------------------------------------------------------ */

.profile-section__title {
    font-family: var(--font-body);
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    color: var(--ink-muted);
    margin-bottom: 1rem;
}

/* ------------------------------------------------------------------ */
/* Account Card                                                         */
/* ------------------------------------------------------------------ */

.account-card {
    background: var(--paper-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    overflow: hidden;
}

.account-card__row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border-soft);
}

.account-card__row:last-child {
    border-bottom: none;
}

.account-card__label {
    font-size: 0.85rem;
    font-weight: 500;
    color: var(--ink-muted);
}

.account-card__value {
    font-size: 0.95rem;
    color: var(--ink);
    font-weight: 400;
}

/* ------------------------------------------------------------------ */
/* Stat Grid                                                            */
/* ------------------------------------------------------------------ */

.stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
}

.stat-card {
    background: var(--paper-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    transition: box-shadow 0.2s ease;
}

.stat-card:hover {
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.07);
}

.stat-card__label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--ink-muted);
}

.stat-card__value {
    font-family: var(--font-display);
    font-size: 1.75rem;
    color: var(--ink);
    line-height: 1.1;
}

.stat-card__sub {
    font-size: 0.8rem;
    color: var(--ink-faint);
}

/* ------------------------------------------------------------------ */
/* Empty State                                                          */
/* ------------------------------------------------------------------ */

.empty-state {
    background: var(--paper-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 3rem 2rem;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
}

.empty-state__icon {
    font-size: 2rem;
    color: var(--accent-light);
    font-family: var(--font-display);
}

.empty-state__title {
    font-family: var(--font-display);
    font-size: 1.2rem;
    color: var(--ink);
}

.empty-state__body {
    font-size: 0.9rem;
    color: var(--ink-muted);
    max-width: 320px;
}

/* ------------------------------------------------------------------ */
/* Quick Actions                                                        */
/* ------------------------------------------------------------------ */

.quick-actions {
    display: flex;
    gap: 1rem;
    align-items: center;
}

/* ------------------------------------------------------------------ */
/* Responsive                                                           */
/* ------------------------------------------------------------------ */

@media (max-width: 900px) {
    .stat-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 600px) {
    .profile-page {
        padding: 2rem 1rem 4rem;
    }

    .stat-grid {
        grid-template-columns: 1fr;
    }

    .account-card__row {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.2rem;
    }

    .quick-actions {
        flex-direction: column;
        align-items: stretch;
    }

    .quick-actions .btn-primary,
    .quick-actions .btn-ghost {
        text-align: center;
    }
}
```

---

## Execution Order

Implement in this exact sequence to avoid broken intermediate states:

1. **Add `from datetime import datetime`** to the import block at the top of `app.py`.
2. **Replace the `/profile` stub** in `app.py` (lines 111–113) with the full handler.
3. **Create `static/css/profile.css`** with the styles above.
4. **Create `templates/profile.html`** with the template above.
5. **Verify** by running the app and manually testing all Definition of Done items.

---

## Verification Plan

### Smoke test (app import)

```bash
.venv\Scripts\python.exe -c "from app import app; print('Import OK')"
```

### Manual test matrix — run at `http://localhost:5001`

| # | Scenario | Expected Result |
|---|----------|-----------------|
| 1 | Visit `GET /profile` while **logged out** | Redirects to `/login` |
| 2 | Log in as `demo@spendly.com` / `demo123`, get redirected to `/profile` | Profile page renders without errors |
| 3 | Check page header | Shows first name from DB (e.g. "Hello, Demo 👋") |
| 4 | Check Account card | Shows full name, email, and "Member since" date in `DD Mon YYYY` format |
| 5 | Check "This month" stat | Shows correct sum of expenses in the current month (₹ format with 2 decimals) |
| 6 | Check "Total expenses" stat | Shows correct all-time count |
| 7 | Check "Top category" stat | Shows the category with the highest cumulative spend |
| 8 | Click "Add Expense" button | Navigates to `/expenses/add` (placeholder — no 404) |
| 9 | Click "Sign out" | Clears session, redirects to `/` |
| 10 | After signing out, visit `/profile` | Redirects to `/login` |
| 11 | Register a **new** user (zero expenses), log in, visit `/profile` | Empty state renders in place of stat cards |
| 12 | Resize browser to ≤ 600 px | Stat cards stack vertically; account rows stack; action buttons stretch full-width |
| 13 | Open browser DevTools → Console | No JavaScript or server errors |
