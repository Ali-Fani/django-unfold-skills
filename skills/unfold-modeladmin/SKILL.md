---
name: unfold-modeladmin
description: Deep guide to unfold.admin.ModelAdmin — @display badges/headers, actions routing, sections (expandable rows), datasets (changelists inside changeform), sortable changelist, queryset optimization (select_related/prefetch/annotate, no N+1). Use when building or customizing a model's changelist/changeform, adding badges or computed columns, when the admin makes too many queries, or when deciding what logic belongs in ModelAdmin vs a service layer.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/configuration/modeladmin/, /docs/decorators/display/, /docs/configuration/sections/, /docs/configuration/datasets/, /docs/configuration/sortable-changelist/
# Dependencies: unfold-core. Related: unfold-actions, unfold-filters, unfold-tabs, unfold-performance, unfold-production.

# Unfold ModelAdmin

## Purpose

Build efficient, correct changelist/changeform experiences on `unfold.admin.ModelAdmin`. Covers Unfold-specific attributes plus the Django foundations Unfold restyles, and the performance rules that keep admins fast.

## Decision rules

- Every admin class inherits `unfold.admin.ModelAdmin` (not `django.contrib.admin.ModelAdmin`) — otherwise page renders unstyled. Mix with third-party bases as `class X(BaseXAdmin, ModelAdmin)`.
- Column value from model field → `list_display` field name. Value computed in Python → `@display` method. Value computable in SQL → `annotate` + `@display(ordering=...)` (preferred — no per-row queries).
- Status-like column (enum with few values) → `@display(label={VALUE: "variant"})`.
- Row heading with subtitle/initials/image → `@display(header=True)`.
- Multiple related rows per changelist row → `list_sections` (expandable) — NOT nested admin hacks.
- Secondary changelist embedded in changeform → `change_form_datasets` (BaseDataset), not iframes/links.
- Drag-reorder changelist → `ordering_field` (needs PositiveIntegerField with `db_index=True`).

## Base template

```python
from django.contrib import admin
from unfold.admin import ModelAdmin

@admin.register(MyModel)
class MyModelAdmin(ModelAdmin):
    list_display = ["name", "status", "owner"]
    search_fields = ["name"]            # [DJANGO]
    list_filter = ["status"]            # [DJANGO]
    ordering = ["-created_at"]           # [DJANGO]
    list_per_page = 25                   # [DJANGO]
    readonly_fields = ["created_at"]     # [DJANGO]
```

## Unfold-specific ModelAdmin attributes [UNFOLD]

```python
class MyModelAdmin(ModelAdmin):
    show_add_link = True                   # add link on changelist/changeform (default True)
    warn_unsaved_form = True               # warn on leaving unsaved changeform
    list_fullwidth = False                 # fullwidth changelist
    list_filter_sheet = True               # True: filter as sheet; False: sidebar
    list_filter_submit = True              # submit button under input filters (REQUIRED for text/numeric/date filters)
    list_disable_select_all = False        # hide "select all"
    list_filter_options = {                # per-filter tweaks
        "status": {"label": "Status", "horizontal": True},
    }
    readonly_preprocess_fields = {         # transform readonly render output
        "description": lambda c: c.strip(),
    }
    change_form_before_template = "app/pre.html"       # inside form
    change_form_after_template = "app/post.html"
    change_form_outer_before_template = "app/opre.html"  # outside form
    change_form_outer_after_template = "app/opost.html"
    change_form_show_cancel_button = True
```

`actions_list`, `actions_row`, `actions_detail`, `actions_submit_line` → `unfold-actions`.

## @display decorator [UNFOLD]

```python
from unfold.decorators import display

class Status(TextChoices):
    ACTIVE = "ACTIVE", "Active"
    PENDING = "PENDING", "Pending"

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ["heading", "status_badge"]

    @display(description="Status", ordering="status", label={
        Status.ACTIVE: "success",   # green
        Status.PENDING: "info",     # blue
    })
    def status_badge(self, obj):
        return obj.status                          # colored badge

    @display(description="Status", ordering="status", label=True)
    def status_two_line(self, obj):
        return obj.status, obj.get_status_display()  # badge + text

    @display(header=True)
    def heading(self, obj):
        return [
            obj.full_name,                 # main line
            obj.email,                     # secondary line (None to skip)
            "AB",                          # initials circle
            {"path": obj.avatar, "squared": True, "borderless": False,
             "width": 64, "height": 48},   # optional image dict; replaces initials
        ]
```

Variants: `success, info, warning, danger` (plus `primary`/`default` where noted in badge contexts).
`ordering="field"` makes column sortable via underlying field — pair with annotation when field is computed.

## Sections (expandable changelist rows) [UNFOLD]

Row expands to show related data without leaving the list:

```python
from unfold.sections import TableSection, TemplateSection

class OrdersSection(TableSection):
    verbose_name = "Orders"
    height = 300                          # optional fixed height + scroll
    related_name = "orders"                # reverse relation on listed model
    fields = ["pk", "title", "amount"]     # related model fields

    def amount(self, instance):           # custom field on related instance
        return f"${instance.amount}"

class NotesSection(TemplateSection):
    template_name = "app/row_notes.html"   # custom content per listed row

class CustomerAdmin(ModelAdmin):
    list_sections = [OrdersSection, NotesSection]
```

Use when: users constantly click through to child records. Avoid for huge child sets (each row renders its section; paginate via `height`).

## Datasets (changelists inside changeform) [UNFOLD]

```python
from unfold.datasets import BaseDataset

class OrderDatasetAdmin(ModelAdmin):
    search_fields = ["number"]
    list_display = ["number", "amount"]
    list_per_page = 20
    # NOTE: list_filter is NOT supported on dataset admins (documented limitation)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        obj = self.extra_context.get("object") if self.extra_context else None
        if not obj:
            return qs.none()               # add view → empty dataset
        return qs.filter(customer__pk=obj.pk)

class OrderDataset(BaseDataset):
    model = Order
    model_admin = OrderDatasetAdmin
    tab = True                             # render dataset as a changeform tab

class CustomerAdmin(ModelAdmin):
    change_form_datasets = [OrderDataset]
```

Use when: related model already has its own admin-worthy list UX. Remember `list_filter` unsupported.

## Sortable changelist [UNFOLD]

Model needs: `ordering = models.PositiveIntegerField(db_index=True)` (+ include in `Meta.ordering`).

```python
class SortableAdmin(ModelAdmin):
    ordering_field = "ordering"
    hide_ordering_field = True   # hide the raw field column
```

## Custom views on ModelAdmin [DJANGO+UNFOLD]

```python
class MyModelAdmin(ModelAdmin):
    def get_urls(self):
        return super().get_urls() + [
            path("report/", self.admin_site.admin_view(ReportView.as_view(model_admin=self)),
                 name="mymodel_report"),
        ]
```

Full treatment (mixin, permissions, forms) in `unfold-custom-pages`.

## Queryset & performance rules

The single most common admin bug: N+1 from `list_display` methods hitting related objects.

```python
# BAD — one query per row
def order_customer(self, obj):
    return obj.customer.name

# GOOD — join
def get_queryset(self, request):
    return super().get_queryset(request).select_related("customer")

# GOOD (M2M/many) — prefetch
def get_queryset(self, request):
    return super().get_queryset(request).prefetch_related("tags")

# BEST for aggregates — annotate once
def get_queryset(self, request):
    return super().get_queryset(request).annotate(
        order_count=Count("orders", distinct=True),
    )

@display(description="Orders", ordering="order_count")
def order_count(self, obj):
    return obj.order_count        # no query — from annotation
```

- `@display(ordering="x")` enables sorting; on annotated names sort uses SQL annotation (cheap). Sorting on a Python-computed method without ordering attr is not possible — annotate instead.
- Search: `search_fields` uses `__icontains` (or `=exact`/`^startswith` prefixes) — on large tables add DB indexes or trigram search; `autocomplete_fields` (FK dropdown via search) requires target admin define `search_fields`.
- Huge table: `paginator = InfinitePaginator`, `show_full_result_count = False` (skips expensive COUNT). See `unfold-performance`.
- Display methods that call external APIs: never — render would block on N calls; move to dashboard with caching or background refresh.

## Where logic lives

| Logic | Location |
|---|---|
| Column formatting, badge mapping | ModelAdmin `@display` |
| Row-count aggregates | queryset annotation in `get_queryset` |
| Complex reporting queries | dedicated queryset/service functions, admin calls them |
| Mutations (bulk state change etc.) | service layer called from actions (`unfold-production`) |
| Permission per object | `has_*_permission` overrides [DJANGO] |

## Anti-patterns

- Inheriting `admin.ModelAdmin` → unstyled pages.
- `@display` methods triggering queries per row without `select_related`/`prefetch_related`/annotation.
- Giant ModelAdmin with every feature — split config per model, push logic to services.
- `list_filter` on dataset admin — unsupported, silently breaks.
- `warn_unsaved_form` with heavy custom JS conflicting — test before enabling globally.
- Business mutations inline in `save_model`/actions — hard to test, no reuse; call services instead.

## Security

- `get_queryset` is a **data boundary**: always filter through `super().get_queryset(request)` (keeps any default scoping), and scope by `request.user` where object-level isolation needed.
- `readonly_fields` for fields staff may see but not edit; but remember readonly data still renders — don't expose secrets (API keys, tokens) in `list_display`/`readonly_fields`/fieldsets for broad-staff admins.
- Custom `has_module_permission`/`has_*_permission` overrides: fail closed (default False on error paths).

## Testing

```python
def test_changelist_single_query(admin_client, django_assert_num_queries):
    Order.objects.create(customer=customer, name="x" * 100)
    for i in range(25):
        Order.objects.create(customer=customer, name=f"o{i}")
    with django_assert_num_queries(10):   # assert a sane ceiling; tune per setup
        admin_client.get("/admin/shop/order/")
```

Also test: badge output contains expected variant class; sortable ordering persists after drag (POST); dataset returns rows only for the parent object.

## Related skills

`unfold-actions`, `unfold-filters`, `unfold-tabs`, `unfold-performance` (deep dive), `unfold-production` (service layer), `unfold-custom-pages`.
