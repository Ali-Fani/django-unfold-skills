---
name: unfold-studio
description: Maps every publicly documented Unfold Studio capability (primary/base colors, branding, palettes, border radius, boxed layout, sticky header, minimal sidebar, nested navigation, banner, dark header/sidebar, dashboard templates) to a public implementation strategy classified as SUPPORTED_DIRECTLY / WITH_TEMPLATE / WITH_TAILWIND_CSS / WITH_CUSTOM_COMPONENT / NOT_DIRECTLY_SUPPORTED. Use when a request resembles a Studio feature, when evaluating buy-vs-build, or before hand-rolling layout effects that settings already cover.
---
# Verified against: django-unfold 0.104.1 + Studio public page/FAQ (capability classification high; implementation specifics medium)
# Docs: https://unfoldadmin.com/studio/ , https://unfoldadmin.com/docs/
# Dependencies: unfold-core, unfold-theming, unfold-tailwind. Related: unfold-navigation, unfold-settings, unfold-dashboard.
# IP rule: study Studio as design reference only; never reproduce proprietary code.

# Unfold Studio — Capability Mapping (no proprietary code)

## Purpose

Unfold Studio is a **paid plugin** (theme customizer). This skill maps every publicly documented Studio capability to a public implementation strategy. We study it as a design reference only — no proprietary code, templates, or internals are reproduced. Per Studio's own FAQ: it "injects additional variables into Django templates".

## Classification legend

- `SUPPORTED_DIRECTLY` — public Unfold setting/API achieves it.
- `SUPPORTED_WITH_TEMPLATE` — template override needed.
- `SUPPORTED_WITH_TAILWIND_CSS` — custom compiled CSS (see `unfold-tailwind`).
- `SUPPORTED_WITH_CUSTOM_COMPONENT` — project code needed.
- `NOT_DIRECTLY_SUPPORTED` — significant custom work; consider buying Studio instead.

## Capability map

| Studio capability (from studio page/FAQ) | Classification | Public implementation |
|---|---|---|
| Primary color change | `SUPPORTED_DIRECTLY` | `UNFOLD["COLORS"]["primary"]` full 50–950 ramp |
| Base color change | `SUPPORTED_DIRECTLY` | `UNFOLD["COLORS"]["base"]` |
| Brand identity (site title, header, logo, favicon) | `SUPPORTED_DIRECTLY` | `SITE_HEADER`, `SITE_TITLE`, `SITE_LOGO`, `SITE_FAVICONS` |
| Predefined color schemes (Tailwind palette picker) | `SUPPORTED_DIRECTLY` (manual) | Paste Tailwind palette values into `COLORS` — Studio just automates the click; outcome identical |
| Border radius | `SUPPORTED_DIRECTLY` | `UNFOLD["BORDER_RADIUS"]` |
| Default theme (light/dark) | `SUPPORTED_DIRECTLY` | `UNFOLD["THEME"]` (forced; switcher disabled) |
| Favicon upload | `SUPPORTED_DIRECTLY` (manual) | `SITE_FAVICONS` dicts + static files |
| Site symbol | `SUPPORTED_DIRECTLY` | `SITE_SYMBOL` |
| Sidebar style options | `PARTIAL` | `SIDEBAR` config (search, collapsible, badges, separators); visual variants beyond that = `SUPPORTED_WITH_TAILWIND_CSS` |
| Boxed layout (fixed content width) | `SUPPORTED_WITH_TAILWIND_CSS` | Add a compiled CSS rule capping `main` content container width + centering. Marker classes exist in templates; override `admin/base.html` blocks if needed. Keep it one CSS rule, not a fork. |
| Sticky header | `SUPPORTED_WITH_TAILWIND_CSS` | `position: sticky; top: 0` (+z-index) on the header element in compiled CSS. Verify against current DOM classes — they may change between versions; prefer `@media` guards so mobile UX unaffected. |
| Minimal sidebar (icon-only) | `NOT_DIRECTLY_SUPPORTED` | No public setting. Options: (a) buy Studio; (b) template override of sidebar with own collapsed state (Alpine.js or CSS-only hover expand) — custom project code, moderate effort; (c) simplest: reduce nav to few items — dense icon rail is a fork. |
| Nested navigation (multi-level menus) | `PARTIAL` | Collapsible groups: `SUPPORTED_DIRECTLY` (`collapsible: True`). True nested child items under items: documented as Studio feature; **public-settings support is UNCERTAIN per current docs — verify in the settings page of current docs before relying on it.** Fallback: collapsible groups (flat, 2-level UX). |
| Banner message at top of page | `SUPPORTED_WITH_CUSTOM_COMPONENT` | No public setting. Implement: override `admin/base.html` block adding a conditional banner div fed from a context processor (e.g. maintenance notice), styled with Unfold palette classes. ~20 lines. |
| Always dark header | `SUPPORTED_WITH_TAILWIND_CSS` | Compiled CSS forcing header surface + text colors in both themes (use `!` utilities or higher specificity; respect `darkMode: "class"`). |
| Force dark sidebar | `SUPPORTED_WITH_TAILWIND_CSS` | Same approach as dark header, scoped to sidebar element. Verify element selectors per version; test both themes. |
| Dashboard templates (pre-built) | `SUPPORTED_WITH_CUSTOM_COMPONENT` | Studio ships ready templates. Public equivalent: build via `unfold-dashboard` archetypes + `unfold-components` (chart/table/card) + `DASHBOARD_CALLBACK`. The Formula demo repo (github.com/unfoldadmin/formula) shows a public dashboard implementation. |
| Live-preview customizer panel | `NOT_DIRECTLY_SUPPORTED` | Product feature; irrelevant to project builds. |

## Recommendation policy

1. If capability is `SUPPORTED_DIRECTLY` → settings only; never hand-roll.
2. `SUPPORTED_WITH_TAILWIND_CSS` → small, contained CSS additions; label them `[CUSTOM]` in code so an upgrade re-checks them.
3. `SUPPORTED_WITH_CUSTOM_COMPONENT` → implement once, cleanly (banner context processor, dashboard archetypes).
4. `NOT_DIRECTLY_SUPPORTED` + business depends on it + budget exists → buying Studio is the senior-engineer move; a DIY sidebar fork is ongoing maintenance debt against an evolving Unfold DOM.

## IP rules for agents

- Never reproduce Studio source, templates, or generated variable names.
- Reimplement outcomes using documented public APIs only.
- Label all such code `[STUDIO-INSPIRED] [CUSTOM]` so future maintainers know its provenance.
- CSS selectors against Unfold DOM are **version-dependent** — pin and re-verify on upgrades (`docs/version-notes.md`).

## Anti-patterns

- Attempting to "replicate Studio" wholesale — replicate the *outcome* needed, not the product.
- Hacking Unfold internals (private template paths) for layout effects — breaks on upgrades.
- Mislabeling Studio-derived config keys as public (e.g., assuming a `SIDEBAR.minimal` key exists — it does not in public docs).

## Related skills

`unfold-theming` (colors), `unfold-tailwind` (custom CSS pipeline), `unfold-navigation` (sidebar config), `unfold-dashboard` (dashboard equivalents), `presets/` (design-system presets approximating Studio styles).
