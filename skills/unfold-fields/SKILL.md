---
name: unfold-fields
description: Changeform input rendering — WysiwygWidget (Trix), ArrayWidget for Postgres ArrayField, pretty JSON readonly display, conditional_fields (Alpine.js show/hide), UnfoldAdmin* form widgets, form-level autocomplete fields, and the unfold_crispy template pack. Use when adding rich text/array/JSON editing, when fields should show/hide based on other field values, or when styling forms on custom admin pages.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/widgets/array/, wysiwyg, /docs/fields/json/, autocomplete, /docs/configuration/conditional-fields/, crispy-forms
# Dependencies: unfold-core, unfold-installation. Related: unfold-modeladmin, unfold-tabs, unfold-integrations.

# Fields, Widgets, Forms

## Purpose

Changeform input rendering: Unfold widgets, conditional fields, JSON, form-level autocomplete, and the crispy-forms template pack. For changelist filters → `unfold-filters`; for display-side (badges etc.) → `unfold-modeladmin`.

## Decision rules

| Need | Use |
|---|---|
| Rich text editing on TextField | `WysiwygWidget` (Trix-based) via `formfield_overrides` |
| Postgres ArrayField editing | `ArrayWidget` |
| Pretty JSON display | JSONField in `readonly_fields` |
| Show/hide fields based on other field values | `conditional_fields` (Alpine.js expressions) |
| Uniform Unfold styling for custom forms' widgets | `unfold.widgets.UnfoldAdmin*` widgets |
| Form-level custom autocomplete (non-FK) | `UnfoldAdminAutocompleteModelChoiceField` + `BaseAutocompleteView` subclass |
| Crispy forms in admin custom pages | `CRISPY_TEMPLATE_PACK = "unfold_crispy"` |
| FK select in Django-native changeform | `autocomplete_fields` [DJANGO] — first choice, no custom code |

## WysiwygWidget [UNFOLD]

```python
# requires unfold.contrib.forms in INSTALLED_APPS
from django.db import models
from unfold.admin import ModelAdmin
from unfold.contrib.forms.widgets import WysiwygWidget

@admin.register(Page)
class PageAdmin(ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }
```

Images inserted via URL after upload through media system. Global override applies to **all** TextFields of that admin — scope per-admin, or per-field via a custom `form`.

## ArrayWidget [UNFOLD]

```python
from django.contrib.postgres.fields import ArrayField

@admin.register(Tag)
class TagAdmin(ModelAdmin):
    formfield_overrides = {
        ArrayField: {"widget": ArrayWidget},
    }
```

## JSON field display [UNFOLD]

```python
@admin.register(Webhook)
class WebhookAdmin(ModelAdmin):
    readonly_fields = ["payload"]
```

JSONField in readonly_fields renders formatted (syntax highlighting when Pygments installed). Editable JSONField stays a textarea — combine with django-json-widget if needed (see `unfold-integrations`).

## Conditional fields [UNFOLD]

Alpine.js expressions toggling field visibility:

```python
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    conditional_fields = {
        "shipping_address": "delivery_method == 'courier'",
        "digital_license": "delivery_method == 'download'",
    }
```

Expressions evaluate against other **form field values** (Alpine scope). Use for dependent single-record forms; not a validation mechanism — server-side `clean_*` still required (client-side show/hide is cosmetic only).

## Unfold form widgets [UNFOLD]

For custom forms (actions, custom pages) so inputs match admin styling:

```python
from unfold.widgets import (
    UnfoldAdminTextInputWidget,
    UnfoldAdminSelectWidget,
    UnfoldAdminSplitDateTimeWidget,
    UnfoldAdminEmailInputWidget,   # check full list in unfold/widgets.py of installed version
)

class ExportForm(forms.Form):
    date_from = forms.SplitDateTimeField(widget=UnfoldAdminSplitDateTimeWidget)
    note = forms.CharField(widget=UnfoldAdminTextInputWidget)
```

Date widgets need Django admin JS (jQuery, calendar, DateTimeShortcuts) via form `Media` — see action form example in `unfold-actions`.

## Form-level autocomplete fields [UNFOLD — advanced]

For ModelChoiceField backed by custom search (not standard FK):

1. Subclass `BaseAutocompleteView`, return JSON options.
2. Register as custom URL in ModelAdmin `get_urls()` (or custom page).
3. Use `UnfoldAdminAutocompleteModelChoiceField` / `UnfoldAdminMultipleAutocompleteModelChoiceField` with `url_path` pointing to registered pattern name.

Follow https://unfoldadmin.com/docs/fields/autocomplete/ verbatim; it's a low-level API — prefer `autocomplete_fields` [DJANGO] wherever it suffices.

## Crispy Forms template pack [UNFOLD]

```python
# settings.py
INSTALLED_APPS = [..., "unfold", ..., "crispy_forms", ...]
CRISPY_TEMPLATE_PACK = "unfold_crispy"
CRISPY_ALLOWED_TEMPLATE_PACKS = ["unfold_crispy"]
```

Use in custom pages/dashboards rendering crispy forms with Unfold look.

## Anti-patterns

- Overriding `models.TextField` widget globally in `formfield_overrides` of a shared base ModelAdmin used by 30 admins — scope intentionally.
- Treating `conditional_fields` as authorization/validation — hidden ≠ unpostable; always validate server-side.
- Reaching for form-level autocomplete when `autocomplete_fields` on FK suffices.
- Rendering JSONField editable + readonly simultaneously — pick per `readonly_fields` membership.
- Using WysiwygWidget on fields holding markdown (double-format confusion) — store HTML or markdown, render accordingly.

## Security

- WysiwygWidget content is HTML — sanitize on display outside admin (admin itself renders it; external site rendering needs cleaning, e.g. `bleach`).
- Conditional fields never remove data from POST — sensitive fields excluded server-side (`exclude` or form `clean`) when not applicable.

## Testing

```python
def test_wysiwyg_render(admin_client):
    res = admin_client.get("/admin/cms/page/add/")
    assert "trix" in res.content.decode().lower()
```

## Related skills

`unfold-modeladmin` (formfield_overrides live there), `unfold-custom-pages` (custom forms), `unfold-integrations` (django-json-widget, modeltranslation etc.).
