# CreatorOS Design System

This document outlines the visual direction and design system rules for CreatorOS, ensuring a consistent and premium experience inspired by high-end studio websites.

## 1. Design Tokens

The palette avoids chromatic brand colors, relying on a warm stone/near-black neutral scale.

### Palette (CSS Variables)
```css
:root {
  /* ink (dark) */
  --ink-900: #080807;   /* page background in dark theme, text in light theme */
  --ink-800: #181715;   /* raised surface / card in dark theme */
  --ink-700: #393632;   /* borders on dark, pressed states */
  --ink-600: #524d47;   /* secondary text on light */
  --ink-500: #6b645c;   /* muted text */
  --ink-400: #938f8a;   /* placeholder, disabled, meta on dark */
  
  /* paper (light) */
  --paper-100: #e8e8e3; /* text on dark; brightest paper */
  --paper-200: #ddddd5; /* editor paper surface */
  --paper-300: #d1d1c7; /* page background in light theme */
  --paper-400: #bfbfb1; /* borders on light, primary button on dark */

  /* functional signals — used ONLY for judge badges, run status, validation */
  --signal-pass: #7d9471;
  --signal-warn: #b8954f;
  --signal-fail: #a5493d;
  --signal-live: var(--paper-100);

  /* structural tokens */
  --radius-sm: 0.15rem;   /* inputs, chips, buttons */
  --radius-md: 1rem;      /* media, large panels */
  --radius-round: 100vw;  /* pills, avatar, status dots */
  --border: 0.094rem;     /* ~1.5px hairline used everywhere */
}
```

## 2. Theme Rules

We implement two main themes as section/surface classes:

- `.theme-dark`: 
  - Background: `--ink-900`
  - Text: `--paper-100`
  - Border: `--ink-700`
- `.theme-light`: 
  - Background: `--paper-300`
  - Text: `--ink-900`
  - Border: `--paper-400`

**Signature Feature:** The core app shell is `.theme-dark`, but writing surfaces (like script editors, generated posts, or captions) render as `.theme-light` (using `--paper-200`). This makes the generated work feel like a physical document on a dark desk, while the "machinery" around it stays quiet and dark.

## 3. Typography & Fonts

We use the following free variable substitutes (via `next/font`) to emulate the premium reference faces:

| Role | Font Family | Usage |
|---|---|---|
| Primary | **Schibsted Grotesk** | UI elements, body copy, and most headlines. (Weight: 500 default) |
| Display | **Anybody** | Only for the biggest moments (Landing hero, campaign completion). |
| Mono | **Geist Mono** | Micro-labels, parenthetical notes, timestamps, counters, origin chips. |

## 4. Motion Rules

- **Smooth Scrolling:** Use Lenis for smooth scroll on marketing pages *only*. In-app scrolling must remain native and instant.
- **Orchestration:** Limit to one orchestrated moment per page (e.g., hero line reveal on marketing, or cards slotting into the timeline during a campaign run).
- **Reduced Motion:** Respect `prefers-reduced-motion` by disabling Lenis, marquees, and reveal animations, jumping straight to the final state.
