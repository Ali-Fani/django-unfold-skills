---
name: unfold-custom-pages
description: Non-CRUD admin surfaces inside Unfold chrome — UnfoldModelAdminViewMixin (title + permission_required), ModelAdmin get_urls integration, standalone pages with staff_member_required, templates extending admin/base_site.html, form + POST + CSRF + messages handling. Use when building report/analytics/settings/wizard pages, any admin page with a form, or when a ModelAdmin is being abused for non-CRUD content.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/configuration/custom-pages/
# Dependencies: unfold-core. Related: unfold-actions, unfold-dashboard, unfold-navigation, unfold-tabs, unfold-security, unfold-fields.

# Custom Admin Pages

## Purpose

Non-CRUD admin surfaces: reports, wizards, settings forms, analytics pages — inside admin chrome with admin auth, styled by Unfold.

## Decision rules

- Page needs form + POST + validation → **custom page** (never fake ModelAdmin).
- One-click object operation → action (`unfold-actions`), not page.
- Read-only analytics → dashboard override (`unfold-dashboard`) unless URL params/POST needed → custom page.
- Reuse across models → attach to a ModelAdmin via `get_urls()`; site-wide page → standalone view registered in urls.py wrapped in `admin_view`-style auth.
- Custom page belongs in sidebar → `SIDEBAR` nav item; needs tabs → `TABS` `page` key + `tab_list`.

## Canonical: page bound to a ModelAdmin [UNFOLD]

```python
# admin.py
from django.urls import path
from django.views.generic import TemplateView

from unfold.admin import ModelAdmin
from unfold.views import UnfoldModelAdminViewMixin

class ReportView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Sales report"          # REQUIRED: page header title
    permission_required = ()        # REQUIRED: tuple of perm codenames, e.g. ("shop.view_order",)
    template_name = "admin/report.html"

@admin.register(Order)
class OrderAdmin(ModelAdmin):
    def get_urls(self):
        # IMPORTANT: model_admin is required
        custom_view = self.admin_site.admin_view(
            ReportView.as_view(model_admin=self)
        )
        return super().get_urls() + [
            path("report/", custom_view, name="order_report"),
        ]
```

URL lands at `/admin/shop/order/report/` (custom paths append under model's namespace).

Mixin contract (verified): `title` and `permission_required` required. `permission_required` checked against `request.user` — empty tuple = staff-only.

## Site-wide custom page (no model)

```python
# views.py
class SystemStatusView(UnfoldModelAdminViewMixin, TemplateView):
    title = "System status"
    permission_required = ()
    template_name = "admin/status.html"

# urls.py — auth via admin site's admin_view equivalent: wrap with staff check
from django.contrib.admin.views.decorators import staff_member_required
urlpatterns = [
    path("admin/status/", staff_member_required(SystemStatusView.as_view()), name="admin_status"),
]
```

`staff_member_required` [DJANGO] keeps admin session/redirect behavior for standalone pages. ModelAdmin-bound pages get this automatically via `admin_view()`.

## Template

```django
{% extends "admin/base_site.html" %}

{% load admin_urls i18n unfold %}

{% block content %}
    {% tab_list "reports" %}     {# optional tabs via UNFOLD["TABS"] page key #}

    {# page body — components or plain Tailwind markup #}
{% endblock %}
```

Extending `admin/base_site.html` (or `admin/base.html`) preserves Unfold chrome: sidebar, header, theme, messages.

## Form + POST handling

```python
from django import forms
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from unfold.views import UnfoldModelAdminViewMixin

class SyncSettingsForm(forms.Form):
    frequency = forms.ChoiceField(choices=[("hourly", "Hourly"), ("daily", "Daily")])
    webhook_url = forms.URLField(required=False)

class SyncSettingsView(UnfoldModelAdminViewMixin, View):
    title = "Sync settings"
    permission_required = ("shop.change_settings",)
    template_name = "admin/sync_settings.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template_name, self.get_context(form=SyncSettingsForm(initial=load_settings())))

    def post(self, request: HttpRequest) -> HttpResponse:
        form = SyncSettingsForm(request.POST)
        if form.is_valid():
            save_settings(form.cleaned_data, actor=request.user)    # service layer
            messages.success(request, "Settings saved.")
            return redirect(reverse_lazy("admin:sync_settings"))
        messages.error(request, "Fix errors below.")
        return render(request, self.template_name, self.get_context(form=form))

    def get_context(self, **extra):
        context = self.admin_site.each_context(self.request)  # Unfold chrome vars
        context.update(extra)
        return context
```

```django
{% extends "admin/base_site.html" %}
{% load i18n unfold %}

{% block content %}
    <form method="post" class="max-w-2xl">
        {% csrf_token %}
        {% for field in form %}
            {% include "unfold/helpers/field.html" with field=field %}
        {% endfor %}
        <button type="submit" class="...">Save</button>
    </form>
{% endblock %}
```

Verified helpers: `unfold/helpers/field.html` renders a styled field wrapper. `admin_site.each_context(request)` supplies base template variables.

Rules:
- Always `{% csrf_token %}` in POST forms.
- Never trust the form for authorization — `permission_required` + explicit re-checks for object-level concerns.
- After successful POST → POST/redirect/GET with `messages` (never render success inline; refresh-duplicates).

## Navigation for custom pages

```python
UNFOLD = {
    "SIDEBAR": {"navigation": [
        {"title": _("Reports"), "icon": "monitoring",
         "link": reverse_lazy("admin:order_report")},   # name given in get_urls
    ]},
    "TABS": [{"page": "reports", "items": [...]}],       # + {% tab_list "reports" %}
}
```

## Anti-patterns

- Faking pages via readonly ModelAdmin with one object — brittle URL hacks, broken permissions, worse than 10 lines of custom view.
- Skipping `permission_required` ("only staff reach admin") — staff ≠ authorized for this operation; use real permissions.
- Templates extending nothing (`base.html` missing) → page renders without sidebar/theme — a sign the mixin/template base is wrong.
- Business logic inside the view class — call services; view handles HTTP only (`unfold-production`).
- Forgetting `model_admin=self` when using `as_view(model_admin=...)` — mixin context breaks.

## Security

- `permission_required` tuple checked by mixin; standalone pages need explicit `staff_member_required` + permission checks.
- POST targets must re-validate everything (forms, object ownership); request.user-controlled inputs are untrusted.
- File uploads on custom pages: validate type/size, random filenames, never serve uploaded HTML inline (XSS via admin upload is real).
- Custom pages bypass ModelAdmin's per-object queryset isolation — implement scoping manually (tenant, region).

## Testing

```python
def test_custom_page_get(admin_client):
    res = admin_client.get("/admin/shop/order/report/")
    assert res.status_code == 200

def test_custom_page_permission(non_perm_client):
    assert non_perm_client.get("/admin/shop/order/report/").status_code == 403

def test_form_post(admin_client):
    res = admin_client.post("/admin/sync-settings/", {"frequency": "daily", "webhook_url": ""})
    assert res.status_code == 302
```

## Related skills

`unfold-actions` (when a page is overkill for an operation), `unfold-dashboard`, `unfold-navigation`, `unfold-security`, `unfold-fields` (widgets for custom forms).
