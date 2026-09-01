# Pattern: Analytics Dashboard

Interactive analytics page (period filters, KPIs, charts, detail table) as **custom page** (POST filters → not the index override).

## When
- URL-parameter/deep-linkable time ranges.
- Multiple related charts + table + export link.
- Role-scoped metrics.

Use dashboard index override (`unfold-dashboard`) only when static KPI landing suffices.

## Reference implementation

```python
# services/analytics.py — query layer, no admin imports
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay
from django.utils import timezone


def order_stats(period_days: int = 30) -> dict:
    start = timezone.now() - timezone.timedelta(days=period_days)
    qs = Order.objects.filter(created_at__gte=start)
    daily = (
        qs.annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(revenue=Sum("total"), orders=Count("pk"))
        .order_by("day")
    )
    rows = list(daily)
    return {
        "labels": [r["day"].strftime("%m-%d") for r in rows],
        "revenue": [float(r["revenue"] or 0) for r in rows],
        "orders": [r["orders"] for r in rows],
        "total": sum(r["revenue"] or 0 for r in rows),
    }


# components.py
import json
from unfold.components import BaseComponent, register_component


@register_component
class RevenueChartComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        stats = kwargs["stats"]
        context = super().get_context_data(**kwargs)
        context.update({
            "height": 320,
            "data": json.dumps({
                "labels": stats["labels"],
                "datasets": [
                    {"label": "Revenue", "data": stats["revenue"],
                     "backgroundColor": "var(--color-primary-700)"},
                    {"label": "Orders", "data": stats["orders"],
                     "borderColor": "var(--color-primary-400)", "type": "line"},
                ],
            }),
        })
        return context


# admin.py
from django import forms
from django.shortcuts import render
from django.urls import path
from django.views import View
from django.http import HttpRequest, HttpResponse

from unfold.admin import ModelAdmin
from unfold.views import UnfoldModelAdminViewMixin
from .services import analytics


class PeriodForm(forms.Form):
    days = forms.ChoiceField(
        choices=[("7", "7 days"), ("30", "30 days"), ("90", "90 days")],
    )


class AnalyticsView(UnfoldModelAdminViewMixin, View):
    title = "Analytics"
    permission_required = ("shop.view_order",)
    template_name = "admin/analytics.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        form = PeriodForm(request.GET or None)
        days = int(form.data.get("days") or 30) if form.is_valid() else 30
        stats = analytics.order_stats(days)
        return render(request, self.template_name, {
            "form": form, "stats": stats,
            **self.admin_site.each_context(request),
        })


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    def get_urls(self):
        return super().get_urls() + [
            path("analytics/", self.admin_site.admin_view(
                AnalyticsView.as_view(model_admin=self)), name="order_analytics"),
        ]
```

```django
{# templates/admin/analytics.html #}
{% extends "admin/base_site.html" %}
{% load i18n unfold %}

{% block content %}
    <form method="get" class="flex gap-4 mb-4">
        {{ form.days }}
        <button type="submit">Apply</button>
    </form>

    {% component "unfold/components/card.html" with title="Revenue & orders" %}
        {% component "unfold/components/chart/bar.html" with component_class="RevenueChartComponent" stats=stats %}{% endcomponent %}
    {% endcomponent %}

    {% component "unfold/components/card.html" with title="Total revenue" %}
        <div class="text-3xl font-semibold">{{ stats.total|floatformat:2 }} €</div>
    {% endcomponent %}
{% endblock %}
```

Note: passing `stats=stats` into `{% component %}` lands in component kwargs — verified pattern for data-driven components (`with data=...` variant also documented). If the installed version doesn't forward extra kwargs to `get_context_data`, fall back to the documented two modes (`component_class` or `data=`) and set context in the view.

## Checklist
- [ ] Query logic in services module (testable without admin)
- [ ] GET param filtering (deep-linkable), no POST needed for read-only
- [ ] Cache heavy aggregates when period > 90d
- [ ] Charts use CSS variables for colors

## Related
`unfold-dashboard`, `unfold-custom-pages`, `unfold-components`.
