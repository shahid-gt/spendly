# Spendly Design System Reference

## Brand Identity
- **Product**: Spendly — personal expense tracker
- **Tagline**: "Track every rupee. Own your finances."
- **Brand mark**: ◈ symbol + "Spendly" wordmark
- **Tone**: Trustworthy, minimal, modern — like a premium fintech tool

## Typography Scale

| Role | Font | Weight | Size |
|---|---|---|---|
| Display heading | DM Serif Display | 400 (regular) | clamp(2.5rem, 5vw, 4rem) |
| Section heading | DM Serif Display | 400 | 1.2rem–2rem |
| Monetary amounts | DM Serif Display | 400 | 1.5rem–2rem |
| Body text | DM Sans | 400 | 1rem |
| Labels / captions | DM Sans | 500 | 0.8rem–0.875rem |
| Buttons | DM Sans | 500 | 0.9rem–0.95rem |

## Spacing System (8px base)
- `0.25rem` = 4px — micro gaps
- `0.5rem` = 8px — tight gaps (icon to label)
- `0.75rem` = 12px — form element gaps
- `1rem` = 16px — standard gap
- `1.25rem` = 20px — form group spacing
- `1.5rem` = 24px — card padding (minimum)
- `2rem` = 32px — card padding (preferred), section horizontal padding
- `3rem` = 48px — section vertical padding (small screens)
- `4rem–6rem` = 64–96px — hero section padding

## Shadow Scale
```css
/* Card, default */
box-shadow: 0 4px 24px rgba(0,0,0,0.05);

/* Card, elevated (hover) */
box-shadow: 0 8px 40px rgba(0,0,0,0.08);

/* Dropdown / floating */
box-shadow: 0 12px 48px rgba(0,0,0,0.12);

/* Input focus ring */
box-shadow: 0 0 0 3px var(--accent-light);
```

## Border Radius Usage
| Context | Value |
|---|---|
| Buttons | `var(--radius-sm)` = 6px |
| Input fields | `var(--radius-sm)` = 6px |
| Cards / panels | `var(--radius-md)` = 12px |
| Large cards / modals | `var(--radius-lg)` = 20px |
| Pills / badges | 999px (fully rounded) |

## Colour Usage Guide

### Primary Accent (Forest Green `#1a472a`)
- CTA button hover
- Active nav links
- Input focus border
- Progress bars
- Positive trend indicators

### Secondary Accent (Amber `#c17f24`)
- Secondary CTAs
- Warning states (budget near limit)
- Footer brand icon
- Category color: misc/shopping

### Danger (`#c0392b`)
- Delete actions
- Error messages
- Negative trend indicators (overspend)

### Neutral Ink Scale
- `--ink` — headings, primary text
- `--ink-soft` — secondary text, labels
- `--ink-muted` — captions, descriptions
- `--ink-faint` — placeholders, disabled

### Background Scale
- `--paper` — page background (warm off-white)
- `--paper-warm` — alternate section bg
- `--paper-card` — card surface (white)

## Component Naming Convention (BEM-lite)

```
.block
.block__element
.block__element--modifier
```

**Examples from existing code:**
- `.hero-v2__badge` — badge inside hero v2 block
- `.hero-v2__stat-tile` — stat tile inside hero v2
- `.hero-v2__chart-bar--food` — food-coloured chart bar

**For new components follow the same pattern:**
- `.dashboard__sidebar` — sidebar inside dashboard
- `.stat-card__value` — value inside stat card
- `.txn-row__icon--food` — food icon modifier on transaction row

## Responsive Breakpoints

| Breakpoint | Width | Behaviour |
|---|---|---|
| Desktop | > 900px | Full multi-column layout |
| Tablet | 600px–900px | Reduced columns, stacked sections |
| Mobile | < 600px | Single column, nav simplified |

## Category Color System

Each expense category has a distinct colour token for chart bars and icon badges:

| Category | Color | Class modifier |
|---|---|---|
| Food | `var(--accent)` forest green | `--food` |
| Travel | `#5b7fa6` slate blue | `--travel` |
| Bills | `#8b5e83` muted purple | `--bills` |
| Shopping | `var(--accent-2)` amber | `--shopping` |
| Health | `#b5524a` muted red | `--health` |
| Entertainment | `#4a7c7a` teal | `--entertainment` |
| Other | `var(--ink-muted)` grey | `--other` |
