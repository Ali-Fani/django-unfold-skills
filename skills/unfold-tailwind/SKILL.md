---
name: unfold-tailwind
description: Tailwind v4 pipeline for Unfold admins — STYLES/SCRIPTS loading, npm @tailwindcss/cli build, tailwind.config.js mapping Unfold CSS variables (bg-primary-600 etc. following the palette), darkMode class, common unstyled causes (no build, content glob, Tailwind 3 vs 4 mismatch). Use when adding custom CSS/Tailwind classes to admin pages, when custom styles don't apply, or when compiling dashboard/page styles.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/styles-scripts/loading-files/, /docs/styles-scripts/customizing-tailwind/
# Dependencies: unfold-core, unfold-installation. Related: unfold-theming, unfold-dashboard, unfold-components, unfold-debugging.

# Tailwind in Unfold

## Purpose

Add and compile custom styles for admin pages (dashboards, custom pages, template hooks). Unfold ships Tailwind v4 — projects adding classes must run their own build.

## Decision rules

- Small tweak (one rule) → plain CSS in `STYLES`, no Tailwind.
- Any custom markup using Tailwind classes (dashboard/custom page templates) → compiled stylesheet with Unfold's CSS-variable mapping, loaded via `UNFOLD["STYLES"]`.
- Admin-wide branding → `UNFOLD["COLORS"]` (see `unfold-theming`), not Tailwind overrides.

## Loading files [UNFOLD]

```python
from django.templatetags.static import static

UNFOLD = {
    "STYLES": [lambda request: static("css/admin.css")],
    "SCRIPTS": [lambda request: static("js/admin.js")],
}
```

Loaded on every admin page. Per-ModelAdmin: `styles`/`scripts` attributes (see `unfold-modeladmin`).

## Tailwind build pipeline [UNFOLD]

```bash
npm i tailwindcss @tailwindcss/cli
```

```json
// package.json
{
  "scripts": {
    "tailwind:watch": "npx tailwindcss -i styles.css -o your_project/static/css/styles.css --minify --watch",
    "tailwind:build": "npx tailwindcss -i styles.css -o your_project/static/css/styles.css --minify"
  }
}
```

```css
/* styles.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* custom: */
.my-kpi { @apply bg-primary-600 text-white rounded-md p-4; }
```

```javascript
// tailwind.config.js — map palette to Unfold's CSS variables
module.exports = {
  darkMode: "class",
  content: ["./your_project/**/*.{html,py}"],
  theme: {
    extend: {
      colors: {
        base: {
          50: "rgb(var(--color-base-50) / <alpha-value>)",
          // ... through 950 — full ramp required
        },
        primary: {
          50: "rgb(var(--color-primary-50) / <alpha-value>)",
          // ... through 950
        },
        font: {
          "subtle-light": "rgb(var(--color-font-subtle-light) / <alpha-value>)",
          "subtle-dark": "rgb(var(--color-font-subtle-dark) / <alpha-value>)",
          "default-light": "rgb(var(--color-font-default-light) / <alpha-value>)",
          "default-dark": "rgb(var(--color-font-default-dark) / <alpha-value>)",
          "important-light": "rgb(var(--color-font-important-light) / <alpha-value>)",
          "important-dark": "rgb(var(--color-font-important-dark) / <alpha-value>)",
        },
      },
    },
  },
};
```

With this, `bg-primary-600`, `text-base-500` etc. in custom templates follow the `UNFOLD["COLORS"]` palette, including dark mode (class-based).

Then in settings: `"STYLES": [lambda request: static("css/styles.css")]`.

In production run `tailwind:build` + `collectstatic` as part of deployment. In dev run the watch task while editing.

## Version notes (verified)

- **Unfold ≥0.56.0 uses Tailwind v4.** Custom Tailwind 3 stylesheets break with current Unfold — the #1 "admin unstyled" FAQ cause. If a project has a v3 config (`tailwind.config.js` with `module.exports` + `@tailwind` directives still works but verify against installed Unfold; official current docs still show this config shape — `npx tailwindcss` CLI and `@tailwind` directives).
- `darkMode: "class"` is required — dark theme is class-toggled.

## Anti-patterns

- Writing Tailwind classes in templates without a build step → classes simply don't exist in production CSS.
- Compiling with `content` paths missing template dirs → silently missing classes (Tailwind only generates classes it finds).
- Overriding Unfold's own base templates to inject styles instead of `STYLES` → upgrade fragility.
- `!important` storms against Unwind classes — prefer component props (`title_class="!py-3"` documented on card) or higher-specificity selectors.
- Forgetting `collectstatic` on deploy → styles 404.

## Performance

- `--minify` in prod (fast).
- Keep `content` scoped; whole-repo scanning slows builds.
- Ship one stylesheet; avoid per-page CSS with duplicated base utilities.

## Security

- Never inline user data into styles; sanitize any user-provided CSS (admin theme editing features) — CSS exfiltration/`url()` tricks apply.

## Debugging (see `unfold-debugging`)

Unstyled page checklist: file in STYLES? compiled? `collectstatic` run? Tailwind v3 vs v4 mismatch? `content` glob covers template?

## Related skills

`unfold-theming`, `unfold-dashboard` (custom dashboard styles), `unfold-components` (in-card classes), `unfold-debugging`.
