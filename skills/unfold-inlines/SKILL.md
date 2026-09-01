---
name: unfold-inlines
description: Related-object editing on changeforms — Unfold Tabular/Stacked/Generic inlines, nonrelated inlines (get_form_queryset/save_new_instance), sortable (ordering_field), paginated (per_page), nested, tabbed (tab = True), and count badges (show_count). Use when editing related rows on a parent form, when inlines render unstyled, when inline lists get too long, or when related data has no FK link.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/inlines/introduction/, options, nonrelated, sortable, paginated, nested
# Dependencies: unfold-core. Related: unfold-modeladmin, unfold-tabs, unfold-performance.

# Inlines

## Purpose

Related-object editing on the changeform: pick correct base class, and Unfold extras (tabs, counts, sorting, pagination, nesting, nonrelated).

## Decision rules

| Need | Use |
|---|---|
| FK/M2M reverse relation, edit on parent form | `TabularInline` (compact rows) or `StackedInline` (complex objects) from `unfold.admin` |
| Generic relations | `GenericTabularInline`/`GenericStackedInline` from `unfold.admin` |
| Related but not FK-linked (e.g. by email/tenant) | `NonrelatedTabularInline`/`NonrelatedStackedInline` (`unfold.contrib.inlines`) |
| Many children (50+) | `per_page = 20` pagination — or drop inline entirely, use link to changelist/dataset |
| Drag-order children | `ordering_field` on inline (+ optional `hide_ordering_field`) |
| Inline as changeform tab | `tab = True` |
| Inline header shows count badge | `show_count = True` |
| Grandchildren on changeform | nested `inlines` — one level is plenty; deeper = UX problem |

Rules:
- Inline count in DB > ~100 → inline is the wrong UX; switch to `change_form_datasets` or a filtered changelist link.
- Every inline class must inherit Unfold bases (`unfold.admin.TabularInline` etc.) or renders unstyled.
- Nonrelated inlines need `unfold.contrib.inlines` in INSTALLED_APPS.

## Base example [DJANGO base + UNFOLD styling]

```python
from unfold.admin import ModelAdmin, StackedInline, TabularInline

class OrderInline(TabularInline):
    model = Order
    fields = ["number", "total", "status"]
    extra = 0                       # [DJANGO] never ship with extra=1+

class CustomerAdmin(ModelAdmin):
    inlines = [OrderInline]
```

## Unfold-specific options [UNFOLD]

### Count badge

```python
class SomeInline(StackedInline):
    model = SomeModel
    show_count = True   # runs .count() — one extra query

    def get_count(self, request, obj):
        return f"{obj.items.filter(read=True).count()}/{obj.items.count()}"  # custom text

    def get_count_variant(self, request, obj):
        return "primary"   # danger, success, info, warning
```

### Tabbed inline

```python
class NoteInline(StackedInline):
    model = Note
    tab = True
```

### Sortable inline

```python
class StepInline(TabularInline):
    model = Step
    ordering_field = "position"          # PositiveIntegerField on model, db_index=True
    hide_ordering_field = True
```

### Paginated inline

```python
class EventInline(TabularInline):
    model = Event
    per_page = 10
```

Works for `StackedInline`, `TabularInline`, `GenericStackedInline`, `GenericTabularInline`.

### Nested inlines

```python
class SubItemInline(TabularInline):
    model = SubItem

class ItemInline(StackedInline):
    model = Item
    inlines = [SubItemInline]        # nested — use TabularInline/StackedInline freely

class ParentAdmin(ModelAdmin):
    inlines = [ItemInline]
```

### Nonrelated inline [UNFOLD]

```python
from unfold.contrib.inlines.admin import NonrelatedTabularInline

class RecentLoginsInline(NonrelatedTabularInline):
    model = LoginEvent
    fields = ["ip", "created_at"]

    def get_form_queryset(self, obj):        # REQUIRED
        return self.model.objects.filter(email=obj.email)

    def save_new_instance(self, parent, instance):   # REQUIRED (can be no-op)
        instance.user = parent

class UserAdmin(ModelAdmin):
    inlines = [RecentLoginsInline]
```

## Performance

- `show_count` = extra COUNT per inline per page load — fine for small tables, avoid for giant ones.
- Paginated inlines cap render size, not queryset fetch — queryset still evaluated lazily but rendering is bounded.
- Nonrelated `get_form_queryset` runs per changeform render; keep it a simple indexed filter.
- M2M inline on model with heavy `save()`/signals — inline rows call full model save; prefer direct FK or service-based flows when child save is expensive.

## Anti-patterns

- `extra = 3` empty rows shipped in production forms — blank-row noise; set 0.
- Stacked inline with 15 fields × 20 rows — unreadable wall; use tabs/datasets.
- Nested inline depth 3 — users get lost; restructure the model relation or page.
- Nonrelated inline where FK actually exists — just use a normal inline.
- Forgetting `get_form_queryset`/`save_new_instance` on nonrelated inlines — hard errors (both required by API).

## Security

- Inline model permissions still enforced by Django (`has_add_permission` etc. via parent), but nonrelated inlines bypass FK-based implicit scoping — filter strictly in `get_form_queryset` (e.g., `email=obj.email` above is a data boundary: leak here = cross-tenant exposure).
- Read-only "inline" for sensitive logs: add `can_delete = False` + `readonly` fields rather than trusting UI.

## Testing

```python
def test_paginated_inline(admin_client):
    parent = ParentFactory()
    for i in range(30):
        ItemFactory(parent=parent)
    res = admin_client.get(f"/admin/app/parent/{parent.pk}/change/")
    assert res.content.decode().count("row-") <= 20   # paginated
```

## Related skills

`unfold-modeladmin`, `unfold-tabs` (`tab = True`), `unfold-performance`.
