# AegisCare — UI Guidelines

## Design Principles

AegisCare should feel like real clinical software:
calm, readable, trustworthy, functional.
It should NOT feel like a startup product, AI chatbot, or consumer app.

---

## What to Avoid (Strictly)

- Glassmorphism (blurred glass card effects)
- Neon colors or glowing borders
- Gradient backgrounds (especially purple-to-blue)
- Animated floating objects or decorative shapes
- Emojis in clinical content
- Futuristic or dystopian aesthetics
- Marketing-style copy ("Revolutionize your healthcare!")
- Excessive animations on clinical data

---

## Colors

| Purpose             | Value        | Usage                              |
|---------------------|--------------|------------------------------------|
| Background          | #F8F9FA      | Page background                    |
| Surface             | #FFFFFF      | Cards, panels                      |
| Border              | #E2E8F0      | Dividers, input borders            |
| Text Primary        | #1A202C      | Body text, headings                |
| Text Secondary      | #4A5568      | Labels, metadata                   |
| Text Muted          | #718096      | Timestamps, hints                  |
| Accent Blue         | #2B6CB0      | Primary actions, links             |
| Severity Green      | #276749      | Low risk indicators                |
| Severity Green BG   | #F0FFF4      | Green severity card background     |
| Severity Yellow     | #744210      | Medium risk indicators             |
| Severity Yellow BG  | #FFFBEB      | Yellow severity card background    |
| Severity Red        | #9B2C2C      | High risk indicators               |
| Severity Red BG     | #FFF5F5      | Red severity card background       |
| Severity Critical   | #63171B      | Critical / emergency               |
| Severity Critical BG| #FFF0F0      | Critical card background           |
| Success             | #276749      | Confirmations                      |
| Error               | #9B2C2C      | Error states                       |

---

## Typography

Font family: 'Inter', system-ui, sans-serif
(Fallback to Manrope if Inter unavailable)

| Element          | Size  | Weight | Line Height |
|------------------|-------|--------|-------------|
| Page title       | 24px  | 700    | 1.2         |
| Section heading  | 18px  | 600    | 1.3         |
| Card title       | 16px  | 600    | 1.4         |
| Body text        | 14px  | 400    | 1.6         |
| Label / caption  | 12px  | 400    | 1.5         |
| Small / meta     | 11px  | 400    | 1.4         |

Never use font sizes below 11px.
Never bold entire paragraphs.

---

## Spacing

Use consistent 4px base unit.

| Level  | Value | Usage                                |
|--------|-------|--------------------------------------|
| xs     | 4px   | Between label and input              |
| sm     | 8px   | Within a card section                |
| md     | 16px  | Between cards, form fields           |
| lg     | 24px  | Between major sections               |
| xl     | 40px  | Between page sections                |
| xxl    | 64px  | Top padding for hero/page header     |

Max readable content width: 720px for prose.
Dashboard panels: fluid within grid.

---

## Severity Indicator

The severity indicator is the most critical UI element.
It must be immediately readable and scannable.

Design:
- Compact pill or badge at the top of the chat panel
- Color: background + text as per color table
- Text: "Low Risk", "Moderate Risk", "High Risk", "Critical"
- Risk score shown as a number: "72 / 100"
- A simple horizontal progress bar (no animations)
- Border-left accent line matching severity color on the chat panel

No pulsing. No flashing. No animation. Calm but clear.

---

## Streamlit Custom CSS Guidelines

- Inject CSS via st.markdown with unsafe_allow_html=True
- Keep all custom styles in frontend/assets/css/main.css
- Load once in app.py with open() and inject into page
- Use CSS custom properties (variables) for theming
- Target Streamlit class names carefully (they can change on updates)

---

## Chat Interface

- Doctor/AI messages: left-aligned, subtle background
- Patient messages: right-aligned, slightly darker background
- No avatar icons — too consumer-app-like
- Show timestamp on each message in small muted text
- Input box at bottom, full width
- Voice input button to the left of text input
- Session info bar above chat (patient name, session ID, time elapsed)

---

## Dashboard

- Grid layout: 3 columns on wide screens, 1 on mobile
- Hospital load: horizontal bar chart (Plotly)
- Escalation timeline: simple vertical list, newest at top
- Doctor availability: status dots (green/yellow/red) next to name
- No decorative charts — all charts must show actionable data

---

## Accessibility

- Minimum 4.5:1 color contrast ratio for all text
- All interactive elements keyboard-accessible
- Screen reader labels on all form inputs
- No information conveyed by color alone (always add text)
- Font size minimum 14px for body content
