# pyrefly: ignore [missing-import]
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "spendly-dev-secret"


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if session.get("user_id"):
            return redirect(url_for("profile"))
        return render_template("register.html")

    # --- POST: process form submission ---
    name     = request.form.get("name",     "").strip()
    email    = request.form.get("email",    "").strip()
    password = request.form.get("password", "").strip()

    # Server-side validation
    if not name or not email or not password:
        return render_template("register.html",
                               error="All fields are required.")

    if len(password) < 8:
        return render_template("register.html",
                               error="Password must be at least 8 characters.")

    # Insert into database
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password))
        )
        conn.commit()
    except Exception:
        return render_template("register.html",
                               error="An account with that email already exists.")
    finally:
        conn.close()

    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    # Guest-only guard
    if session.get("user_id"):
        return redirect(url_for("profile"))

    if request.method == "GET":
        return render_template("login.html")

    # --- POST: verify credentials ---
    email    = request.form.get("email",    "").strip()
    password = request.form.get("password", "").strip()

    if not email or not password:
        return render_template("login.html",
                               error="All fields are required.")

    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()

    if user is None or not check_password_hash(user["password_hash"], password):
        return render_template("login.html",
                               error="Invalid email or password.")

    session["user_id"] = user["id"]
    return redirect(url_for("profile"))


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    # Auth guard — must be the very first check
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]
    conn = get_db()
    try:
        # 1. Fetch user record (safe columns only — no password_hash exposed)
        user_row = conn.execute(
            "SELECT id, name, email, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        # 2. Total amount spent in the current calendar month
        month_row = conn.execute(
            """SELECT COALESCE(SUM(amount), 0) AS month_total
               FROM expenses
               WHERE user_id = ?
                 AND strftime('%Y-%m', date) = strftime('%Y-%m', 'now')""",
            (user_id,)
        ).fetchone()

        # 3. All-time expense count
        count_row = conn.execute(
            "SELECT COUNT(*) AS total_count FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        # 4. Top spending category (all time)
        top_row = conn.execute(
            """SELECT category, SUM(amount) AS cat_total
               FROM expenses
               WHERE user_id = ?
               GROUP BY category
               ORDER BY cat_total DESC
               LIMIT 1""",
            (user_id,)
        ).fetchone()
    finally:
        conn.close()

    # Format created_at: "YYYY-MM-DD HH:MM:SS" → "26 Jul 2026"
    # Using %d (zero-padded) for cross-platform safety on Windows
    raw_date = user_row["created_at"] or ""
    try:
        member_since = datetime.strptime(
            raw_date[:10], "%Y-%m-%d"
        ).strftime("%d %b %Y")
    except (ValueError, TypeError):
        member_since = raw_date

    # Build safe context dicts — password_hash is never included
    user = {
        "name":         user_row["name"],
        "email":        user_row["email"],
        "member_since": member_since,
    }
    stats = {
        "month_total":  month_row["month_total"],
        "total_count":  count_row["total_count"],
        "top_category": top_row["category"] if top_row else None,
    }

    return render_template("profile.html", user=user, stats=stats)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


# ------------------------------------------------------------------ #
# Database initialisation                                             #
# ------------------------------------------------------------------ #
with app.app_context():
    init_db()
    seed_db()


if __name__ == "__main__":
    app.run(debug=True, port=5001)
