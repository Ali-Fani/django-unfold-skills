---
name: unfold-dashboard
description: Designs admin dashboards — DASHBOARD_CALLBACK + templates/admin/index.html override, five archetypes (KPI, SaaS metrics, operations, analytics, admin overview), information hierarchy, responsive grids, and query-budget rules (SQL aggregation, caching, bounded lists). Use when building an admin landing page, revenue/users/churn dashboard, ops overview, or when a dashboard is slow.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/configuration/dashboard/, demo repo github.com/unfoldadmin/formula
# Dependencies: unfold-core, unfold-components, unfold-tailwind. Related: unfold-custom-pages, unfold-performance, unfold-studio.

# Dashboards

## Purpose

Design admin landing pages: override `templates/admin/index.html`, inject data via `DASHBOARD_CALLBACK`, compose with components. This skill is about **designing** dashboards, not only rendering widgets.

## Implementation path (verified)

```python
# settings.py
UNFOLD = {"DASHBOARD_CALLBACK": "app.views.dashboard_callback"}

# app/views.py — inject context into admin index
def dashboard_callback(request, context):
    context.update(build_dashboard_context(request))
    return context
```

```django
{# templates/admin/index.html — overrides admin index #}
{% extends "admin/base_site.html" %}
{% load i18n unfold %}

{% block content %}
    ...components...
{% endblock %}
```

Custom styles in the override are **not auto-compiled** — Tailwind config required (see `unfold-tailwind`).

Decision: dashboard = `admin/index.html` override + `DASHBOARD_CALLBACK` when it's the admin landing. Use a **custom page** (`unfold-custom-pages`) instead when: dashboard needs POST filters, per-URL params deep-linking, or non-dashboard sibling pages.

## Dashboard archetypes

### 1. KPI / Executive dashboard

```
┌ KPI row (4 cards: revenue, users, churn, NPS) ┐
├ primary chart (30d trend)                    ├
├ secondary row: recent activity | alerts       ├
└ quick actions                                 ┘
```

Context:
```python
def dashboard_callback(request, context):
    today = timezone.now()
    context.update({
        "kpi_revenue": billing.revenue_30d(),
        "kpi_users": User.objects.count(),
        "kpi_churn": billing.churn_rate(),
        "recent_activity": audit.recent(10),
    })
    return context
```

```django
{% component "unfold/components/card.html" with title="Revenue (30d)" %}
    <div class="text-2xl font-semibold">{{ kpi_revenue|floatformat:2 }} €</div>
    <div class="text-sm text-base-500">+12% vs previous period</div>
{% endcomponent %}
```

### 2. SaaS metrics dashboard

Rows: MRR / ARR / active subscriptions / churn — then cohort chart (retention), plan distribution (tracker), recent signups table.

Cohort data (periods × retention %) via `cohort` component class; plan split via `tracker` component (each state = plan, width = share).

### 3. Operations dashboard

Queue state (progress components), incident alerts (cards with `warning`/`danger` link styling), recent events table, system health row (DB/cache/celery checks as KPI cards). Auto-refresh via `SCRIPTS` JS (documented `UNFOLD["SCRIPTS"]`) — keep interval ≥30s and off by default.

### 4. Analytics dashboard

Filter row (period preset links), KPI row, charts (bar + line mixed), comparison columns (current vs previous period in table), detailed table. Interactivity (POST filters) → **custom page**, not index override.

### 5. Admin overview (small teams)

Model counts, recent objects per model, quick actions (links), health indicators. Zero custom JS.

## Design rules

1. **Answer one question first**: "Is the system OK?" — health/KPI row top, always.
2. **5-second rule**: top row must communicate state without reading numbers.
3. Hierarchy: KPI (big) → trend (chart) → detail (table) → actions (links). Never start with tables.
4. Density: ≤4 KPIs top row; ≤8 total cards above fold; use tables below fold.
5. Responsive: grid `lg:grid-cols-4 md:grid-cols-2` — components collapse gracefully.
6. Money/percent formatting in Python (`floatformat`, custom helpers), never raw floats.
7. Every stat card shows: value + delta vs previous period + tiny label. Deltas need previous-period queries — compute both in one `build_dashboard_context` pass.
8. Loading: dashboard renders per request — cache expensive aggregates (see below).

## Performance (critical)

Bad: 20 cards each computing separately → 30+ queries per admin page view (index renders often!).

Good pattern — **one context builder, minimal queries**:

```python
from django.core.cache import cache

def build_dashboard_context(request) -> dict:
    ctx = cache.get("admin_dashboard_ctx")
    if ctx is None:
        ctx = {
            "revenue": revenue_30d(),        # aggregate in SQL
            "users": User.objects.count(),
            "recent_orders": list(Order.objects.order_by("-created_at")[:10].values(
                "pk", "number", "total", "status")),
        }
        cache.set("admin_dashboard_ctx", ctx, 300)   # 5 min TTL
    return ctx
```

Rules:
- SQL aggregation (`Sum/Count/TruncMonth`) over Python loops — always.
- List endpoints limited (`[:10]`) and `values()`/`values_list()` to skip model instantiation.
- Cache TTL 60–600s for stats dashboards; per-user dashboards need user-keyed cache or request-scoped compute.
- Chart data pre-aggregated server-side; never ship raw rows to JS for client-side aggregation.

## Anti-patterns

- Dashboard callback doing 1 query per KPI card with per-row Python aggregation → 500ms+ page.
- Unbounded tables ("recent activity" without slicing) — memory + render cost.
- Charts pulling year of raw rows → aggregate in SQL, ship labels+points only.
- Building dashboard as ModelAdmin of a fake model — use the documented override/callback path or custom page.
- Compiling dashboard Tailwind classes without a build step → unstyled pages in prod (see `unfold-tailwind`).

## Security

- Dashboard context renders for **every staff user** — scope data by role/tenant inside `build_dashboard_context`; cross-tenant numbers on a shared dashboard are a data leak.
- Cached contexts shared across users: cache global stats only, never per-user data, or key by user.

## Testing

```python
def test_dashboard_renders(admin_client, django_assert_num_queries):
    with django_assert_num_queries(15):
        res = admin_client.get("/admin/")
    assert "Revenue" in res.content.decode()
```

## Related skills

`unfold-components` (widgets), `unfold-tailwind` (styling pipeline), `unfold-custom-pages` (interactive dashboards), `unfold-performance`, `unfold-studio` (Studio dashboard templates → public equivalents).
