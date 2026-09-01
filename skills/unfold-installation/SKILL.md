---
name: unfold-installation
description: Installs and wires django-unfold correctly — INSTALLED_APPS ordering, optional contrib apps, User/Group admin re-registration with Unfold forms, custom admin sites. Use when setting up Unfold, when the admin looks unstyled, when User/Group pages render wrong, or when a third-party admin is unstyled.
---
# Verified against: django-unfold 0.104.1
# Docs: https://unfoldadmin.com/docs/installation/ , https://unfoldadmin.com/docs/installation/auth/
# Dependencies: unfold-core. Related: unfold-settings, unfold-modeladmin, unfold-integrations, unfold-debugging.

# Installation

## Purpose

Correct project wiring for django-unfold. Most "Unfold doesn't work" reports are ordering or inheritance mistakes fixed here.

## Activation / Triggers

- "Set up Unfold in my Django project"
- "Admin looks unstyled / plain Django admin"
- "User or Group pages look wrong"
- "Which unfold contrib apps do I need?"

## Canonical installation

```bash
pip install django-unfold
```

```python
# settings.py — order matters
INSTALLED_APPS = [
    "unfold",                        # REQUIRED: before django.contrib.admin
    "unfold.contrib.filters",        # optional: Unfold filters (dropdown, numeric, datetime, autocomplete)
    "unfold.contrib.forms",          # optional: WysiwygWidget, ArrayWidget
    "unfold.contrib.inlines",        # optional: nonrelated inlines
    "unfold.contrib.import_export",  # optional: only if django-import-export used
    "unfold.contrib.guardian",       # optional: only if django-guardian used
    "unfold.contrib.simple_history", # optional: only if django-simple-history used
    "unfold.contrib.location_field", # optional: only if django-location-field used
    "unfold.contrib.constance",      # optional: only if django-constance used
    "unfold.contrib.hijack",         # optional: only if django-hijack used
    "django.contrib.admin",
    # ... rest
]
```

```python
# urls.py
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
```

Rules:
- Add contrib apps **only when the corresponding feature/package is used** — each adds template/load overhead.
- `unfold.contrib.filters` must sit **immediately after `"unfold"`** (documented requirement).
- No model migrations are needed; Unfold works on existing admin registrations.

## User & Group re-registration [UNFOLD]

Django's built-in `UserAdmin`/`GroupAdmin` render unstyled because they don't inherit Unfold's `ModelAdmin`. Unregister and re-register:

```python
# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
```

MRO order: `BaseUserAdmin` first, `ModelAdmin` second — keeps Django's fieldsets/logic and Unfold's styling.

## Custom admin site [UNFOLD]

For parallel or separate admin surfaces:

```python
# sites.py
from unfold.sites import UnfoldAdminSite

custom_admin_site = UnfoldAdminSite(name="custom_admin_site")

# urls.py
urlpatterns = [path("control/", custom_admin_site.urls)]

# registration
@admin.register(MyModel, site=custom_admin_site)
class MyModelAdmin(ModelAdmin): ...
```

Use when: two admin audiences (staff vs operators) need different registration sets. Avoid when one admin with permissions suffices.

## Anti-patterns

- Putting `"unfold"` after `"django.contrib.admin"` → templates resolve to default admin.
- Inheriting `django.contrib.admin.ModelAdmin` for some models → those pages unstyled. Audit **every** `admin.site.register` call.
- Installing all contrib apps "to be safe" → unnecessary template overrides, harder upgrades.
- Forgetting to re-register third-party package admins (celery-beat, import-export models) → mixed styling. See `unfold-integrations`.
- Building custom Tailwind CSS against Tailwind v3 semantics with a current Unfold → broken styles. Unfold ≥0.56.0 uses Tailwind v4. See `unfold-tailwind`.

## Security

- Custom admin sites still require `admin_site.admin_view()` wrapping for custom URLs (handled by Unfold views; required manually for custom views — see `unfold-custom-pages`).
- `DEBUG=True` + admin = error page leakage; never run admin on public hosts with DEBUG.

## Testing

After install, smoke test: `/admin/` renders styled sidebar, a model changelist uses Unfold tables, User change page renders Unfold forms. A failing smoke test = ordering/inheritance problem, not a Unfold bug.

## Related skills

- `unfold-settings` — first customization steps.
- `unfold-debugging` — if install smoke tests fail.
- `unfold-integrations` — third-party package re-registration.
