# Implementation Plan: Login and Logout (Step 3)

Based on [03-login-logout.md](file:///c:/Users/Hp/Downloads/expense-tracker/expense-tracker/.gemini/specs/03-login-logout.md)

## Background

Two files need changes. No new files, no schema changes.

| File | Current State | Required Change |
|------|--------------|-----------------|
| `app.py` | `GET /login` renders template; `GET /logout` returns a string | Add `secret_key`, new imports, `POST /login` handler, real `GET /logout`, guest guards on `GET /login` and `GET /register` |
| `templates/base.html` | Navbar always shows Sign in / Get started | Make nav conditional on `session.get('user_id')` |

`templates/login.html` needs **no changes** — form method, action, and error block are already correct.

---

## Proposed Changes

### Application Layer

---

#### [MODIFY] [app.py](file:///c:/Users/Hp/Downloads/expense-tracker/expense-tracker/app.py)

**Change 1 — Imports** (lines 2–3)

Add `session` to the Flask import and `check_password_hash` to the Werkzeug import:

```diff
- from flask import Flask, render_template, request, redirect, url_for
- from werkzeug.security import generate_password_hash
+ from flask import Flask, render_template, request, redirect, url_for, session
+ from werkzeug.security import generate_password_hash, check_password_hash
```

**Change 2 — Secret key** (line 7, after `app.config`)

Flask sessions require a secret key — without it, the session cookie cannot be signed:

```diff
  app.config["TEMPLATES_AUTO_RELOAD"] = True
+ app.secret_key = "spendly-dev-secret"
```

**Change 3 — `GET /register` guest-only guard** (lines 29–32)

Add a redirect at the top of the existing `register()` GET branch so logged-in users cannot reach the form:

```diff
  @app.route("/register", methods=["GET", "POST"])
  def register():
      if request.method == "GET":
+         if session.get("user_id"):
+             return redirect(url_for("profile"))
          return render_template("register.html")
```

**Change 4 — `GET /login` + `POST /login`** (lines 65–67)

Replace the GET-only stub with a full GET/POST handler:

```diff
- @app.route("/login")
- def login():
-     return render_template("login.html")
+ @app.route("/login", methods=["GET", "POST"])
+ def login():
+     # Guest-only guard
+     if session.get("user_id"):
+         return redirect(url_for("profile"))
+
+     if request.method == "GET":
+         return render_template("login.html")
+
+     # --- POST: verify credentials ---
+     email    = request.form.get("email",    "").strip()
+     password = request.form.get("password", "").strip()
+
+     if not email or not password:
+         return render_template("login.html",
+                                error="All fields are required.")
+
+     conn = get_db()
+     try:
+         user = conn.execute(
+             "SELECT * FROM users WHERE email = ?", (email,)
+         ).fetchone()
+     finally:
+         conn.close()
+
+     if user is None or not check_password_hash(user["password_hash"], password):
+         return render_template("login.html",
+                                error="Invalid email or password.")
+
+     session["user_id"] = user["id"]
+     return redirect(url_for("profile"))
```

**Change 5 — `GET /logout`** (lines 74–76)

Replace the placeholder string with a real handler:

```diff
- @app.route("/logout")
- def logout():
-     return "Logout — coming in Step 3"
+ @app.route("/logout")
+ def logout():
+     session.clear()
+     return redirect(url_for("landing"))
```

---

### Template Layer

---

#### [MODIFY] [templates/base.html](file:///c:/Users/Hp/Downloads/expense-tracker/expense-tracker/templates/base.html)

**Change — Session-aware navbar** (lines 25–28)

Replace the static nav links with a Jinja conditional block:

```diff
- <div class="nav-links">
-     <a href="{{ url_for('login') }}">Sign in</a>
-     <a href="{{ url_for('register') }}" class="nav-cta">Get started</a>
- </div>
+ <div class="nav-links">
+     {% if session.get('user_id') %}
+         <a href="{{ url_for('logout') }}" class="nav-cta">Sign out</a>
+     {% else %}
+         <a href="{{ url_for('login') }}">Sign in</a>
+         <a href="{{ url_for('register') }}" class="nav-cta">Get started</a>
+     {% endif %}
+ </div>
```

---

## Verification Plan

### Automated

```bash
.venv\Scripts\python.exe -c "from app import app; print('App import OK')"
```

### Manual — Test at `http://localhost:5001`

| # | Scenario | Expected Result |
|---|----------|-----------------|
| 1 | Visit `GET /login` (logged out) | Login form renders cleanly |
| 2 | Submit empty email or password | Re-renders form: `"All fields are required."` |
| 3 | Submit wrong password | Re-renders form: `"Invalid email or password."` |
| 4 | Submit non-existent email | Re-renders form: `"Invalid email or password."` |
| 5 | Submit `demo@spendly.com` / `demo123` | Redirects to `/profile` |
| 6 | After login, navbar shows **Sign out** only | ✓ |
| 7 | After login, visit `GET /login` | Redirects to `/profile` (form not shown) |
| 8 | After login, visit `GET /register` | Redirects to `/profile` (form not shown) |
| 9 | Click **Sign out** | Redirects to `/` (landing page) |
| 10 | After logout, navbar shows **Sign in / Get started** | ✓ |
| 11 | After logout, visit `/logout` again | Redirects to `/` cleanly (no crash) |
