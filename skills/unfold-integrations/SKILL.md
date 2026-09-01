---
name: unfold-integrations
description: Third-party package support — the universal re-registration pattern (unregister, re-register with Unfold bases, base-first MRO), the official contrib apps (import_export, guardian, simple_history, constance, location_field, hijack), and the django-celery-beat widget/form override example. Use when a third-party package's admin pages look unstyled, when integrating celery-beat/import-export/guardian/simple-history, or when custom package widgets clash with Unfold.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/integrations/* (12 official guides)
# Dependencies: unfold-core, unfold-installation. Related: unfold-modeladmin, unfold-fields.

# Integrations

## Purpose

Third-party package support. General rule: every third-party ModelAdmin renders unstyled until re-registered with Unfold bases (and contrib app added when one exists). Unfold ships dedicated contrib apps for the packages below.

## The re-registration pattern (universal)

```python
from django.contrib import admin
from unfold.admin import ModelAdmin

admin.site.unregister(ThirdPartyModel)

@admin.register(ThirdPartyModel)
class UnstyledFixAdmin(BaseThirdPartyAdmin, ModelAdmin):   # MRO: base first, Unfold second
    pass
```

## Supported packages (official guides)

| Package | Contrib app | Notes |
|---|---|---|
| django-import-export | `unfold.contrib.import_export` | Import/export buttons/batch styled |
| django-guardian | `unfold.contrib.guardian` | Object permissions UI |
| django-simple-history | `unfold.contrib.simple_history` | History pages styled |
| django-constance | `unfold.contrib.constance` | Settings config UI |
| django-celery-beat | — (manual re-registration) | Requires widget + form overrides (see below) |
| django-money | — | Currency widgets |
| django-location-field | `unfold.contrib.location_field` | Map widget |
| djangoql | — | Query language in changelist |
| django-json-widget | — | JSON pretty editor |
| django-hijack | `unfold.contrib.hijack` | User impersonation |
| django-modeltranslation | — | Translated fields |
| django-waffle | — | Feature flags |

Add contrib apps **only when the package is installed** (see `unfold-installation`).

## django-celery-beat (most complex, verified example shape)

Celery Beat's admin uses custom widgets/forms that need Unfold equivalents:

```python
from django_celery_beat.models import (
    ClockedSchedule, CrontabSchedule, IntervalSchedule,
    PeriodicTask, SolarSchedule,
)
from django_celery_beat.admin import (
    ClockedScheduleAdmin as BaseClockedScheduleAdmin,
    CrontabScheduleAdmin as BaseCrontabScheduleAdmin,
    PeriodicTaskAdmin as BasePeriodicTaskAdmin,
    PeriodicTaskForm, TaskSelectWidget,
)
from unfold.admin import ModelAdmin
from unfold.widgets import UnfoldAdminSelectWidget, UnfoldAdminTextInputWidget

for m in (PeriodicTask, IntervalSchedule, CrontabSchedule, SolarSchedule, ClockedSchedule):
    admin.site.unregister(m)

class UnfoldTaskSelectWidget(UnfoldAdminSelectWidget, TaskSelectWidget):
    pass

class UnfoldPeriodicTaskForm(PeriodicTaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["task"].widget = UnfoldAdminTextInputWidget()
        self.fields["regtask"].widget = UnfoldTaskSelectWidget()

@admin.register(PeriodicTask)
class PeriodicTaskAdmin(BasePeriodicTaskAdmin, ModelAdmin):
    form = UnfoldPeriodicTaskForm

@admin.register(IntervalSchedule)
class IntervalScheduleAdmin(ModelAdmin):
    pass

@admin.register(CrontabSchedule)
class CrontabScheduleAdmin(BaseCrontabScheduleAdmin, ModelAdmin):
    pass

@admin.register(SolarSchedule)
class SolarScheduleAdmin(ModelAdmin):
    pass

@admin.register(ClockedSchedule)
class ClockedScheduleAdmin(BaseClockedScheduleAdmin, ModelAdmin):
    pass
```

Lesson: when a package ships custom **forms/widgets**, they too must be wrapped with Unfold widget bases — re-registering the admin alone isn't enough.

## Decision rules

- Package in the table → follow its official guide link; use contrib app.
- Package not in table but has admin → re-register with `ModelAdmin`; if pages still look off (custom templates), check whether package templates extend `admin/base_site.html` (usually fixable by adding contrib-style overrides in project) — otherwise accept partial styling or contribute upstream.
- Never fork Unfold templates for a package fix without first trying re-registration.

## Anti-patterns

- Registering package models on a second `AdminSite` to "escape" styling issues — splits permissions/UX.
- Copying old integration snippets from blog posts without checking the official guide — APIs move (e.g., celery-beat form internals).
- Adding contrib apps for packages not installed → import errors at startup.

## Security

- django-guardian: object-level permissions tighten admin — ensure custom views/actions also respect them (guardian checks are not automatic in custom code).
- django-hijack: impersonation is high-risk; restrict to superusers, audit impersonation sessions.

## Testing

```python
def test_package_admin_styled(admin_client):
    res = admin_client.get("/admin/django_celery_beat/periodictask/")
    assert res.status_code == 200
    assert "unfold" in res.content.decode().lower() or b"sidebar" in res.content
```

## Related skills

`unfold-installation` (INSTALLED_APPS), `unfold-modeladmin` (re-registration MRO), `unfold-fields` (widget wrapping).
