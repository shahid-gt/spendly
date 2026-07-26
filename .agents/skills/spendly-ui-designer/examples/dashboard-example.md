# Example: Dashboard Page

**Trigger:** "Design the dashboard page"

This example shows the expected output structure for a full page design request.

---

## UI Structure Overview

- **Sidebar (left, 240px)**: Navigation links with icons, user profile snippet at bottom
- **Main content (right, flex-grow)**: Page header + 4 stat cards + recent transactions table
- **Stat cards row**: Total Spent, Budget Left, Transactions Count, Biggest Category
- **Transactions table**: Date | Category icon | Description | Amount — last 10 entries
- **Empty state**: Shown when user has no expenses yet

## File Outputs Expected

1. `templates/dashboard.html` — extends base.html
2. `static/css/dashboard.css` — scoped styles
3. `static/js/dashboard.js` — optional (only if filters needed)

## Key Design Decisions

- Sidebar uses `position: sticky; top: 60px` so it stays visible while scrolling
- Stat cards use `display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))`
- Transaction rows use `:nth-child(even) { background: var(--paper-warm) }` for zebra striping
- Currency displayed in DM Serif Display for visual weight
- Active sidebar link: `background: var(--accent-light); color: var(--accent);`

## Sample Stat Card CSS

```css
/* --- Stat Card --- */
.stat-card {
  background: var(--paper-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  transition: box-shadow 0.2s ease;
}

.stat-card:hover {
  box-shadow: 0 8px 40px rgba(0,0,0,0.08);
}

.stat-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-card__label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--ink-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.stat-card__icon {
  width: 18px;
  height: 18px;
  color: var(--ink-faint);
}

.stat-card__value {
  font-family: var(--font-display);
  font-size: 1.75rem;
  color: var(--ink);
  line-height: 1.1;
}

.stat-card__delta {
  font-size: 0.8rem;
  font-weight: 500;
}

.stat-card__delta--up   { color: var(--danger); }
.stat-card__delta--down { color: var(--accent); }
.stat-card__delta--neutral { color: var(--ink-muted); }
```
