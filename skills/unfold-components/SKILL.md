---
name: unfold-components
description: Unfold's reusable UI building blocks rendered via the {% component %} tag — card, table, chart (Chart.js), link, button, progress, tracker, cohort, layer — plus BaseComponent/register_component for data prep. Use when building dashboard or custom-page visuals, rendering KPI cards/charts/tables, registering custom components, or deciding whether an existing component fits.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/components/* (introduction, component-class, card, table, chart, link, button, progress, tracker, cohort, layer)
# Dependencies: unfold-core, unfold-installation. Related: unfold-dashboard, unfold-custom-pages, unfold-theming.

# Components

## Purpose

Unfold's reusable UI building blocks, rendered via the `{% component %}` tag, plus the `BaseComponent` class for data prep. Primary use: dashboards and custom pages. Charts are Chart.js-based; styling uses theme CSS variables.

## Decision rules

| Need                                         | Component                                                    |
| -------------------------------------------- | ------------------------------------------------------------ |
| Contained panel with title + optional action | `card.html`                                                  |
| Tabular data (headers+rows dict)             | `table.html`                                                 |
| Chart.js chart (bar/line/mixed)              | `chart/bar.html` + `BaseComponent` subclass providing `data` |
| KPI link / list of links                     | `link.html`                                                  |
| Primary/secondary action button              | `button.html`                                                |
| Percentage/meter display                     | `progress.html`                                              |
| Distribution across states (color strip)     | `tracker.html`                                               |
| Cohort retention grid                        | `cohort.html`                                                |
| Overlay/dropdown-ish content wrapper         | `layer.html`                                                 |

When NOT to use a component: one-off visual → plain HTML+Tailwind in the page template. Component exists → use it (consistency + theme integration).

## Component class pattern [UNFOLD]

```python
# components.py
import json
from unfold.components import BaseComponent, register_component

@register_component
class RevenueChartComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "height": 320,
            "data": json.dumps({
                "labels": ["Mo", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "datasets": [
                    {
                        "label": "Revenue",
                        "data": [12, 19, 3, 5, 2, 3, 9],
                        "backgroundColor": "var(--color-primary-700)",
                    },
                    {
                        "label": "Costs",
                        "data": [3, 12, 5, 9, 2, 19, 3],
                        "borderColor": "var(--color-primary-400)",
                        "type": "line",
                    },
                ],
            }),
            # optional: "options": json.dumps({...})  # full Chart.js options override
        })
        return context
```

Chart options (verified): `displayYAxis`, `maxTicksXLimit`, `suffixYAxis` on datasets.

## Template usage

```django
{% load unfold %}

{% component "unfold/components/card.html" with title="Revenue" %}
    {% component "unfold/components/chart/bar.html" with component_class="RevenueChartComponent" %}{% endcomponent %}
{% endcomponent %}
```

Two data modes for data-driven components (tracker, chart, cohort...):

- `component_class="X"` → component class computes context.
- `data=my_variable` → precomputed context variable passed directly.

## Card composition (title + action button + links)

```django
{% load i18n unfold %}

{% trans "Quick actions" as qa_title %}
{% capture as qa_action silent %}
    {% component "unfold/components/button.html" with href="#" variant="default" size="sm" %}
        {% trans "View more" %}
    {% endcomponent %}
{% endcapture %}

{% component "unfold/components/card.html" with title=qa_title action=qa_action title_class="!py-3" %}
    <div class="flex flex-col gap-5">
        {% component "unfold/components/link.html" with href="https://example.com" icon="start" external=1 %}
            {% trans "External docs" %}
        {% endcomponent %}
    </div>
{% endcomponent %}
```

## Table component

```django
{% component "unfold/components/table.html" with table=table_data card_included=1 striped=1 %}{% endcomponent %}
```

Verified params: `table` (dict with headers + rows; required), `title`, `striped`, `card_included`, `height` (max-height + scrollbar).

## Progress

```django
{% for item in queue %}
    {% component "unfold/components/progress.html" with title=item.title description=item.description value=item.value %}{% endcomponent %}
{% endfor %}
```

## Tracker / Cohort / Layer

```django
{% component "unfold/components/tracker.html" with component_class="MyTrackerComponent" %}{% endcomponent %}
{% component "unfold/components/cohort.html" with component_class="MyCohortComponent" %}{% endcomponent %}
{% component "unfold/components/layer.html" with component_class="SomeComponent" %}
    {% for item in some_variable %}{{ item.title }}{% endfor %}
{% endcomponent %}
```

Tracker context: `data` + optional `size` (`"md"`, `"sm"`).

## When to build a custom component

- Repeated data-prep + template pair across pages → `BaseComponent` subclass (registered) — reusable via `component_class`.
- One-off → inline HTML in page template.
- Forcing a card to behave like a modal, or table like a form → wrong; build custom.

## Anti-patterns

- Heavy queries inside `get_context_data` of many components on one dashboard — total queries multiply; batch per page in the view and pass via context, or cache (see `unfold-performance`).
- Hardcoded hex colors in chart datasets — breaks dark mode; use `var(--color-primary-700)` style variables.
- Building tables by concatenating HTML strings in Python — use the `table` dict.
- Forgetting `{% load unfold %}` — component tag silently unknown → TemplateSyntaxError (good) but often misdiagnosed as "component missing".

## Performance

- Each component = template render + its class queries. A dashboard with 8 components each doing 3 queries = 24 queries/page. Rule: view-level aggregation into context, or component-level caching with short TTL for stats.

## Security

- Component context values land in HTML — escape user-derived strings (Django autoescape handles; avoid `|safe`).
- Links rendered from DB (e.g. external URLs) — validate scheme (no `javascript:`).

## Testing

```python
def test_component_registered():
    from unfold.components import get_components  # verify presence in installed version
    # simpler: render the page containing the component and assert marker text
```

## Related skills

`unfold-dashboard` (composition patterns), `unfold-custom-pages` (hosting pages), `unfold-theming` (color variables).
