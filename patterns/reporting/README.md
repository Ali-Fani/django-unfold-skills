# Pattern: Reporting

Recurring report pages (daily/weekly/monthly) with export — services + custom pages, cached aggregates.

## When
Periodic reports, CSV/XLSX exports, scheduled digests surfaced in admin.

## Reference implementation

```python
# services/reports.py
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from datetime import date


def monthly_revenue(year: int) -> list[dict]:
    rows = (
        Order.objects.filter(created_at__year=year, status=Order.Status.PAID)
        .annotate(month=TruncMonth("created_at"))
        .values("month")
        .annotate(revenue=Sum("total"), orders=Count("pk"))
        .order_by("month")
    )
    return list(rows)


def revenue_to_csv(year: int) -> str:
    import csv, io
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["month", "revenue", "orders"])
    for r in monthly_revenue(year):
        writer.writerow([r["month"].strftime("%Y-%m"), r["revenue"], r["orders"]])
    return buf.getvalue()
```

```python
# admin.py — report page + export action
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.views import View

from unfold.admin import ModelAdmin
from unfold.views import UnfoldModelAdminViewMixin


class MonthlyReportView(UnfoldModelAdminViewMixin, View):
    title = "Monthly revenue"
    permission_required = ("shop.view_order",)
    template_name = "admin/monthly_report.html"

    def get(self, request):
        year = int(request.GET.get("year") or timezone.now().year)
        rows = monthly_revenue(year)          # cached upstream if heavy
        return render(request, self.template_name, {
            "year": year,
            "rows": rows,
            "table": {
                "headers": ["Month", "Revenue", "Orders"],
                "rows": [[r["month"].strftime("%Y-%m"),
                          f"{r['revenue']:.2f}", r["orders"]] for r in rows],
            },
            **self.admin_site.each_context(request),
        })


class ExportReportView(UnfoldModelAdminViewMixin, View):
    title = "Export monthly revenue"
    permission_required = ("shop.view_order",)

    def get(self, request):
        year = int(request.GET.get("year") or timezone.now().year)
        response = HttpResponse(revenue_to_csv(year), content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="revenue-{year}.csv"'
        return response


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    def get_urls(self):
        return super().get_urls() + [
            path("reports/monthly/", self.admin_site.admin_view(
                MonthlyReportView.as_view(model_admin=self)), name="order_monthly_report"),
            path("reports/monthly/export/", self.admin_site.admin_view(
                ExportReportView.as_view(model_admin=self)), name="order_monthly_export"),
        ]
```

```django
{# templates/admin/monthly_report.html #}
{% extends "admin/base_site.html" %}
{% load unfold %}

{% block content %}
    {% component "unfold/components/card.html" with title="Monthly revenue " year %}
        {% component "unfold/components/table.html" with table=table striped=1 %}{% endcomponent %}
    {% endcomponent %}
    <a class="..." href="export/?year={{ year }}">Download CSV</a>
{% endblock %}
```

## Rules
- Query functions in services; admin renders only.
- Exports: stream or cap rows; for big exports → background task + file link (see `unfold-production`).
- Cache per (report, params) with short TTL; invalidate on data-change events if freshness matters.
- Export endpoints need same `permission_required` as the report view.

## Related
`patterns/analytics-dashboard`, `unfold-custom-pages`, `unfold-components`, `unfold-production`.
