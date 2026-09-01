# Unfold Decision System (architecture)

Central routing: "user wants X → use mechanism Y". Optimized for agent retrieval.

## Master decision table

| # | Requirement | Mechanism | Layer | Skill | Notes / pitfalls |
|---|---|---|---|---|---|
| 1 | CRUD for a model | `ModelAdmin` | DJANGO(+unfold base) | modeladmin | Must inherit `unfold.admin.ModelAdmin` |
| 2 | List column, field value | `list_display` field name | DJANGO | modeladmin | |
| 3 | List column, computed value | `@display` method | UNFOLD | modeladmin | Annotate when sortable/aggregated |
| 4 | Status chip / badge | `@display(label={...})` | UNFOLD | modeladmin | variants: success/info/warning/danger |
| 5 | Two-line row heading + avatar | `@display(header=True)` | UNFOLD | modeladmin | |
| 6 | Column sorting on computed | annotation + `@display(ordering=...)` | CUSTOM(query)+UNFOLD | modeladmin, performance | |
| 7 | Search box | `search_fields` | DJANGO | modeladmin | index/trigram on big tables |
| 8 | Filter, simple values | `list_filter` built-ins | DJANGO | filters | |
| 9 | Filter, dropdown/autocomplete/range | `unfold.contrib.filters` classes | UNFOLD | filters | needs `list_filter_submit=True` for inputs |
| 10 | Filter, arbitrary logic | TextFilter/DropdownFilter/RadioFilter subclass | UNFOLD+CUSTOM | filters | `queryset()` + EMPTY_VALUES guard |
| 11 | Bulk operation | Django `actions` or Unfold `actions_list` | DJANGO/UNFOLD | actions | Unfold buttons + dialogs |
| 12 | Per-row operation | `actions_row` | UNFOLD | actions | permission callback has NO object_id |
| 13 | Per-object operation (detail) | `actions_detail` | UNFOLD | actions | |
| 14 | Save-variant button | `actions_submit_line` | UNFOLD | actions | runs after save |
| 15 | Confirmation before op | `@action(dialog={...})` | UNFOLD | actions | handler returns `HX-Redirect` |
| 16 | Action collecting input | `dialog={"form_class": BaseDialogForm}` | UNFOLD | actions | must inherit `BaseDialogForm` |
| 17 | Multi-field form page | custom view + `UnfoldModelAdminViewMixin` | UNFOLD+CUSTOM | custom-pages | not actions, not ModelAdmin hacks |
| 18 | Non-CRUD page (report/wizard) | custom page | CUSTOM | custom-pages | `permission_required` required |
| 19 | Admin landing analytics | dashboard override + `DASHBOARD_CALLBACK` | UNFOLD+CUSTOM | dashboard | POST filters → custom page instead |
| 20 | KPI/chart/table presentation | components (`card`, `chart/bar`, `table`...) | UNFOLD | components | colors via CSS vars |
| 21 | Multi-section form (changeform) | fieldsets `"tab"` classes | UNFOLD | tabs | titleless fieldsets don't render as tabs |
| 22 | Tabs linking related changelists | `UNFOLD["TABS"]` models | UNFOLD | tabs | `"detail": True` for changeform |
| 23 | Tabs on custom page | `TABS` `page` key + `tab_list` tag | UNFOLD | tabs | |
| 24 | Inline editing related rows | `TabularInline`/`StackedInline` (unfold) | DJANGO+UNFOLD | inlines | |
| 25 | Many inline rows | `per_page` pagination or dataset | UNFOLD | inlines, modeladmin | list_filter unsupported in datasets |
| 26 | Inline as tab | inline `tab = True` | UNFOLD | tabs, inlines | |
| 27 | Related-by-convention (no FK) inline | `NonrelatedTabularInline` | UNFOLD | inlines | needs contrib.inlines; both methods required |
| 28 | Expandable row detail | `list_sections` (Table/TemplateSection) | UNFOLD | modeladmin | |
| 29 | Drag-reorder list | `ordering_field` (+db_index field) | UNFOLD | modeladmin | |
| 30 | Global branding/title/logo | `SITE_*` settings | UNFOLD | settings | |
| 31 | Color palette/dark mode/radius | `COLORS`, `THEME`, `BORDER_RADIUS` | UNFOLD | theming | full 50–950 ramps |
| 32 | Environment badge | `ENVIRONMENT` callback | UNFOLD | settings | |
| 33 | Login page branding | `UNFOLD["LOGIN"]` | UNFOLD | settings | |
| 34 | Global CSS/JS | `STYLES`/`SCRIPTS` | UNFOLD | tailwind | |
| 35 | Custom Tailwind classes | npm build + variable mapping | CUSTOM | tailwind | v4 since 0.56.0 |
| 36 | Sidebar menu structure | `UNFOLD["SIDEBAR"]["navigation"]` | UNFOLD | navigation | badges, collapsible, separators |
| 37 | Brand links dropdown | `SITE_DROPDOWN` | UNFOLD | navigation | |
| 38 | cmd+K search | `UNFOLD["COMMAND"]` | UNFOLD | navigation | scope search_models |
| 39 | User avatar/badge in header | model properties `avatar_*` | UNFOLD | navigation | |
| 40 | Huge table pagination | `InfinitePaginator` + `show_full_result_count=False` | UNFOLD | performance | |
| 41 | Object-level permissions | `get_queryset` scoping / guardian | DJANGO | security | |
| 42 | Action permissions | `permissions=[...]` + `has_{name}_permission` | UNFOLD | actions, security | |
| 43 | Audit trail | service-layer audit writes + read-only admin | CUSTOM | production | |
| 44 | Long-running operation | background task from action/service | CUSTOM | production | never sync in handler |
| 45 | Third-party package admin | re-register + contrib app | UNFOLD | integrations | |
| 46 | Multi-admin surfaces | `UnfoldAdminSite` subclass | UNFOLD | installation | |
| 47 | Multi-language admin | LocaleMiddleware + `LANGUAGES` | DJANGO | settings(integrations) | |
| 48 | Boxed layout / sticky header / minimal sidebar / dark sidebar / banner | Studio features | STUDIO | studio | public equivalents: CSS/template — see studio skill |
| 49 | JSON display | readonly JSONField | UNFOLD | fields | Pygments optional |
| 50 | Rich text / array input | `WysiwygWidget` / `ArrayWidget` | UNFOLD | fields | needs unfold.contrib.forms |
| 51 | Conditional field visibility | `conditional_fields` (Alpine expr) | UNFOLD | fields | not validation — validate server-side |
| 52 | Crispy forms styling | `unfold_crispy` pack | UNFOLD | fields | |
| 53 | Custom admin site branding per site | multiple `UnfoldAdminSite` + per-site UNFOLD? | — | installation | UNFOLD is global; per-site customization limited — verify needs first |

## Configuration vs custom page vs template — escalation ladder

1. Does a documented setting cover it? → setting (`unfold-settings`).
2. Does a documented ModelAdmin attribute cover it? → attribute (`unfold-modeladmin`).
3. Does a documented decorator/component cover it? → use it (`unfold-actions`, `unfold-components`).
4. Does a template override of a documented pattern cover it (dashboard index, custom page)? → `unfold-custom-pages`/`unfold-dashboard`.
5. Is it purely visual beyond settings? → Tailwind/CSS (`unfold-tailwind`).
6. Otherwise → Studio feature or real custom build; evaluate buy-vs-build (`unfold-studio`).

## Skill dependency graph

```
unfold-core
├── unfold-installation ── unfold-integrations
├── unfold-settings ──┬── unfold-navigation ── unfold-custom-pages
│                     ├── unfold-theming ── unfold-studio
│                     └── unfold-tabs
├── unfold-modeladmin ──┬── unfold-actions ── unfold-production
│                       ├── unfold-filters
│                       ├── unfold-inlines
│                       └── unfold-fields
├── unfold-components ── unfold-dashboard ── unfold-performance
├── unfold-tailwind (→ theming, dashboard, studio)
├── unfold-security (→ actions, custom-pages, production)
├── unfold-testing (→ actions, filters, custom-pages)
└── unfold-debugging (→ installation, tailwind)
```

Load order for a typical task: `unfold-core` → routed skill → its `related` skills only when touching shared surfaces (e.g., actions + security; dashboard + performance).

## Anti-goals

- Do not load the whole suite per task; each SKILL.md has triggers for selective loading.
- Do not attribute Django mechanics to Unfold (rule: check the layering table in `unfold-core`).
- Do not implement Studio features by guessing keys — public equivalents only (`unfold-studio`).
