# Pattern: Settings Page

Global configuration form (feature flags, API credentials, webhooks) as custom admin page.

## When
App settings not tied to a single model row, or too sensitive for a writable model admin. (Django-constance alternative when not installed.)

## Reference implementation

```python
# forms.py
from django import forms
from unfold.widgets import UnfoldAdminTextInputWidget, UnfoldAdminSelectWidget


class SettingsForm(forms.Form):
    maintenance_mode = forms.BooleanField(required=False, label="Maintenance mode")
    support_email = forms.EmailField(required=False)
    sync_frequency = forms.ChoiceField(
        choices=[("hourly", "Hourly"), ("daily", "Daily"), ("weekly", "Weekly")],
        widget=UnfoldAdminSelectWidget,
    )
    webhook_url = forms.URLField(required=False, widget=UnfoldAdminTextInputWidget)
```

```python
# services/settings.py — storage-agnostic
from django.core.cache import cache
from typing import Any


def get_setting(key: str, default: Any = None) -> Any:
    value = cache.get(f"appsetting:{key}")
    if value is None:
        value = AppSetting.objects.get_value(key, default)
        cache.set(f"appsetting:{key}", value, 3600)
    return value


def save_settings(cleaned: dict, *, actor) -> None:
    with transaction.atomic():
        for key, value in cleaned.items():
            AppSetting.objects.set(key, value)
        AuditLog.objects.create(actor=actor, action="settings.change",
                                payload=cleaned)
    cache.delete_pattern("appsetting:*")   # or per-key invalidation
```

```python
# admin.py
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View

from unfold.views import UnfoldModelAdminViewMixin


class SettingsView(UnfoldModelAdminViewMixin, View):
    title = "Application settings"
    permission_required = ("app.change_appsetting",)   # dedicated permission
    template_name = "admin/settings.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, self._ctx(SettingsForm(
            initial={k: get_setting(k) for k in ("maintenance_mode", "support_email",
                                                 "sync_frequency", "webhook_url")})))

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SettingsForm(request.POST)
        if form.is_valid():
            save_settings(form.cleaned_data, actor=request.user)
            messages.success(request, "Settings saved.")
            return redirect(reverse_lazy("admin:app_settings"))
        messages.error(request, "Fix errors below.")
        return render(request, self.template_name, self._ctx(form))

    def _ctx(self, form):
        return {"form": form, **self.admin_site.each_context(self.request)}


# standalone page in urls.py
urlpatterns = [
    path("admin/settings/", staff_member_required(SettingsView.as_view()),
         name="app_settings"),
]
```

```django
{# templates/admin/settings.html #}
{% extends "admin/base_site.html" %}
{% load unfold %}

{% block content %}
    <form method="post" class="max-w-2xl">
        {% csrf_token %}
        {% for field in form %}
            {% include "unfold/helpers/field.html" with field=field %}
        {% endfor %}
        <button type="submit">Save</button>
    </form>
{% endblock %}
```

```python
# SIDEBAR nav entry
{"title": _("Settings"), "icon": "settings", "link": reverse_lazy("admin:app_settings")}
```

## Rules
- Dedicated permission (`app.change_appsetting`), not just staff.
- POST → validate → save in service → audit → PRG redirect + messages.
- Secrets (API keys) shown as masked readonly inputs; never round-trip value; write-only field if editable at all.
- Cache invalidation on save — stale flags worse than none.
- Audit every change (who flipped maintenance mode when).

## Related
`unfold-custom-pages`, `unfold-fields` (widgets), `unfold-security`, `unfold-production`.
