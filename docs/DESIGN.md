# Design System Documentation: Industrial Precision & Editorial Clarity

## 1. Overview & Creative North Star: "The Digital Caliper"
This design system moves beyond the "generic SaaS" aesthetic to embrace a Creative North Star we call **The Digital Caliper**. In the world of industrial gauge management, precision is everything. This system reflects that through extreme intentionality, high-contrast typography scales, and a rejection of traditional "boxed" UI.

Instead of a rigid grid of outlines, we treat the interface as a precision instrument. We utilize **Architectural Layering**—using tonal shifts and sophisticated white space to create a "nested" experience that feels high-end, authoritative, and impossibly clean. We break the "template" look by using oversized display type for data highlights and asymmetrical layouts that guide the eye to critical metrics.

---

## 2. Colors & Tonal Architecture
The palette is rooted in `primary` (#00488d), a color that signals reliability and industrial heritage. However, the sophistication lies in the neutrals and how they interact.

### The "No-Line" Rule
**Explicit Instruction:** Designers are prohibited from using 1px solid borders for sectioning or layout containment. 
Boundaries must be defined solely through background color shifts. For example, a dashboard section using `surface-container-low` should sit directly on the `background` (#f8f9fa). The eye should perceive the edge through the change in value, not a line.

### Surface Hierarchy & Nesting
Treat the UI as a series of physical layers. Use the surface-container tiers to create "nested" depth:
*   **Base:** `surface` (#f8f9fa) for the main canvas.
*   **Secondary Sections:** `surface-container-low` (#f3f4f5) for sidebars or utility panels.
*   **Priority Cards:** `surface-container-lowest` (#ffffff) to make critical gauge data "pop" against the background.

### The "Glass & Gradient" Rule
To elevate the experience, floating elements (like hover menus or active status indicators) should utilize **Glassmorphism**. Use `surface` colors at 80% opacity with a `backdrop-blur` of 12px. 
*   **Signature Texture:** For primary CTAs or high-level status cards, use a subtle linear gradient transitioning from `primary` (#00488d) to `primary_container` (#005fb8) at a 135-degree angle. This adds a "lithic" weight that flat colors lack.

---

## 3. Typography: The Editorial Scale
We use **Inter** not just for legibility, but as a structural element. By utilizing extreme size differentials, we create an "Editorial" feel that highlights critical industrial data.

*   **Display (Large/Medium):** Reserved for the "Hero" metric (e.g., a critical PSI reading). Use `on_surface` (#191c1d) with a slight negative letter-spacing (-0.02em) to feel "machined."
*   **Headline & Title:** Used for equipment names and section headers. High contrast between `headline-lg` (2rem) and `body-md` (0.875rem) is required to ensure the user never gets lost in a sea of data.
*   **Labels (Medium/Small):** These are your "unit" markers (e.g., "BAR", "°C"). Use `on_surface_variant` (#424752) in `label-md` to provide a clear secondary hierarchy that doesn't compete with the raw numbers.

---

## 4. Elevation & Depth: Tonal Layering
Traditional drop shadows are often messy. This system uses **Ambient Depth**.

*   **The Layering Principle:** Depth is achieved by stacking. Place a `surface-container-lowest` card on a `surface-container-low` section. The delta in brightness creates a soft, natural lift.
*   **Ambient Shadows:** If an element must float (like a Modal or a FAB), use an extra-diffused shadow: `box-shadow: 0 12px 32px rgba(25, 28, 29, 0.06);`. The shadow color is a tinted version of `on-surface`, never pure black.
*   **The "Ghost Border" Fallback:** If accessibility requires a container edge, use a "Ghost Border": the `outline-variant` (#c2c6d4) at **15% opacity**. Anything more is considered visual noise.

---

## 5. Components: Machined Precision

### Buttons
*   **Primary:** High-gloss. Gradient from `primary` to `primary_container`. `0.5rem` (8px) corner radius. White text (`on_primary`).
*   **Secondary:** No background, no border. Use `on_primary_fixed_variant` (#00468b) text. On hover, apply a `surface-container-high` background.
*   **Tertiary:** Used for "Danger" or "Caution" actions. Use `tertiary` (#7b3200) tones.

### Input Fields & Industrial Readouts
*   **Inputs:** Forbid the 4-sided box. Use a `surface-container-highest` (#e1e3e4) background with a 2px bottom-weighted "accent" line in `primary` only when focused.
*   **Cards & Lists:** **Strictly forbid divider lines.** Separate list items using 12px of vertical white space or by alternating background tones between `surface` and `surface-container-low`.

### Specialized Components
*   **The Gauge-Bar:** A custom horizontal progress component using `primary` for the fill and `surface-container-highest` for the track.
*   **Status Orbs:** Small, glowing indicators using `error` (#ba1a1a) or `surface_tint` (#005db5) with a subtle outer glow (4px blur) to simulate a physical LED on a control panel.

---

## 6. Do’s and Don’ts

### Do
*   **Do** use asymmetrical layouts. A heavy left-aligned headline with a wide-open right margin creates a premium, airy feel.
*   **Do** use `on_surface_variant` for all non-essential metadata to reduce cognitive load.
*   **Do** leverage `0.5rem` (8px) rounding for all containers to soften the "industrial" hardness into something approachable.

### Don't
*   **Don't** use a 1px border to separate the sidebar from the main content. Use a background color shift.
*   **Don't** use pure black (#000) for text. Use `on_surface` (#191c1d) for a softer, more sophisticated "ink" feel.
*   **Don't** crowd data. If a screen feels full, increase the spacing scale. In this system, "white space" is a functional component, not a void.