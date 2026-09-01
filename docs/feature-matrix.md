# Feature Matrix

Inventory of Unfold capabilities → owning skill → implementation layer → official doc URL. Verified against django-unfold 0.104.1 docs (Sept 2026).

Layer key: **[U]** official Unfold API/setting · **[D]** Django feature restyled by Unfold · **[C]** custom project implementation · **[S]** Studio plugin capability (public equivalents in `unfold-studio`).

## Configuration

| Feature | Skill | Layer | Doc |
|---|---|---|---|
| `SITE_TITLE/SITE_HEADER/SITE_SUBHEADER/SITE_VERSION/SITE_SYMBOL/SITE_URL` | unfold-settings | U | /docs/configuration/settings/ |
| `SITE_LOGO`, `SITE_ICON` (light/dark dicts) | unfold-settings | U | /docs/configuration/settings/ |
| `SITE_FAVICONS` | unfold-settings | U | /docs/configuration/settings/ |
| `SITE_DROPDOWN` | unfold-navigation | U | /docs/configuration/site-dropdown/ |
| `SITE_VIEWS` | unfold-navigation | U | /docs/configuration/settings/ |
| `SHOW_HISTORY/SHOW_VIEW_ON_SITE/SHOW_BACK_BUTTON/SHOW_UI_WARNINGS` | unfold-settings | U | /docs/configuration/settings/ |
| `ENVIRONMENT`, `ENVIRONMENT_TITLE_PREFIX` | unfold-settings | U | /docs/configuration/settings/ |
| `THEME` (forced), `BORDER_RADIUS` | unfold-theming | U | /docs/configuration/settings/ |
| `COLORS` (primary/base/font ramps) | unfold-theming | U | /docs/configuration/settings/ |
| `STYLES`, `SCRIPTS` | unfold-tailwind | U | /docs/styles-scripts/loading-files/ |
| `LOGIN` (image/redirect/form) | unfold-settings | U | /docs/configuration/settings/ |
| `DASHBOARD_CALLBACK` | unfold-dashboard | U | /docs/configuration/dashboard/ |
| `SIDEBAR` (search, show_all_applications, navigation groups) | unfold-navigation | U | /docs/configuration/settings/ |
| `TABS` (changelist/changeform/page) | unfold-tabs | U | /docs/tabs/ |
| `COMMAND` (palette: search_models, search_callback, show_history) | unfold-navigation | U | /docs/configuration/command/ |
| Custom Tailwind build (variable mapping) | unfold-tailwind | C | /docs/styles-scripts/customizing-tailwind/ |

## ModelAdmin

| Feature | Skill | Layer | Doc |
|---|---|---|---|
| `unfold.admin.ModelAdmin` base | unfold-modeladmin | U | /docs/configuration/modeladmin/ |
| `@display(description, ordering, label, header)` | unfold-modeladmin | U | /docs/decorators/display/ |
| `actions_list/row/detail/submit_line` + `@action` | unfold-actions | U | /docs/actions/* |
| `actions_list_hide_default`, `actions_detail_hide_default` | unfold-actions | U | /docs/actions/introduction/ |
| Dialog actions + `BaseDialogForm` | unfold-actions | U | /docs/actions/dialog-actions/ |
| Action dropdown grouping | unfold-actions | U | /docs/actions/dropdown-actions/ |
| `list_filter_submit`, `list_filter_sheet`, `list_filter_options` | unfold-filters | U | /docs/filters/introduction/ |
| `list_fullwidth`, `list_disable_select_all` | unfold-modeladmin | U | /docs/configuration/modeladmin/ |
| `readonly_preprocess_fields` | unfold-modeladmin | U | /docs/configuration/modeladmin/ |
| `warn_unsaved_form` | unfold-modeladmin | U | /docs/configuration/modeladmin/ |
| `conditional_fields` | unfold-fields | U | /docs/configuration/conditional-fields/ |
| `list_sections` (TableSection/TemplateSection) | unfold-modeladmin | U | /docs/configuration/sections/ |
| `change_form_datasets` (BaseDataset) | unfold-modeladmin | U | /docs/configuration/datasets/ |
| `ordering_field` + `hide_ordering_field` (sortable changelist) | unfold-modeladmin | U | /docs/configuration/sortable-changelist/ |
| Changeform template hooks (before/after, outer) | unfold-modeladmin | U | /docs/configuration/modeladmin/ |
| `change_form_show_cancel_button` | unfold-modeladmin | U | /docs/configuration/modeladmin/ |
| Avatar (`avatar_url`, `avatar_badge_*` model properties) | unfold-navigation | U | /docs/configuration/avatar/ |
| `InfinitePaginator` + `show_full_result_count` | unfold-performance | U | /docs/configuration/paginator/ |
| Fieldsets tabs (`"tab"` class) | unfold-tabs | U | /docs/tabs/fieldsets/ |
| `list_display`, `search_fields`, `list_filter`, `fieldsets`, `get_queryset`, permissions… | unfold-modeladmin | D | Django admin docs |

## Filters (unfold.contrib.filters)

| Class | Skill | Doc |
|---|---|---|
| TextFilter, FieldTextFilter | unfold-filters | /docs/filters/text/ |
| RangeDateFilter, RangeDateTimeFilter | unfold-filters | /docs/filters/datetime/ |
| DropdownFilter, MultipleDropdownFilter, ChoicesDropdownFilter, MultipleChoicesDropdownFilter, RelatedDropdownFilter, MultipleRelatedDropdownFilter | unfold-filters | /docs/filters/dropdown/ |
| SingleNumericFilter, RangeNumericFilter, SliderNumericFilter, RangeNumericListFilter | unfold-filters | /docs/filters/numeric/ |
| AutocompleteSelectFilter, AutocompleteSelectMultipleFilter | unfold-filters | /docs/filters/autocomplete/ |
| RadioFilter, CheckboxFilter | unfold-filters | /docs/filters/checkbox-radio/ |
| Horizontal layout (ChoicesFieldListFilter subclass / list_filter_options) | unfold-filters | /docs/filters/horizontal/ |

## Inlines

| Feature | Skill | Layer | Doc |
|---|---|---|---|
| Tabular/Stacked/Generic inlines (unfold bases) | unfold-inlines | U | /docs/inlines/introduction/ |
| `show_count`, `get_count`, `get_count_variant` | unfold-inlines | U | /docs/inlines/options/ |
| Nonrelated inlines | unfold-inlines | U | /docs/inlines/nonrelated/ |
| Sortable inlines (`ordering_field`) | unfold-inlines | U | /docs/inlines/sortable/ |
| Paginated (`per_page`) | unfold-inlines | U | /docs/inlines/paginated/ |
| Nested inlines | unfold-inlines | U | /docs/inlines/nested/ |
| Inline `tab = True` | unfold-tabs | U | /docs/tabs/inline/ |

## Fields / widgets / forms

| Feature | Skill | Doc |
|---|---|---|
| ArrayWidget | unfold-fields | /docs/widgets/array/ |
| WysiwygWidget (Trix) | unfold-fields | /docs/widgets/wysiwyg/ |
| JSONField readonly display | unfold-fields | /docs/fields/json/ |
| Autocomplete form fields (BaseAutocompleteView etc.) | unfold-fields | /docs/fields/autocomplete/ |
| Crispy template pack `unfold_crispy` | unfold-fields | /docs/configuration/crispy-forms/ |
| `UnfoldAdmin*` widgets | unfold-fields | /docs/actions/action-form-example/ |

## Components

| Component | Skill | Doc |
|---|---|---|
| `BaseComponent`, `register_component` | unfold-components | /docs/components/component-class/ |
| card, table, chart (bar), link, button, progress, tracker, cohort, layer | unfold-components | /docs/components/* |

## Pages & sites

| Feature | Skill | Doc |
|---|---|---|
| Custom pages (`UnfoldModelAdminViewMixin`) | unfold-custom-pages | /docs/configuration/custom-pages/ |
| Dashboard (index override + callback) | unfold-dashboard | /docs/configuration/dashboard/ |
| Custom sites (`UnfoldAdminSite`) | unfold-installation | /docs/configuration/custom-sites/ |
| Multi-language | unfold-settings/integrations | /docs/configuration/multi-language/ |

## Integrations (official guides)

django-celery-beat, djangoql, django-money, django-constance, django-json-widget, django-waffle, django-import-export, django-simple-history, django-guardian, django-modeltranslation, django-hijack, django-location-field → `unfold-integrations` (/docs/integrations/*)

## Studio capabilities [S] — public equivalents in `unfold-studio`

primary color, base color, brand identity, predefined palettes, border radius, favicons, site symbol, default theme, sidebar style, boxed layout, sticky header, minimal sidebar, nested navigation, banner message, always dark header, forced dark sidebar, dashboard templates, live preview customizer.

## Not in public Unfold (verify before claiming)

- Per-user theme settings persistence beyond light/dark toggle.
- `list_filter` on datasets — explicitly unsupported.
- Row-action permission callbacks receiving object_id — explicitly not provided.
- Any `SIDEBAR.minimal` / layout settings keys — not in public settings docs.
