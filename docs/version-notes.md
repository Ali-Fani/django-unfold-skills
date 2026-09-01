# Version Notes

Verified: 2026-09-02. Latest PyPI release at time of writing: **django-unfold 0.104.1**.

## Current requirements (from PyPI metadata)

- Python `>=3.12,<4.0`
- Django `>=5.2`
- JavaScript stack: Tailwind CSS v4, Alpine.js, HTMX, Chart.js, Trix, Material Symbols icons, Inter font (from official README credits).

## Known breaking changes / version-sensitive areas

| Area | Notes |
|---|---|
| Tailwind 3 → 4 | Unfold ≥0.56.0 uses Tailwind v4. Custom Tailwind 3 generated stylesheets are incompatible — the #1 FAQ "site unstyled" cause. If upgrading a legacy project: rebuild custom CSS pipeline (see `unfold-tailwind`). |
| Colors format | Current docs show oklch values for `COLORS` palettes; any CSS color string works. Full 50–950 ramps expected by components. |
| Chart options | Dataset-level `displayYAxis`, `maxTicksXLimit`, `suffixYAxis`; full override via `options` JSON — verify against installed version's component templates when building custom chart types. |
| Datasets (`change_form_datasets`) | `list_filter` not supported on dataset admin — documented limitation, stable. |
| Row action permissions | `has_changelist_row_action_permission(request)` — no object_id. Documented. |
| `SearchResult` dataclass | Official docs example shows malformed keyword syntax; construct with keyword args (`SearchResult(title=..., description=..., link=..., icon=...)`) and verify field names against installed `unfold.dataclasses`. |
| Studio nested navigation | Guaranteed in Studio; public `SIDEBAR` support for child items is UNCERTAIN — always verify current settings docs before using nested items in OSS. |
| Unfold internals | Template DOM classes and internal template paths are not public API — any CSS override targeting them must be re-verified each upgrade. |

## Changelog watch procedure (for maintainers of this suite)

1. Check https://github.com/unfoldadmin/django-unfold/releases and PyPI version.
2. Diff https://unfoldadmin.com/docs/configuration/settings/ against this suite's `unfold-settings` reference; note new/removed keys.
3. Skim formula demo (https://github.com/unfoldadmin/formula) for new canonical usage patterns.
4. Update this file + affected SKILL.md `verified_against` fields.

## Conventions in this suite

- Every skill frontmatter carries `verified_against: django-unfold 0.104.1`.
- Anything unverified is marked `UNCERTAIN — verify against current docs`.
- Examples reference only documented APIs; where a Django version bumped (e.g., `StrEnum`, `model.None` changes) prefer documented example shapes over inferred ones.
