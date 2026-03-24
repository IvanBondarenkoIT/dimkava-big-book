# Design System Document: Specialty Coffee Learning Portal

> **Эталон визуала:** `experiments/stitch_lesson_view/lesson_view/code.html` — при изменении стилей сверяться с этим файлом.

## 1. Overview & Creative North Star
**The Creative North Star: "The Modern Barista’s Atelier"**
This design system moves away from the sterile, "corporate LMS" look and leans into the warmth of high-end specialty coffee culture. It treats digital learning like a curated craft. We break the rigid, boxy "template" look through **intentional asymmetry**, **tonal depth**, and **overlapping editorial layers**. 

By utilizing high-contrast typography scales and breathable layouts, the portal feels less like a chore and more like an achievement-driven lifestyle app. We use the "Stacked Paper" philosophy—where every element feels like a physical piece of artisan stationery layered on a warm marble counter.

---

## 2. Colors & Surface Philosophy
The palette is grounded in the organic tones of the coffee process: from the washed parchment of raw beans to the deep, oily sheen of a dark roast.

### The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders to section content. Boundaries must be defined solely through background color shifts or tonal transitions. To separate a sidebar from a main feed, use `surface-container-low` against a `surface` background. Lines feel clinical; color shifts feel organic.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers. Use the `surface-container` tiers to define depth:
- **Base Layer:** `surface` (#fbf9f5) for the main application background.
- **Sectioning:** `surface-container-low` (#f5f3ef) for large grouped content areas.
- **Interactive Cards:** `surface-container-lowest` (#ffffff) to provide a "pop" of clean white for primary content.
- **In-Set Details:** `surface-container-high` (#eae8e4) for recessed areas like search bars or secondary metadata containers.

### The "Glass & Gradient" Rule
To inject energy and "soul":
- **CTAs & Progress:** Use a subtle linear gradient on primary buttons, transitioning from `primary` (#8e4e14) to `primary_container` (#f4a261).
- **Floating Elements:** Use Glassmorphism for overlays and navigation bars. Apply a semi-transparent `surface` color with a `backdrop-filter: blur(20px)`. This allows the warm coffee tones to bleed through the UI, creating a tactile, high-end feel.

---

## 3. Typography
We utilize **Plus Jakarta Sans** for its contemporary, geometric, yet friendly personality. It bridges the gap between technical precision (coffee chemistry) and approachability (service).

- **Display (Display-LG/MD):** Used for "Big Wins" and gamified streak numbers. These should feel authoritative and energetic.
- **Headlines (Headline-LG/SM):** Reserved for module titles. Use a tighter letter-spacing (-0.02em) to create a sophisticated editorial look.
- **Body (Body-LG/MD):** High readability is paramount. Use `on_surface_variant` (#534439) for secondary body text to reduce eye strain against the warm cream backgrounds.
- **Labels (Label-MD):** Used for micro-copy and coffee notes. Always uppercase with slightly increased tracking (+0.05em) for a "premium tag" aesthetic.

---

## 4. Elevation & Depth
Hierarchy is achieved through **Tonal Layering** rather than structural shadows.

### The Layering Principle
Stacking is our primary tool for depth. Place a `surface-container-lowest` card on top of a `surface-container-low` section to create a soft, natural lift. This mimics the way a menu sits on a café table.

### Ambient Shadows
When a "floating" effect is required (e.g., a "Level Up" modal):
- **Blur:** Large (24px - 40px).
- **Opacity:** Ultra-low (4% - 8%).
- **Color:** Use a tinted version of `on_surface` (a deep brown-tinted shadow) rather than neutral grey. This maintains the "warmth" of the brand.

### The "Ghost Border" Fallback
If accessibility requires a border, use the **Ghost Border**: the `outline-variant` (#d8c2b5) at **15% opacity**. Never use a 100% opaque border.

---

## 5. Components

### Buttons & Interaction
- **Primary:** Rounded (`DEFAULT`: 1rem), using the Primary-to-Container gradient. These should feel like "Pressable Beans"—inviting and tactile.
- **Secondary:** Using `secondary_container` (#8cf5e4) for a refreshing teal pop. This marks "Action" vs "Learning."
- **Tertiary:** Text-only with an underline that appears on hover, utilizing `primary`.

### Achievement Cards
- **Construction:** Use `surface-container-lowest` (#ffffff) with a `DEFAULT` (1rem) corner radius.
- **Layout:** Forbid divider lines. Separate content using `3` (1rem) or `4` (1.4rem) spacing increments.
- **Imagery:** Overlap coffee-leaf patterns or bean illustrations across the card boundaries to break the grid and feel "hand-crafted."

### Progress & Gamification
- **Streak Indicators:** Use `primary_container` (#f4a261) for the active path.
- **Progress Rings:** Use a thick stroke (4px+) with rounded caps. The background track should be `surface-container-highest` (#e4e2de) to feel recessed into the "paper."

### Input Fields
- **Default State:** A soft fill of `surface-container-high` (#eae8e4) with no border.
- **Active State:** Transitions to a `surface-container-lowest` (#ffffff) fill with a 1px "Ghost Border" in `primary`.

---

## 6. Do’s and Don’ts

### Do
- **Do** use asymmetrical margins (e.g., a wider left margin for headlines) to create an editorial, boutique feel.
- **Do** use "White Space" as a functional separator. If you think you need a line, try adding `6` (2rem) of vertical space instead.
- **Do** use the `secondary` (#006a60) teal sparingly for "Moment of Delight" highlights (e.g., completing a difficult espresso module).

### Don't
- **Don't** use pure black (#000000) or pure grey. Always use the Espresso Brown (`on_surface`) or warm neutrals to maintain the specialty coffee vibe.
- **Don't** use sharp corners. Everything in this system should feel as smooth as a ceramic latte cup. Stick to the `12px-16px` (`DEFAULT`) range.
- **Don't** crowd the interface. If the screen feels busy, increase the spacing scale and remove decorative elements. Let the typography do the work.

---

## 7. Tokens Reference

| Scale | Value | Usage |
| :--- | :--- | :--- |
| **Radius-Default** | 1rem (16px) | Standard Cards & Buttons |
| **Radius-LG** | 2rem (32px) | Feature Hero Sections |
| **Spacing-3** | 1rem | Internal Card Padding |
| **Spacing-6** | 2rem | Section Gaps |
| **Shadow-Ambient** | 0 8px 32px 0 | Modals (4% Opacity `on_surface`) |