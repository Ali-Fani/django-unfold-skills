---
name: unfold-tabs
description: Disambiguates Unfold's four tab mechanisms — UNFOLD["TABS"] (changelist/changeform page tabs), fieldsets "tab" classes (in-form sections), inline tab = True, and dynamic tab_list on custom pages. Use when adding tabs anywhere in the admin, when tabs don't render as expected, or when deciding between page navigation tabs vs in-form grouping.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/tabs/changelist/, changeform, fieldsets, inline, dynamic
# Dependencies: unfold-core, unfold-settings. Related: unfold-modeladmin, unfold-inlines, unfold-custom-pages.

# Tabs

## Purpose

Four distinct tab mechanisms; picking the wrong one is the classic mistake. This skill disambiguates.

## Which tab mechanism?

| Need | Mechanism | Where defined |
|---|---|---|
| Tab bar **above the page** linking model A's changelist to model B's etc. | `UNFOLD["TABS"]` with `models` list | settings.py |
| Same tab bar but on the **changeform** of a model | `UNFOLD["TABS"]` with `"detail": True` on the model | settings.py |
| Tabs **inside the changeform** grouping fieldsets | fieldsets with `"classes": ["tab"]` | ModelAdmin |
| A single inline rendered as a tab inside changeform | inline class with `tab = True` | inline class |
| Tabs above a **custom page** | `UNFOLD["TABS"]` with `page` key + `tab_list` tag | settings + template |

Rule of thumb: navigation between pages → settings TABS. Grouping within a page → fieldsets tab classes / inline tabs.

## Changelist tabs [UNFOLD]

```python
# settings.py
UNFOLD = {
    "TABS": [
        {
            "models": ["app_label.model_name"],   # lowercase app.model
            "items": [
                {
                    "title": _("Orders"),
                    "link": reverse_lazy("admin:shop_order_changelist"),
                },
                {
                    "title": _("Customers"),
                    "link": reverse_lazy("admin:shop_customer_changelist"),
                    "permission": "shop.tab_permission_callback",
                },
            ],
        },
    ],
}

# shop/callbacks.py
def tab_permission_callback(request):
    return request.user.has_perm("shop.view_order")
```

## Changeform tabs [UNFOLD]

```python
UNFOLD = {
    "TABS": [
        {
            "models": [
                {
                    "name": "app_label.model_name",
                    "detail": True,    # required to show tabs on changeform page
                },
            ],
            "items": [
                {"title": _("Edit"), "link": reverse_lazy("admin:shop_customer_changelist")},
                {"title": _("Orders"), "link": reverse_lazy("admin:shop_order_changelist")},
            ],
        },
    ],
}
```

Use for: "orders and customers are one workspace" — tabs let staff hop between related changelists without the sidebar.

## Fieldsets tabs (inside changeform) [UNFOLD]

```python
class ProductAdmin(ModelAdmin):
    fieldsets = (
        (None, {"fields": ["name", "slug"]}),                 # always visible base
        (
            _("Pricing"),
            {"classes": ["tab"], "fields": ["price", "currency", "tax_rate"]},
        ),
        (
            _("Inventory"),
            {"classes": ["tab"], "fields": ["stock", "warehouse", "sku"]},
        ),
    )
```

Each `"tab"` class fieldset becomes a tab; the fieldset **title is the tab label** (titleless tab fieldsets won't render). First non-tab fieldset stays above tabs.

Use when: form has 15+ fields or clear domain sections. Avoid for short forms — tabs add navigation cost.

## Inline tabs [UNFOLD]

```python
from unfold.admin import StackedInline, TabularInline

class OrderInline(TabularInline):
    model = Order
    tab = True                  # renders as tab within changeform

class NoteInline(StackedInline):
    model = Note
    tab = True
```

Combines with fieldsets tabs: fieldset tabs and inline tabs share the tab bar. Inline's verbose_name becomes label.

## Dynamic tabs on custom pages [UNFOLD]

```python
# settings.py — tabs identified by a unique page key instead of models
UNFOLD = {
    "TABS": [
        {
            "page": "custom_page",
            "items": [
                {"title": _("Overview"), "link": reverse_lazy("admin:index")},
                {"title": _("Reports"), "link": reverse_lazy("admin:reports")},
            ],
        }
    ]
}
```

```html
{# custom page template #}
{% extends "admin/base_site.html" %}
{% load unfold %}

{% block content %}
    {% tab_list "custom_page" %}
    {# page body #}
{% endblock %}
```

## Anti-patterns

- Using settings TABS to group fields — wrong layer; use fieldsets tab classes.
- Using fieldsets tabs to simulate navigation between pages — URLs don't change with field tabs; user loses deep-linking/bookmarks per section.
- Tab item `link` as plain string with app label typos — use `reverse_lazy("admin:app_model_changelist")` so URL conf errors surface.
- Forgetting `"detail": True` then wondering why changeform shows no tabs.
- Overlapping tab groups matching the same model — last match wins; keep `models` lists disjoint.

## Performance

Tabs are rendered chrome evaluated per admin page; permission callbacks run per item per request — keep them `has_perm`-style checks, not queries.

## Security

Tab item `permission` only **hides the link**; it does not protect target views. Target admins must enforce model permissions themselves (Django does this by default for model admins; custom pages must check — `unfold-custom-pages`).

## Testing

```python
def test_fieldset_tabs_render(admin_client):
    res = admin_client.get("/admin/shop/product/1/change/")
    body = res.content.decode()
    assert "Pricing" in body and "Inventory" in body

def test_tab_permission(admin_client_limited):
    res = admin_client_limited.get("/admin/shop/order/")
    assert "Customers" not in res.content.decode()
```

## Related skills

`unfold-settings`, `unfold-modeladmin` (fieldsets), `unfold-inlines`, `unfold-custom-pages`.
