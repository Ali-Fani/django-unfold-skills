---
name: unfold-theming
description: Themes Unfold via settings — COLORS primary/base 50-950 palettes (oklch or any CSS color), font tone tokens, dark mode (switcher vs forced THEME), BORDER_RADIUS, environment label pairing. Use when changing admin colors to match a brand, forcing light/dark mode, fixing contrast issues, or deciding between settings-level theming and CSS overrides.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/configuration/settings/ (COLORS), /docs/styles-scripts/customizing-tailwind/, /studio/
# Dependencies: unfold-core, unfold-settings. Related: unfold-tailwind, unfold-studio, unfold-components.

# Theming

## Purpose

Theme Unfold with settings: primary/base color palettes, font tones, dark mode, border radius, forced theme. Anything beyond these keys → `unfold-tailwind` / `unfold-studio`.

## Decision rules

- Brand primary color → `COLORS["primary"]` palette (50–950).
- Background/border tones → `COLORS["base"]` palette.
- Text contrast issues → `COLORS["font"]` tones.
- Rounded vs sharp corners → `BORDER_RADIUS`.
- Lock users into one mode → `THEME` (removes switcher).
- One-click palette from Tailwind colors → Studio feature; OSS = paste palette values manually (below).
- Layout effects (boxed, sticky header, minimal sidebar, dark sidebar, banner) → NOT settings; see `unfold-studio` for custom strategies.

## Color palettes [UNFOLD]

```python
UNFOLD = {
    "BORDER_RADIUS": "6px",
    "COLORS": {
        "base": {
            "50": "oklch(98.5% .002 247.839)",
            "100": "oklch(96.7% .003 264.542)",
            "200": "oklch(92.8% .006 264.531)",
            "300": "oklch(87.2% .01 258.338)",
            "400": "oklch(70.7% .022 261.325)",
            "500": "oklch(55.1% .027 264.364)",
            "600": "oklch(44.6% .03 256.802)",
            "700": "oklch(37.3% .034 259.733)",
            "800": "oklch(27.8% .033 256.848)",
            "900": "oklch(21% .034 264.665)",
            "950": "oklch(13% .028 261.692)",
        },
        "primary": {
            "50": "oklch(97.7% .014 308.299)",
            # ... full 50–950 ramp
            "950": "oklch(29.1% .149 302.717)",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-600)",
            "default-dark": "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark": "var(--color-base-100)",
        },
    },
}
```

- Values accept any CSS color string; docs use oklch (Tailwind v4 palette values). Source palettes: https://tailwindcss.com/docs/customizing-colors — paste 50–950 ramps.
- `primary` drives buttons, active links, accents. `base` drives surfaces/borders. Both must be full 50–950 ramps (components reference many steps).
- `font` keys map semantic text tones to palette variables — override for contrast fixes, not for new hues.

## Dark mode [UNFOLD]

- Automatic: theme switcher in header (light/dark/system), persisted per user.
- Forced: `"THEME": "dark"` or `"light"` → switcher disabled.
- Dark-specific assets: `SITE_LOGO`/`SITE_ICON` accept `{"light": fn, "dark": fn}`.
- Dark-mode-specific styling in custom CSS: `dark:` Tailwind classes (config uses `darkMode: "class"`).

## Border radius [UNFOLD]

```python
UNFOLD = {"BORDER_RADIUS": "6px"}
```

Guidance: technical/ops tools 0–4px (dense, sharp); consumer-facing SaaS 6–10px (friendly). Applies globally to components.

## Environment label [UNFOLD]

Pairs with theming for safety: colored header badge per environment — see `unfold-settings` (`ENVIRONMENT`). Use `danger` red on production.

## Applying theme in code

- Components/charts must reference theme variables: `var(--color-primary-700)`, `var(--color-base-500)` — never hex.
- Custom CSS using theme: compile Tailwind with the CSS-variable mapping (see `unfold-tailwind`), then `bg-primary-600` works and follows user palette.

## Anti-patterns

- Setting only `primary["600"]` and leaving the rest default — mismatched ramp renders half-default UI.
- Hardcoding `#7c3aed` in templates instead of `var(--color-primary-500)` — dark mode breaks.
- Using `COLORS` to make text unreadable (low contrast primary-on-base) — check WCAG AA (4.5:1 body text) in both modes.
- Forcing `THEME` per user preference (should be per deployment, not per request) — it's a global setting.
- Expecting `BORDER_RADIUS` to affect third-party package admin pages not using Unfold components.

## Performance

Color values are injected as CSS variables at render — no runtime cost. Logo/favicon lambdas per request — keep trivial.

## Security

None specific beyond not leaking environment details via labels (see `unfold-settings`).

## Testing

Visual regression: screenshot light+dark, both palettes. Programmatic:

```python
def test_theme_variables_render(admin_client):
    res = admin_client.get("/admin/")
    assert "--color-primary-600" in res.content.decode()
```

## Related skills

`unfold-settings` (parent dict), `unfold-tailwind` (compiling custom styles), `unfold-studio` (palette pickers, boxed layout etc.), `presets/` (ready-made palettes).
