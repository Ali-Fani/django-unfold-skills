---
name: unfold-core
description: Establishes the Unfold mental model — Unfold is a restyling/enhancement layer over django.contrib.admin, not a replacement — with layering rules ([DJANGO] vs [UNFOLD] vs [CUSTOM] vs [STUDIO]) and a routing table for every admin customization need. Use when starting ANY Django Unfold task, when deciding which mechanism fits a requirement, or when unsure whether a feature is Django, Unfold, or custom.
---
# Verified against: django-unfold 0.104.1
# Docs: https://unfoldadmin.com/docs/ , https://github.com/unfoldadmin/django-unfold
# Dependencies: none. Related: unfold-installation, unfold-modeladmin, unfold-settings, unfold-navigation.

# Unfold Core — Mental Model & Routing

## Purpose

Establish the correct mental model for Unfold work: Unfold is a **restyling and enhancement layer on top of `django.contrib.admin`**, not a replacement. Nearly everything Unfold does is Django admin with new templates (Tailwind), a settings dictionary, and extra opt-in features (actions, filters, tabs, components, command palette).

An agent that internalizes the layering rules below will not misattribute features, fight Django mechanics, or invent configuration.

## Layering rules

Every capability belongs to exactly one layer:

| Layer | What it covers | Examples |
|---|---|---|
| `[DJANGO]` | Standard admin machinery — Unfold only changes appearance | `list_display`, `search_fields`, `fieldsets`, `inlines`, `get_queryset()`, `has_*_permission`, actions dropdown, `autocomplete_fields`, `raw_id_fields`, list pagination |
| `[UNFOLD]` | Official Unfold additions — settings dict, contrib apps, decorators, components, mixins | `UNFOLD = {...}`, `unfold.admin.ModelAdmin`, `@display`, `@action`, `unfold.contrib.filters`, `UnfoldModelAdminViewMixin`, `BaseComponent`, `InfinitePaginator`, `actions_list/row/detail/submit_line`, tabs, command palette |
| `[CUSTOM]` | Project-level code the agent writes | `templates/admin/index.html` override, Tailwind build, custom views with forms, service/queryset layers, custom components |
| `[STUDIO]` | Paid Unfold Studio plugin capabilities | boxed layout, sticky header, minimal sidebar, forced dark sidebar, banner, nested navigation, dashboard templates. See `unfold-studio` skill for public-API equivalents. |

Rule: attribute a feature to the **lowest layer that provides it**. If plain Django does it, recommend plain Django.

## Routing table (which mechanism for which need)

| User wants | Mechanism | Skill |
|---|---|---|
| CRUD for a model | `ModelAdmin` (Django) | unfold-modeladmin |
| Bulk operation on selected rows | `actions` (Django dropdown) or Unfold `actions_list` | unfold-actions |
| Operation on one row from the list | `actions_row` | unfold-actions |
| Operation on one object from its detail page | `actions_detail` | unfold-actions |
| Extra save-mode button on changeform | `actions_submit_line` | unfold-actions |
| Confirmation dialog before an action | `@action(dialog={...})` | unfold-actions |
| Filter/side panel on changelist | `list_filter` (+ Unfold filter classes) | unfold-filters |
| Search box on changelist | `search_fields` (Django) | unfold-modeladmin |
| Global brand/title/logo | `UNFOLD` settings | unfold-settings |
| Sidebar menu with icons/badges | `UNFOLD["SIDEBAR"]` | unfold-navigation |
| Extra tabs above changelist/changeform | `UNFOLD["TABS"]` | unfold-tabs |
| Tabs *inside* the changeform form | fieldsets `"tab"` class, inline `tab = True` | unfold-tabs |
| Non-CRUD page (analytics, wizard) | custom admin view (`UnfoldModelAdminViewMixin`) | unfold-custom-pages |
| Admin landing page with cards/charts | `DASHBOARD_CALLBACK` + `templates/admin/index.html` override, or custom page | unfold-dashboard |
| Related objects on changeform | `inlines` (Django; Unfold base classes) | unfold-inlines |
| Changeform field grouping | `fieldsets` (Django; Unfold adds tab classes) | unfold-modeladmin, unfold-tabs |
| Compact repeatable field list | `ArrayWidget` | unfold-fields |
| Rich text editing | `WysiwygWidget` | unfold-fields |
| Visual color/theme change | `UNFOLD["COLORS"]`, `BORDER_RADIUS`, `THEME` | unfold-theming |
| Anything beyond settings visually | Tailwind/template override | unfold-tailwind |
| Huge table slow pagination | `InfinitePaginator` | unfold-performance |
| Model data in cmd+K palette | `UNFOLD["COMMAND"]` | unfold-navigation |
| Related-record tables in changelist rows (expandable) | `list_sections` with `TableSection`/`TemplateSection` | unfold-modeladmin |
| Secondary changelist on changeform | `change_form_datasets` (`BaseDataset`) | unfold-modeladmin |

**When configuration is NOT enough** (custom implementation required):

- Anything with a form + POST that isn't an action dialog → custom page (`unfold-custom-pages`).
- Dashboard richer than components → dashboard template override + Tailwind (`unfold-dashboard`).
- Visual effects not exposed as settings → Tailwind CSS or template override (`unfold-tailwind`, `unfold-studio`).
- Business logic beyond simple mutations → service layer, never ModelAdmin methods (`unfold-production`).

## Golden rules

1. Every admin class must inherit `unfold.admin.ModelAdmin` (and every inline `unfold.admin.TabularInline`/`StackedInline`) or pages render unstyled. Third-party ModelAdmins need re-registration with Unfold bases.
2. `"unfold"` goes **before `django.contrib.admin`** in `INSTALLED_APPS`. Contrib apps (`unfold.contrib.filters`, `unfold.contrib.forms`, `unfold.contrib.inlines`) go immediately after.
3. Unfold does not replace admin URLs, templates path (`admin/base_site.html` extends work), or Django's permission machinery — extend, don't fight.
4. Never hardcode Unfold internals (template names beyond documented components, private template tags); use documented settings/classes only.
5. Business logic does not live in ModelAdmin. ModelAdmin is an HTTP/permissions layer over a service layer. See `unfold-production`.
6. Unfold changes fast; anything behaving unexpectedly → check `docs/version-notes.md` and current docs before debugging deeper.

## Version facts (verified)

- Current PyPI release: `0.104.1` (this suite verified against it).
- Requires Python ≥3.12, Django ≥5.2 (`requires_dist: django>=5.2`).
- Tailwind v4 since 0.56.0 (broke v3 custom stylesheets).
- Unfold works alongside default admin; incremental adoption OK.

## Related skills

Load `unfold-installation` for setup tasks; everything else routes from the table above.
