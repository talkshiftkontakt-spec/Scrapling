# Us — illustrated screen pack

Generated full-screen mockups + transparent layers for the couples app preview.

## Folders

- `screens/paper-ink/` — Splash, Our Day, Plan, Together, Wellbeing, Memories
- `screens/sunday-morning/` — Our Day, Plan, Together, Wellbeing, Memories
- `layers/` — transparent PNGs (sun, clouds, hills, hearts, stars, plane, illustrations)

## Usage in Antigravity / intelligent-bell

1. Drop `screens/` into your design or `public/` folder as visual source-of-truth.
2. Use each full PNG as the layout target for that tab (color, typography, illustration mood).
3. Use `layers/` when you want motion (float sun, drift clouds) without redrawing the whole UI in code.

## Preview

In `apps/us-preview`: `npm run dev` → http://localhost:3200

- Theme toggle: Paper & Ink / Sunday Morning
- Screen pills + clickable bottom-nav hotspots
- “Warstwy live” shows animated transparent layers
