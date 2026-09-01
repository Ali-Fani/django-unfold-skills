---
name: unfold-filters
description: Covers all unfold.contrib.filters classes (dropdown, choices, related, autocomplete, date/datetime range, numeric range/slider, text, radio/checkbox, horizontal layout) and when to use Django built-ins vs Unfold filters vs custom filter subclasses. Use when adding filters to a changelist, when filters need input fields or ranges, when a filter shows custom logic, or when filters perform badly on large tables.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/filters/introduction/ + text, datetime, dropdown, numeric, autocomplete, checkbox-radio, horizontal
# Dependencies: unfold-core, unfold-installation. Related: unfold-modeladmin, unfold-performance.

# Filters

## Purpose

Choose correct filtering mechanism: Django built-ins vs `unfold.contrib.filters` classes vs fully custom. All Unfold filter classes live in `unfold.contrib.filters.admin`.

## Decision rules

| Need | Use |
|---|---|
| Boolean/FK/choices/date hierarchy, few values | Django built-in `list_filter` (AllValuesFieldListFilter etc.) — Unfold restyles it |
| Choices with compact UI | `ChoicesDropdownFilter` / `MultipleChoicesDropdownFilter` |
| FK with many rows | `RelatedDropdownFilter` / `MultipleRelatedDropdownFilter`, or `AutocompleteSelectFilter(Multiple)` when huge |
| Date range (from–to) | `RangeDateFilter` |
| Datetime range | `RangeDateTimeFilter` |
| Single number threshold | `SingleNumericFilter` |
| Number range inputs | `RangeNumericFilter` |
| Number range slider | `SliderNumericFilter` |
| Range over **annotated** count/aggregate | custom `RangeNumericListFilter` subclass with `parameter_name`/`title` |
| Free-text filter on a column | `FieldTextFilter` (model field) / `TextFilter` subclass (custom logic) |
| Checkbox list / radio list of custom options | `CheckboxFilter`(multiple) / `RadioFilter` subclass |
| Horizontal chip layout for choices | subclass Django's `ChoicesFieldListFilter` with `horizontal = True`, or per-field via `list_filter_options` |
| Filter logic no class covers | subclass `TextFilter`/`DropdownFilter` and write `queryset()` |

Rules:
- Input-based filters (text/numeric/date ranges) need `list_filter_submit = True` on the ModelAdmin so users can submit values.
- Custom list filters not restricted to a model field need `title` + `parameter_name` + `lookups()` + `queryset()` override.
- `list_filter_options` tweaks label/horizontal per field path without subclassing.

## Setup

```python
INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",   # immediately after "unfold"
    ...
]
```

## Filter class examples [UNFOLD]

```python
from django.contrib import admin
from django.core.validators import EMPTY_VALUES
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter, AutocompleteSelectMultipleFilter,
    ChoicesDropdownFilter, MultipleChoicesDropdownFilter,
    DropdownFilter, MultipleDropdownFilter,
    RangeDateFilter, RangeDateTimeFilter,
    RangeNumericFilter, SingleNumericFilter, SliderNumericFilter,
    RangeNumericListFilter,
    TextFilter, FieldTextFilter,
    RadioFilter, CheckboxFilter,
)

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_filter_submit = True
    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("product", MultipleRelatedDropdownFilter),
        ("customer", AutocompleteSelectFilter),          # customer admin needs search_fields
        ("tags", AutocompleteSelectMultipleFilter),
        ("placed_at", RangeDateTimeFilter),
        ("total", RangeNumericFilter),
        ("total_gt", SingleNumericFilter),
        ("amount", SliderNumericFilter),
        ("number", FieldTextFilter),
        CustomStatusFilter,
    )
    list_filter_options = {
        "status": {"label": _("Status"), "horizontal": True},
    }
```

### Custom text filter

```python
class CustomStatusFilter(TextFilter):
    title = _("Custom filter")
    parameter_name = "status_custom"     # URL query param

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            return queryset.filter(status=self.value())
        return queryset
```

### Custom radio filter

```python
class OrderStateFilter(RadioFilter):
    title = _("Order state")
    parameter_name = "state"

    def lookups(self, request, model_admin):
        return [["open", _("Open")], ["closed", _("Closed")]]

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            return queryset.filter(state=self.value())
        return queryset
```

### Range over annotated count

```python
class ProductCountFilter(RangeNumericListFilter):
    parameter_name = "items_count"
    title = _("Items")

@admin.register(User)
class MerchantAdmin(ModelAdmin):
    list_filter = (ProductCountFilter,)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            items_count=Count("product", distinct=True)
        )
```

### Autocomplete filters

```python
list_filter = (
    ["customer", AutocompleteSelectFilter],
    ["tags", AutocompleteSelectMultipleFilter],
)
```

`CustomerAdmin` must define `search_fields` (used by autocomplete search).

### Custom dropdown

```python
class RegionFilter(DropdownFilter):
    title = _("Region")
    parameter_name = "region"

    def lookups(self, request, model_admin):
        return [[r.slug, r.name] for r in Region.objects.all()]

    def queryset(self, request, queryset):
        if self.value() not in EMPTY_VALUES:
            return queryset.filter(region__slug=self.value())
        return queryset
```

## Performance

- `AllValuesFieldListFilter`-style filters issue DISTINCT value queries → avoid on million-row tables; use dropdown/autocomplete variants which search instead of enumerate.
- Autocomplete filters hit `search_fields` — index those columns.
- Range filters cause scans across ranges: ensure B-tree indexes on filtered fields.
- Custom `queryset()` must return a **new** queryset (`queryset.filter(...)`) — mutating in place breaks pagination counts.
- Annotated filters (like ProductCountFilter) force aggregation on every changelist load — acceptable, but keep the annotation in `get_queryset` (already needed for display ordering).

## UX guidance

- ≤3 filters: sheet layout (`list_filter_sheet=True` default) fine.
- Many filters: set `list_filter_sheet = False` for persistent sidebar.
- Horizontal layout for small choice sets (≤6) via `list_filter_options` — reduces vertical scroll.
- Never mix text input filter with autocomplete filter for same concept — pick one canonical path per field.

## Anti-patterns

- Forgetting `unfold.contrib.filters` in INSTALLED_APPS → import errors.
- Custom filter missing `parameter_name` → collides or breaks pagination.
- `lookups()` returning model instances instead of `[value, label]` pairs.
- Overriding `queryset()` without EMPTY_VALUES guard → empty listing when filter unused.
- Using `MultipleDropdownFilter` on FK with 10k+ rows — use autocomplete variant.
- Slider filter on unindexed float columns — every drag triggers a ranged scan.

## Security

Filters receive `request`; if filtering by request-dependent scopes (tenants), re-check scopes inside `queryset()` — filter values arrive via URL params and are **user-controlled**: never pass raw values into `extra()`/`raw()` SQL (standard injection rule).

## Testing

```python
def test_date_range_filter(admin_client):
    Order.objects.create(placed_at="2026-01-15 12:00")
    url = "/admin/shop/order/?placed_at__range__gte=2026-01-01&placed_at__range__lte=2026-01-31"
    res = admin_client.get(url)
    assert res.status_code == 200
```

## Related skills

`unfold-modeladmin` (list_filter lives there), `unfold-performance` (indexing, large tables).
