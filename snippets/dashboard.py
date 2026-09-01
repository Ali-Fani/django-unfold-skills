# Dashboard snippet — DASHBOARD_CALLBACK + template + component (django-unfold 0.104.x)
# settings.py: UNFOLD = {"DASHBOARD_CALLBACK": "app.views.dashboard_callback"}

import json
from typing import Any

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay
from django.http import HttpRequest
from django.utils import timezone

from unfold.components import BaseComponent, register_component

User = get_user_model()


def dashboard_callback(request: HttpRequest, context: dict) -> dict:
    """Inject variables into templates/admin/index.html (dashboard override)."""
    ctx = cache.get("admin_dash_ctx")
    if ctx is None:
        ctx = build_dashboard_context()
        cache.set("admin_dash_ctx", ctx, 300)  # 5 min TTL — global stats only
    context.update(ctx)
    return context


def build_dashboard_context() -> dict[str, Any]:
    start = timezone.now() - timezone.timedelta(days=30)
    daily = list(
        Order.objects.filter(created_at__gte=start)
        .annotate(day=TruncDay("created_at"))
        .values("day")
        .annotate(revenue=Sum("total"), orders=Count("pk"))
        .order_by("day")
    )
    recent_orders = list(
        Order.objects.order_by("-created_at")
        .values("pk", "number", "total", "status")[:10]
    )
    recent_users = list(
        User.objects.order_by("-date_joined")
        .values("pk", "email", "date_joined")[:10]
    )
    return {
        "kpi_revenue": sum(r["revenue"] or 0 for r in daily),
        "kpi_orders": sum(r["orders"] for r in daily),
        "chart": {
            "labels": [r["day"].strftime("%m-%d") for r in daily],
            "revenue": [float(r["revenue"] or 0) for r in daily],
            "orders": [r["orders"] for r in daily],
        },
        # table component expects {"headers": [...], "rows": [[...], ...]}
        "recent_orders_table": {
            "headers": ["Number", "Total", "Status"],
            "rows": [[o["number"], f"{o['total']:.2f}", o["status"]] for o in recent_orders],
        },
        "recent_users_table": {
            "headers": ["Email", "Joined"],
            "rows": [[u["email"], u["date_joined"].strftime("%Y-%m-%d")] for u in recent_users],
        },
    }


@register_component
class DashboardChartComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chart = kwargs.get("chart") or build_dashboard_context()["chart"]
        context.update({
            "height": 320,
            "data": json.dumps({
                "labels": chart["labels"],
                "datasets": [
                    {
                        "label": "Revenue",
                        "data": chart["revenue"],
                        "backgroundColor": "var(--color-primary-700)",
                    },
                    {
                        "label": "Orders",
                        "data": chart["orders"],
                        "borderColor": "var(--color-primary-400)",
                        "type": "line",
                        # "displayYAxis": True, "maxTicksXLimit": 50, "suffixYAxis": "€",
                    },
                ],
            }),
        })
        return context


DASHBOARD_TEMPLATE = """
{# templates/admin/index.html #}
{% extends "admin/base_site.html" %}
{% load i18n unfold %}

{% block content %}
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
        {% component "unfold/components/card.html" with title="Revenue (30d)" %}
            <div class="text-2xl font-semibold">{{ kpi_revenue|floatformat:2 }} €</div>
        {% endcomponent %}
        {% component "unfold/components/card.html" with title="Orders (30d)" %}
            <div class="text-2xl font-semibold">{{ kpi_orders }}</div>
        {% endcomponent %}
    </div>

    {% component "unfold/components/card.html" with title="Trend" %}
        {% component "unfold/components/chart/bar.html" with component_class="DashboardChartComponent" chart=chart %}{% endcomponent %}
    {% endcomponent %}

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
        {% component "unfold/components/card.html" with title="Recent orders" %}
            {% component "unfold/components/table.html" with table=recent_orders_table striped=1 card_included=1 %}{% endcomponent %}
        {% endcomponent %}
        {% component "unfold/components/card.html" with title="Recent users" %}
            {% component "unfold/components/table.html" with table=recent_users_table striped=1 card_included=1 %}{% endcomponent %}
        {% endcomponent %}
    </div>
{% endblock %}
"""

# NOTE on passing extra kwargs (e.g. chart=chart) through {% component %}:
# documented modes are component_class=... or data=... . If the installed version
# does not forward extra `with` kwargs into get_context_data(**kwargs), fall back:
# pass the payload via the documented `data=` mode, or let the component read from
# the request-level context (dashboard_callback already injected `chart`).
