# AegisCare — Frontend Specification Document

**Version:** 1.0  
**Date:** August 21, 2026  
**Status:** Draft  

---

## Table of Contents

1. [Design Philosophy](#1-design-philosophy)
2. [Color System](#2-color-system)
3. [Typography](#3-typography)
4. [Spacing & Layout](#4-spacing--layout)
5. [Component Library](#5-component-library)
6. [Page Specifications](#6-page-specifications)
7. [Voice & Interaction Patterns](#7-voice--interaction-patterns)
8. [Accessibility](#8-accessibility)
9. [API & Integration Spec — Backend (FastAPI)](#9-api--integration-spec--backend-fastapi)
10. [API & Integration Spec — Supabase](#10-api--integration-spec--supabase)
11. [API & Integration Spec — Google Gemini](#11-api--integration-spec--google-gemini)
12. [API & Integration Spec — Voice Pipeline](#12-api--integration-spec--voice-pipeline)
13. [API & Integration Spec — Agora (Video)](#13-api--integration-spec--agora-video)
14. [API & Integration Spec — OpenAI (Fallback)](#14-api--integration-spec--openai-fallback)
15. [Environment Variables Reference](#15-environment-variables-reference)

---

## 1. Design Philosophy

AegisCare must feel like **clinical software** — calm, readable, trustworthy, functional. It is NOT a consumer app, startup product, or AI chatbot.

### Core Principles

| Principle | Meaning |
|-----------|---------|
| **Clarity over beauty** | Every element must serve a clinical purpose. No decoration. |
| **Calm urgency** | Critical information is obvious without being alarming. No flashing, no pulsing. |
| **Scanability** | A doctor should grasp a patient's status in under 3 seconds. |
| **Consistency** | Same patterns across all 5 pages. Predictable layout, predictable behavior. |
| **Accessible** | 4.5:1 contrast minimum. Keyboard-navigable. Screen-reader friendly. |

### Strictly Forbidden

- Glassmorphism (blurred glass effects)
- Neon colors or glowing borders
- Gradient backgrounds (especially purple-to-blue)
- Animated floating objects or decorative shapes
- Emojis in clinical content
- Futuristic or dystopian aesthetics
- Marketing copy ("Revolutionize your healthcare!")
- Excessive animations on clinical data
- Avatars in chat (too consumer-app-like)

---

## 2. Color System

All colors are defined as CSS custom properties in `frontend/styles/main.css`.

### Base Palette

| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| `--bg-primary` | `#F8F9FA` | 248, 249, 250 | Page background |
| `--bg-surface` | `#FFFFFF` | 255, 255, 255 | Cards, panels, modals |
| `--bg-hover` | `#EDF2F7` | 237, 242, 247 | Hover state on interactive surfaces |
| `--border-color` | `#E2E8F0` | 226, 232, 240 | Dividers, input borders, card borders |
| `--border-focus` | `#2B6CB0` | 43, 108, 176 | Focus ring on inputs, buttons |

### Text Colors

| Token | Hex | Usage | Contrast on `#FFFFFF` |
|-------|-----|-------|----------------------|
| `--text-primary` | `#1A202C` | Headings, body text, patient data | 15.4:1 |
| `--text-secondary` | `#4A5568` | Labels, metadata, form labels | 7.1:1 |
| `--text-muted` | `#718096` | Timestamps, hints, captions | 4.6:1 |
| `--text-inverse` | `#FFFFFF` | Text on dark/colored backgrounds | — |

### Brand / Accent

| Token | Hex | Usage |
|-------|-----|-------|
| `--accent-blue` | `#2B6CB0` | Primary buttons, links, focus rings, active nav |
| `--accent-blue-hover` | `#2C5282` | Button hover state |
| `--accent-blue-light` | `#EBF4FF` | Blue background tint (info cards) |

### Severity System (Critical — Most-Used Visual Element)

| Severity | Background | Text | Border/Left Accent | Usage |
|----------|-----------|------|-------------------|-------|
| **Green** | `#F0FFF4` | `#276749` | `#276749` | Low risk — monitor |
| **Yellow** | `#FFFBEB` | `#744210` | `#D69E2E` | Medium risk — priority attention |
| **Red** | `#FFF5F5` | `#9B2C2C` | `#E53E3E` | High risk — urgent intervention |
| **Critical** | `#FFF0F0` | `#63171B` | `#C53030` | Emergency — escalate now |

### Semantic Colors

| Token | Hex | Usage |
|-------|-----|-------|
| `--color-success` | `#276749` | Confirmations, completed actions, "Connected" status |
| `--color-warning` | `#D69E2E` | Cautions, load warnings |
| `--color-error` | `#9B2C2C` | Errors, failures, disconnections |
| `--color-info` | `#2B6CB0` | Informational messages, tips |

### Doctor/Status Dots (Dashboard)

| Status | Color | Meaning |
|--------|-------|---------|
| Available | `#276749` | Doctor is free, can take patients |
| Busy | `#D69E2E` | Doctor is with a patient |
| On Call | `#2B6CB0` | Doctor is on-call but not in department |
| Offline | `#A0AEC0` | Doctor is off-shift |

---

## 3. Typography

**Primary Font:** `'Inter', system-ui, sans-serif`  
**Fallback:** `'Manrope', system-ui, sans-serif`  
**Monospace (code/data):** `'JetBrains Mono', 'Fira Code', monospace`

### Type Scale

| Name | Size | Weight | Line Height | Letter Spacing | Usage |
|------|------|--------|-------------|----------------|-------|
| `h1` | 24px | 700 | 1.2 | -0.02em | Page titles ("Dashboard", "Patient Triage") |
| `h2` | 18px | 600 | 1.3 | -0.01em | Section headings ("Risk Distribution", "Patient Info") |
| `h3` | 16px | 600 | 1.4 | 0 | Card titles, subsection headers |
| `body` | 14px | 400 | 1.6 | 0 | Body text, descriptions, form content |
| `label` | 12px | 400 | 1.5 | 0.02em | Form labels, captions, metadata |
| `small` | 11px | 400 | 1.4 | 0.02em | Timestamps, hints, badge text |

### Rules

- **Never use font sizes below 11px.** Clinical data must be readable.
- **Never bold entire paragraphs.** Bold is for emphasis on specific terms only.
- **Body text is always 14px.** This is the minimum for clinical readability.
- **Headings use 700/600 weight only.** Body and labels use 400.
- **Line height 1.6 for body text.** Dense text with 1.4 line height is harder to scan.

### Streamlit Override

Streamlit's default font is overridden in `main.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, sans-serif !important;
}
```

---

## 4. Spacing & Layout

### Spacing Scale (4px Base Unit)

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | 4px | Gap between label and input, icon padding |
| `--space-sm` | 8px | Within a card section, between inline elements |
| `--space-md` | 16px | Between cards, form fields, list items |
| `--space-lg` | 24px | Between major sections (e.g., header to content) |
| `--space-xl` | 40px | Between page-level sections |
| `--space-xxl` | 64px | Top padding for hero/page header area |

### Layout Grid

| Context | Columns | Gutter | Max Width | Notes |
|---------|---------|--------|-----------|-------|
| Dashboard | 3 | 16px | 100% fluid | Responsive: 1 col on mobile |
| Triage | 2 (sidebar + chat) | 24px | 100% fluid | Left: patient info. Right: chat |
| Emergency Center | 1 (full width) | — | 100% fluid | Table-driven layout |
| Coordination | 3 | 16px | 100% fluid | Appointments, doctors, load |
| Analytics | 3 | 16px | 100% fluid | Charts + summary cards |

### Content Width

| Context | Max Width | Notes |
|---------|-----------|-------|
| Prose / Reports | 720px | Readable paragraph width |
| Dashboard panels | Fluid | Fill available grid columns |
| Chat messages | 100% of container | Messages fill their column |
| Forms | 600px max | Prevents overly long input lines |

### Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `--radius-sm` | 4px | Badges, small buttons |
| `--radius-md` | 8px | Cards, inputs, modals |
| `--radius-lg` | 12px | Modal containers |
| `--radius-pill` | 9999px | Severity badges, status pills |

### Shadows

| Token | Value | Usage |
|-------|-------|-------|
| `--shadow-sm` | `0 1px 2px rgba(0,0,0,0.05)` | Cards at rest |
| `--shadow-md` | `0 4px 6px rgba(0,0,0,0.07)` | Cards on hover, dropdowns |
| `--shadow-lg` | `0 10px 15px rgba(0,0,0,0.1)` | Modals |

---

## 5. Component Library

### 5.1 Buttons

#### Primary Button

```css
.btn-primary {
    background-color: var(--accent-blue);
    color: var(--text-inverse);
    border: none;
    border-radius: var(--radius-sm);
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.15s ease;
}

.btn-primary:hover {
    background-color: var(--accent-blue-hover);
}

.btn-primary:focus-visible {
    outline: 2px solid var(--accent-blue);
    outline-offset: 2px;
}
```

| Variant | Background | Text | Usage |
|---------|-----------|------|-------|
| Primary | `#2B6CB0` | White | "Analyze Patient", "Generate Report" |
| Danger | `#9B2C2C` | White | "Escalate Now", "End Session" |
| Ghost | Transparent | `#2B6CB0` | "Cancel", secondary actions |
| Disabled | `#E2E8F0` | `#A0AEC0` | Non-interactive state |

**Size Variants:**

| Size | Padding | Font Size | Usage |
|------|---------|-----------|-------|
| Small | 6px 12px | 12px | Inline actions, table row buttons |
| Medium | 10px 20px | 14px | Standard form submissions |
| Large | 14px 28px | 16px | Primary CTAs ("Analyze Patient") |

### 5.2 Inputs

#### Text Input

```css
.input {
    background-color: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    padding: 10px 12px;
    font-size: 14px;
    color: var(--text-primary);
    width: 100%;
    transition: border-color 0.15s ease;
}

.input:focus {
    border-color: var(--border-focus);
    outline: none;
    box-shadow: 0 0 0 3px rgba(43, 108, 176, 0.15);
}

.input::placeholder {
    color: var(--text-muted);
}
```

| Type | Height | Validation | Error State |
|------|--------|------------|-------------|
| Text | 40px | Required, min/max length | Red border `#E53E3E`, error text below |
| Textarea | Auto (min 80px) | Required, max length | Same as text |
| Select | 40px | Required | Same as text |
| Date/Time | 40px | Valid range | Same as text |

**Error State:**

```css
.input-error {
    border-color: #E53E3E;
}

.input-error-text {
    color: #9B2C2C;
    font-size: 12px;
    margin-top: 4px;
}
```

### 5.3 Cards

#### Base Card

```css
.card {
    background-color: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--space-md);
    margin-bottom: var(--space-md);
}

.card:hover {
    box-shadow: var(--shadow-md);
}
```

#### Metric Card (Dashboard KPIs)

```css
.metric-card {
    background-color: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--space-md);
    text-align: center;
}

.metric-card h4 {
    font-size: 12px;
    color: var(--text-secondary);
    margin-bottom: 4px;
}

.metric-card h2 {
    font-size: 24px;
    font-weight: 700;
    color: var(--text-primary);
}
```

#### Severity Card (Triage Results)

Left border accent matching severity color:

```css
.severity-card-green  { border-left: 4px solid #276749; background: #F0FFF4; }
.severity-card-yellow { border-left: 4px solid #D69E2E; background: #FFFBEB; }
.severity-card-red    { border-left: 4px solid #E53E3E; background: #FFF5F5; }
.severity-card-critical { border-left: 4px solid #C53030; background: #FFF0F0; }
```

#### Patient Card (Emergency Center)

```css
.patient-card {
    background-color: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--space-md);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
```

### 5.4 Severity Badge (Most Critical UI Element)

Must be immediately readable and scannable. Appears at the top of every triage view.

```css
.severity-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: var(--radius-pill);
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.02em;
}
```

| Severity | Background | Text | Label |
|----------|-----------|------|-------|
| Green | `#F0FFF4` | `#276749` | "Low Risk" |
| Yellow | `#FFFBEB` | `#744210` | "Moderate Risk" |
| Red | `#FFF5F5` | `#9B2C2C` | "High Risk" |
| Critical | `#FFF0F0` | `#63171B` | "Critical" |

**Risk Score Display:**

```
┌──────────────────────────────────────────┐
│  [Moderate Risk]        Score: 72 / 100  │
│  ████████████████░░░░░░░░░░░░░░░░░░░░░░  │
└──────────────────────────────────────────┘
```

Progress bar uses severity color. No animation. No pulsing. Calm but clear.

### 5.5 Modals

```css
.modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal {
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    padding: var(--space-lg);
    max-width: 560px;
    width: 90%;
    box-shadow: var(--shadow-lg);
}

.modal-header {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: var(--space-md);
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: var(--space-sm);
    margin-top: var(--space-lg);
}
```

### 5.6 Status Dot (Doctor Availability)

```css
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
}

.status-dot-available  { background-color: #276749; }
.status-dot-busy       { background-color: #D69E2E; }
.status-dot-on-call    { background-color: #2B6CB0; }
.status-dot-offline    { background-color: #A0AEC0; }
```

### 5.7 Chat Interface

| Element | Style | Notes |
|---------|-------|-------|
| AI messages | Left-aligned, `#F7FAFC` background, 14px body | No avatar icon |
| Patient messages | Right-aligned, `#EBF4FF` background, 14px body | No avatar icon |
| Timestamps | 11px, `--text-muted`, below each message | Small, non-intrusive |
| Input box | Full width, bottom of chat area | `st.text_area` or custom |
| Voice button | Left of text input, 40x40px, mic icon | Records audio, sends to `/voice/transcribe` |
| Session info bar | Above chat, full width | Patient name, session ID, time elapsed, severity badge |

### 5.8 Toast / Alert Messages

| Type | Background | Border | Icon | Usage |
|------|-----------|--------|------|-------|
| Success | `#F0FFF4` | `#276749` left | Checkmark | "Analysis completed" |
| Warning | `#FFFBEB` | `#D69E2E` left | Triangle | "Escalation triggered" |
| Error | `#FFF5F5` | `#9B2C2C` left | X circle | "Failed to connect" |
| Info | `#EBF4FF` | `#2B6CB0` left | Info circle | "No escalation required" |

### 5.9 Data Tables

```css
/* Streamlit dataframe override */
.stDataFrame {
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
}
```

| Property | Value |
|----------|-------|
| Header row | `--text-secondary`, 12px, weight 600, background `#F7FAFC` |
| Body rows | `--text-primary`, 14px, weight 400 |
| Row hover | `#F7FAFC` background |
| Row height | 40px (compact) or 48px (comfortable) |
| Zebra striping | None — use borders instead |
| Sortable columns | Click header to sort, arrow indicator |

---

## 6. Page Specifications

### 6.1 Dashboard (Command Center)

**Purpose:** Real-time hospital operations overview for staff.

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  Header: "Dashboard" + "Hospital Operations Overview"       │
├─────────────┬─────────────┬─────────────────────────────────┤
│  Metric     │  Metric     │  Metric                         │
│  Hospital   │  Active     │  Avg Triage                     │
│  Load: 72%  │  Emergencies│  Time: 3.8 min                  │
│  [+8%]      │  5 [+1]    │  [-0.4 min]                     │
├─────────────┴─────────────┴─────────────────────────────────┤
│                                                             │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │  Risk Distribution   │  │  Recent Patient Activity     │ │
│  │  (Plotly Pie Chart)  │  │  (Data Table)                │ │
│  │                      │  │  Time | Patient | Action     │ │
│  │                      │  │  10:42| P-1042 | Update      │ │
│  │                      │  │  10:38| P-1041 | New Session │ │
│  │                      │  │  10:31| P-1040 | Escalated   │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Hospital Load by Facility                              │ │
│  │  (Plotly Horizontal Bar Chart)                          │ │
│  │  General Hospital   ████████████████░░░░  78%           │ │
│  │  City Medical       ██████████████░░░░░░  65%           │ │
│  │  Community Clinic   ████████░░░░░░░░░░░░  40%           │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**Data Sources:**

| Widget | Backend Endpoint | Refresh |
|--------|-----------------|---------|
| Hospital Load | `GET /api/v1/system/status` + DB query | 30s auto-refresh |
| Active Emergencies | `GET /api/v1/patient/` (filtered by severity) | 30s auto-refresh |
| Avg Triage Time | Aggregated from sessions table | 5 min |
| Risk Distribution | Count of active sessions by severity | 30s |
| Recent Activity | Last 10 session events | 30s |
| Load by Facility | `hospital_load` table, latest snapshot per hospital | 5 min |

### 6.2 Patient Triage

**Purpose:** AI-assisted symptom intake and clinical assessment.

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  Header: "Patient Triage" + "AI-assisted clinical assessment"│
├─────────────────────────┬───────────────────────────────────┤
│                         │                                   │
│  Patient Information    │  Triage Chat / Results            │
│  ┌───────────────────┐  │  ┌─────────────────────────────┐ │
│  │ Patient ID: [___] │  │  │ [Severity Badge: Moderate]  │ │
│  │ Duration:   [___] │  │  │ Score: 72/100              │ │
│  └───────────────────┘  │  │ ████████████████░░░░░░░░░░░ │ │
│                         │  │                             │ │
│  Symptoms               │  │ AI: "I see you have fever   │ │
│  ┌───────────────────┐  │  │ and cough for 2 days. Can   │ │
│  │ fever, cough,     │  │  │ you tell me if you have any │ │
│  │ fatigue           │  │  │ difficulty breathing?"       │ │
│  │ (comma separated) │  │  │                             │ │
│  └───────────────────┘  │  │ Patient: "Yes, mild          │ │
│                         │  │ difficulty since this        │ │
│  [Analyze Patient]      │  │ morning."                    │ │
│                         │  │                             │ │
│                         │  │ AI: "I'm updating your      │ │
│                         │  │ severity to HIGH. Let me     │ │
│                         │  │ generate a handoff report." │ │
│                         │  └─────────────────────────────┘ │
│                         │                                   │
│                         │  [Generate Report] [End Session]  │
├─────────────────────────┴───────────────────────────────────┤
│  Assessment Results (appears after analysis)                 │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Clinical Reasoning: "Based on symptom progression..."  │ │
│  │ Suggested Follow-up: "Have you experienced chest pain?" │ │
│  │ Escalation: ⚠️ This case may require escalation        │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

**User Flow:**

1. User enters Patient ID, Duration, and Symptoms
2. Clicks "Analyze Patient" → `POST /api/v1/ai/analyze`
3. Results appear: severity badge, risk score, reasoning, follow-up
4. If escalation needed → warning banner + "Generate Report" button
5. "Generate Report" → `POST /api/v1/report/handoff`
6. Report displayed in expandable section + saved to DB

### 6.3 Emergency Center

**Purpose:** Real-time monitoring of high-risk patients.

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  Header: "Emergency Center" + "High-Risk Patient Monitoring"│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  High Risk Patients                                         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Patient ID │ Risk Score │ Last Update    │ Status       ││
│  │ P-0987     │ 82/100     │ 2 min ago      │ [Escalated]  ││
│  │ P-0991     │ 79/100     │ 5 min ago      │ [Reviewing]  ││
│  │ P-0994     │ 85/100     │ 12 min ago     │ [Critical]   ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
│  Escalation Queue                                           │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ [Live escalation events appear here]                    ││
│  │ Each entry: timestamp + patient ID + severity change     ││
│  │ + action taken                                          ││
│  └─────────────────────────────────────────────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Data Sources:**

| Widget | Backend Endpoint | Refresh |
|--------|-----------------|---------|
| High Risk Patients | Sessions WHERE severity IN ('red', 'critical') | 15s auto-refresh |
| Escalation Queue | Escalations table, last 20, ordered by triggered_at DESC | 15s auto-refresh |

### 6.4 Coordination Dashboard

**Purpose:** Appointment scheduling and doctor availability.

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  Header: "Coordination Dashboard"                           │
├─────────────┬─────────────┬─────────────────────────────────┤
│  Upcoming   │  Doctor     │  Hospital Load                  │
│  Appointments│ Availability│  Summary                       │
│             │             │                                 │
│  10:30 AM   │ Dr. Smith   │  General: 78% [HIGH]           │
│  P-1042     │ ● Available │  City Med: 65% [MODERATE]      │
│  Video      │ Dr. Jones   │  Community: 40% [NORMAL]        │
│             │ ● Busy      │                                 │
│  11:00 AM   │ Dr. Patel   │                                 │
│  P-1039     │ ● Available │                                 │
│  In-person  │             │                                 │
└─────────────┴─────────────┴─────────────────────────────────┘
```

### 6.5 Analytics

**Purpose:** Aggregate reporting and trend analysis.

**Layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  Header: "Analytics" + "Reporting & Insights"               │
├─────────────┬─────────────┬─────────────────────────────────┤
│  Total      │  Avg Triage │  Escalation                     │
│  Sessions   │  Time       │  Rate                           │
│  1,247      │  3.2 min    │  12.4%                          │
├─────────────┴─────────────┴─────────────────────────────────┤
│                                                             │
│  ┌──────────────────────┐  ┌──────────────────────────────┐ │
│  │  Sessions Over Time  │  │  Severity Distribution       │ │
│  │  (Plotly Line Chart) │  │  (Plotly Bar Chart)          │ │
│  └──────────────────────┘  └──────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Top Symptom Categories                                │ │
│  │  (Plotly Horizontal Bar)                                │ │
│  │  Respiratory  ████████████████████  42%                 │ │
│  │  Cardiac      ████████████░░░░░░░░  28%                 │ │
│  │  Neurological ██████░░░░░░░░░░░░░░  15%                 │ │
│  │  General      █████░░░░░░░░░░░░░░░  15%                 │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Voice & Interaction Patterns

### Voice Input Flow

```
1. User clicks mic button
   → Browser requests microphone permission
   → Recording starts (Web Audio API)

2. User speaks symptoms
   → Audio captured as WAV/MP3

3. User clicks stop (or silence detected)
   → Audio sent to POST /api/v1/voice/transcribe
   → Backend: Whisper STT → text
   → Text inserted into symptom input field

4. Triage proceeds as normal
```

### Voice Output Flow

```
1. AI generates text response
   → Text sent to POST /api/v1/voice/respond
   → Backend: XTTS → audio bytes
   → Audio returned to frontend

2. Frontend plays audio
   → HTML5 Audio element
   → User hears AI response
```

### Session Info Bar

Displayed above the chat during active triage:

```
┌─────────────────────────────────────────────────────────────┐
│  Patient: P-1043  │  Session: sess_xyz789  │  04:32 elapsed │
│  Severity: [Moderate Risk]  │  Score: 72/100                │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Accessibility

| Requirement | Implementation |
|-------------|---------------|
| **Color contrast** | Minimum 4.5:1 for all text. Verified against WCAG AA. |
| **Keyboard navigation** | All interactive elements (buttons, inputs, links) are tabbable and activatable with Enter/Space. |
| **Screen reader labels** | Every form input has an `aria-label` or visible `<label>`. |
| **No color-only info** | Severity is always communicated by BOTH color AND text label ("High Risk" text, not just red). |
| **Focus indicators** | 2px outline with `outline-offset: 2px` on all focusable elements. |
| **Minimum font size** | 11px absolute minimum. Body text 14px. |
| **Form error messaging** | Errors appear as text below the input, not just red borders. |
| **Alt text** | All Plotly charts have descriptive titles that serve as alt text. |
| **Reduced motion** | `@media (prefers-reduced-motion: reduce)` disables all transitions. |

---

## 9. API & Integration Spec — Backend (FastAPI)

All API calls from the frontend go through `frontend/utils/api_client.py`, which injects the `Authorization: Bearer <token>` header automatically.

### Base Configuration

| Property | Value | Source |
|----------|-------|--------|
| Base URL | `http://localhost:8000` (dev) or `https://aegiscare-backend.onrender.com` (prod) | `BACKEND_URL` env var |
| Auth Header | `Authorization: Bearer <AEGISCARE_TOKEN>` | `AEGISCARE_TOKEN` env var |
| Timeout | 30 seconds | Hardcoded in APIClient |
| Content-Type | `application/json` | Set by httpx automatically |

### Endpoint Specifications

#### 9.1 `POST /api/v1/ai/analyze`

**Purpose:** AI-powered patient symptom analysis. Creates a new triage session.

**Request:**

```json
{
    "patient_id": "P-1043",
    "session_id": "sess_xyz789",
    "symptoms": ["fever", "cough", "fatigue"],
    "duration": "2 days",
    "language": "en"
}
```

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `patient_id` | string | Yes | 3-64 chars |
| `session_id` | string | No | Auto-generated UUID if omitted |
| `symptoms` | string[] | Yes | Min 1 item, lowercased & trimmed |
| `duration` | string | No | Max 100 chars |
| `language` | string | No | ISO code, default "en" |

**Response (200):**

```json
{
    "status": "success",
    "patient_id": "P-1043",
    "session_id": "sess_xyz789",
    "analysis": {
        "severity": "yellow",
        "risk_score": 45,
        "reasoning": "Fever and cough for 2 days suggests respiratory infection. Risk elevated due to duration.",
        "follow_up_question": "Have you experienced any difficulty breathing or chest tightness?",
        "escalation_needed": false
    },
    "current_state": {
        "patient_id": "P-1043",
        "symptoms": ["fever", "cough", "fatigue"],
        "severity": "yellow",
        "risk_score": 45
    }
}
```

**Error Response (500):**

```json
{
    "detail": "AI analysis failed. Please try again."
}
```

**Frontend Usage:**

```python
response = api_client.post("/api/v1/ai/analyze", json={
    "patient_id": patient_id,
    "session_id": session_id,
    "symptoms": symptoms,
    "duration": duration
})
analysis = response["analysis"]
# Display: analysis["severity"], analysis["risk_score"], analysis["reasoning"]
```

---

#### 9.2 `POST /api/v1/patient/analyze`

**Purpose:** Initial symptom analysis with risk scoring (non-AI path).

**Request:**

```json
{
    "patient_id": "P-1043",
    "symptoms": ["fever", "cough"],
    "duration": "2 days",
    "language": "en"
}
```

**Response (200):**

```json
{
    "patient_id": "P-1043",
    "session_id": "sess_abc123",
    "severity": "medium",
    "risk_score": 45,
    "confidence": 0.82,
    "message": "Risk assessment complete. Severity: medium."
}
```

---

#### 9.3 `POST /api/v1/patient/update`

**Purpose:** Add new symptom during session. Triggers drift detection.

**Request:**

```json
{
    "patient_id": "P-1043",
    "new_symptom": "chest pain"
}
```

**Response (200):**

```json
{
    "patient_id": "P-1043",
    "new_symptom": "chest pain",
    "updated_risk_score": 85,
    "severity": "critical",
    "message": "Risk score updated. Severity escalated to critical."
}
```

**Frontend Behavior:** After receiving this response, the frontend should:
1. Update the severity badge immediately
2. Show an escalation warning banner if severity increased
3. Enable the "Generate Report" button if severity is red or critical

---

#### 9.4 `POST /api/v1/voice/transcribe`

**Purpose:** Convert uploaded audio to text using Whisper STT.

**Request:** `multipart/form-data`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `file` | File | Yes | WAV, MP3, OGG, FLAC, M4A. Max 25MB. |
| `language` | string | No | ISO code, default "en" |

**Response (200):**

```json
{
    "status": "success",
    "transcription": "I have a fever and cough for two days",
    "language": "en"
}
```

**Error Responses:**

| Status | Detail |
|--------|--------|
| 400 | Unsupported content type |
| 400 | Audio file is empty |
| 400 | Audio file too large (>25MB) |
| 400 | Not a valid audio file (magic byte check) |
| 500 | Transcription failed |
| 503 | STT engine not available (faster-whisper not installed) |

**Frontend Usage:**

```python
import httpx

with open("recording.wav", "rb") as f:
    response = httpx.post(
        f"{BACKEND_URL}/api/v1/voice/transcribe",
        files={"file": ("recording.wav", f, "audio/wav")},
        data={"language": "en"},
        headers={"Authorization": f"Bearer {token}"}
    )
text = response.json()["transcription"]
```

---

#### 9.5 `POST /api/v1/voice/respond`

**Purpose:** Convert text to speech using XTTS.

**Request:**

```json
// Query parameters
?text=Your+severity+has+increased&language=en
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `text` | string | Yes | Text to synthesize |
| `language` | string | No | ISO code, default "en" |

**Response (200):**

```json
{
    "status": "success",
    "message": "Voice response generated",
    "audio_size": 48320
}
```

**Note:** Returns metadata, not audio bytes directly. Audio delivery is planned for V1.1.

---

#### 9.6 `POST /api/v1/report/handoff`

**Purpose:** Generate doctor handoff report from triage session data.

**Request:**

```json
{
    "session_id": "sess_xyz789",
    "patient_id": "P-1043"
}
```

**Response (200):**

```json
{
    "status": "success",
    "message": "Handoff report generated and saved successfully",
    "saved_to_db": true,
    "report": "# Doctor Handoff Report\n\n## Patient: P-1043\n..."
}
```

**Frontend Usage:**

```python
response = api_client.post("/api/v1/report/handoff", json={
    "session_id": session_id,
    "patient_id": patient_id
})
report_markdown = response["report"]
# Display in st.markdown() or convert to PDF
```

---

#### 9.7 `GET /api/v1/system/status`

**Purpose:** System health check (public, no auth required).

**Response (200):**

```json
{
    "status": "healthy",
    "version": "0.1.0",
    "environment": "development",
    "database": "connected",
    "ai_model": "gemini-1.5-flash"
}
```

**Frontend Usage:** Sidebar polls this to show "Backend: Connected" status.

---

#### 9.8 `GET /api/v1/system/uptime`

**Purpose:** Server uptime in seconds (public, no auth required).

**Response (200):**

```json
{
    "uptime_seconds": 3847,
    "uptime_human": "1h 4m 7s"
}
```

---

#### 9.9 `GET /health`

**Purpose:** Simple health check for load balancers and Render health probes.

**Response (200):**

```json
{
    "status": "ok"
}
```

---

## 10. API & Integration Spec — Supabase

The frontend does NOT call Supabase directly. All database operations go through the FastAPI backend. Supabase is accessed server-side only.

### Client Configuration

| Client | Key | Usage |
|--------|-----|-------|
| Anon client | `SUPABASE_ANON_KEY` | Read-only queries (respects RLS) |
| Admin client | `SUPABASE_SERVICE_ROLE_KEY` | Writes (bypasses RLS). Server-side only. |

### Operations Used by Backend

| Operation | Table | Client | Endpoint |
|-----------|-------|--------|----------|
| INSERT session | `sessions` | Admin | `POST /api/v1/patient/analyze` |
| UPDATE session | `sessions` | Admin | `POST /api/v1/patient/update` |
| INSERT symptom | `symptom_records` | Admin | `POST /api/v1/patient/analyze` |
| INSERT escalation | `escalations` | Admin | `POST /api/v1/patient/update` (when drift detected) |
| SELECT sessions | `sessions` | Admin | Dashboard queries |
| SELECT escalations | `escalations` | Admin | Emergency Center |
| INSERT report | `reports` | Admin | `POST /api/v1/report/handoff` |
| SELECT hospital_load | `hospital_load` | Admin | Dashboard load balancing |

### Supabase Auth (Planned — Not Yet Implemented)

| Flow | Supabase API | Current State |
|------|-------------|---------------|
| Sign up | `supabase.auth.sign_up()` | Placeholder (shared token) |
| Sign in | `supabase.auth.sign_in_with_password()` | Placeholder |
| Get session | `supabase.auth.get_session()` | Not implemented |
| Refresh token | `supabase.auth.refresh_session()` | Not implemented |
| Sign out | `supabase.auth.sign_out()` | Not implemented |

---

## 11. API & Integration Spec — Google Gemini

Gemini is called server-side by the backend's AI engine. The frontend never calls Gemini directly.

### Configuration

| Setting | Value | Source |
|---------|-------|--------|
| API Key | `GEMINI_API_KEY` | Environment variable |
| Model | `gemini-1.5-flash` | `GEMINI_MODEL` env var |
| Max Tokens | 1024 | `LLM_MAX_TOKENS` env var |
| Temperature | 0.3 | `LLM_TEMPERATURE` env var (low for medical determinism) |
| Timeout | 30s | `LLM_TIMEOUT_SECONDS` env var |
| SDK | `google-genai>=1.10.0` | `requirements.txt` |

### Backend Calls to Gemini

| Use Case | When | Input | Expected Output |
|----------|------|-------|-----------------|
| **Triage Analysis** | `POST /api/v1/ai/analyze` | PatientState JSON (max 200 tokens) | Severity, risk_score, reasoning, follow_up_question |
| **Differential Reasoning** | `POST /api/v1/ai/reason` | PatientState + symptom history | Differential analysis, confidence, recommended tests |
| **Report Generation** | `POST /api/v1/report/handoff` | PatientState + session summary | Markdown handoff report |
| **Memory Summarization** | After 15 turns | Full symptom history | Condensed summary (< 100 tokens) |
| **Adaptive Questioning** | During triage | PatientState + conversation context | Next best question to ask |

### Prompt Construction Pattern

```
System Prompt (triage role instructions)
    +
Patient State (JSON, max 200 tokens)
    +
Conversation Summary (rolling, max 100 tokens)
    +
User Message (current patient input)
    =
Complete Prompt → Gemini API
```

**Token Budget:** Maximum 800 tokens per LLM call (defined in `MAX_CONTEXT_TOKENS`).

### Error Handling

| Error | Backend Behavior | Frontend Impact |
|-------|-----------------|-----------------|
| Gemini API timeout | Retry once, then fall back to rule-based scoring | Triage still works, just no AI reasoning |
| Gemini rate limit (429) | Queue and retry with exponential backoff | Slight delay, then response |
| Gemini unavailable | Fall back to GPT-4o-mini | No visible change to user |
| Both LLMs down | Rule-based scoring only | Reduced reasoning quality, but triage still functions |

---

## 12. API & Integration Spec — Voice Pipeline

Voice processing runs server-side. The frontend sends audio bytes and receives text (or vice versa).

### Speech-to-Text (Faster Whisper)

| Setting | Value | Source |
|---------|-------|--------|
| Model Size | `base` | `WHISPER_MODEL_SIZE` env var |
| Device | `cpu` | `WHISPER_DEVICE` env var |
| Compute Type | `int8` | `WHISPER_COMPUTE_TYPE` env var |
| Supported Formats | WAV, MP3, OGG, FLAC, M4A | Enforced via magic byte validation |
| Max File Size | 25 MB | `MAX_AUDIO_BYTES` constant |
| Expected Latency | 2-5 seconds | On CPU with `base` model |

**Frontend Audio Recording:**

```javascript
// Browser MediaRecorder API
const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
const recorder = new MediaRecorder(stream);
const chunks = [];

recorder.ondataavailable = (e) => chunks.push(e.data);
recorder.onstop = () => {
    const blob = new Blob(chunks, { type: "audio/wav" });
    // Send to /api/v1/voice/transcribe
};
```

### Text-to-Speech (XTTS-v2)

| Setting | Value | Source |
|---------|-------|--------|
| Engine | XTTS-v2 | `TTS_ENGINE` env var |
| Fallback | Piper | Automatic if XTTS unavailable |
| Expected Latency | 3-8 seconds | On CPU |
| Output Format | WAV audio bytes | — |

**Note:** TTS response currently returns metadata only (`audio_size`). Full audio delivery (streaming WAV back to frontend) is planned for V1.1.

---

## 13. API & Integration Spec — Agora (Video)

Agora SDK integration is **placeholder only** in V1. The architecture is ready but no real video calls are implemented.

### Configuration

| Setting | Value | Source |
|---------|-------|--------|
| App ID | `AGORA_APP_ID` | Environment variable |
| Certificate | `AGORA_APP_CERTIFICATE` | Environment variable |
| Token Expiry | 3600 seconds | `AGORA_TOKEN_EXPIRY_SECONDS` env var |

### Planned Integration (V1.1)

| Component | Agora API | Purpose |
|-----------|-----------|---------|
| Token Generation | Server-side REST API | Generate temporary tokens for patients and doctors |
| Join Channel | `client.join(channel, token, uid)` | Patient and doctor join same video channel |
| Publish/Subscribe | `client.publish([localAudioTrack, localVideoTrack])` | Enable audio/video |
| Leave Channel | `client.leave()` | End consultation |
| Screen Sharing | `localScreenTrack` | Share test results during consultation |

### Channel Naming Convention

```
aegiscare-{session_id_short}
// Example: aegiscare-sess_xyz789
```

Channel name is stored in `appointments.agora_channel` when a video appointment is created.

---

## 14. API & Integration Spec — OpenAI (Fallback)

OpenAI is a **fallback only** — used when Gemini is unavailable.

### Configuration

| Setting | Value | Source |
|---------|-------|--------|
| API Key | `OPENAI_API_KEY` | Environment variable (optional) |
| Model | `gpt-4o-mini` | `OPENAI_MODEL` env var |
| Temperature | 0.3 | Same as Gemini |
| Max Tokens | 1024 | Same as Gemini |

### When OpenAI Is Used

| Scenario | Trigger |
|----------|---------|
| Gemini API returns 500 | Automatic failover |
| Gemini API times out (>30s) | After one retry |
| Gemini API rate limited (429) | After backoff exhaustion |
| `PRIMARY_LLM=openai` | Explicit configuration |

### Prompt Parity

The same prompts used for Gemini are sent to OpenAI. The prompt construction is model-agnostic — only the SDK client changes.

---

## 15. Environment Variables Reference

### Frontend-Specific Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BACKEND_URL` | Yes | `http://localhost:8000` | Backend API base URL |
| `AEGISCARE_TOKEN` | Yes | `dev-token` | Bearer token for API auth |

### Variables Shared with Backend (set in same `.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SUPABASE_URL` | Yes | — | Supabase project URL |
| `SUPABASE_ANON_KEY` | Yes | — | Supabase public key |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | — | Supabase admin key (server only) |
| `GEMINI_API_KEY` | Yes | — | Google Gemini API key |
| `OPENAI_API_KEY` | No | — | OpenAI key (fallback only) |
| `AGORA_APP_ID` | No | — | Agora video SDK (V1.1) |
| `AGORA_APP_CERTIFICATE` | No | — | Agora video SDK (V1.1) |

---

*This document defines the complete frontend specification for AegisCare. Update as the design evolves. Last updated: August 21, 2026.*
