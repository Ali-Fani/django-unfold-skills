# Unfold components snippet bundle — django-unfold 0.104.x
# All snippets use {% load unfold %} in templates. Components: https://unfoldadmin.com/docs/components/
import json

from unfold.components import BaseComponent, register_component


# --- Component class (data prep) ---
@register_component
class SignupChartComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "height": 320,
            "data": json.dumps({
                "labels": ["Mo", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                "datasets": [
                    {
                        "label": "Signups",
                        "data": [12, 19, 3, 5, 2, 3, 9],
                        "backgroundColor": "var(--color-primary-700)",  # theme-aware
                    },
                ],
            }),
            # "options": json.dumps({...})  # full Chart.js options override
        })
        return context


@register_component
class PlanDistributionTrackerComponent(BaseComponent):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "data": [
                {"label": "Free", "value": 420, "color": "var(--color-base-300)"},
                {"label": "Pro", "value": 180, "color": "var(--color-primary-500)"},
                {"label": "Enterprise", "value": 45, "color": "var(--color-primary-800)"},
            ],
            "size": "md",  # "md" | "sm"
        })
        return context


"""
---------- template usage (copy into .html) ----------
Requires: {% load i18n unfold %}

Card with title + action button + links:
  {% trans "Quick actions" as qa_title %}
  {% capture as qa_action silent %}
      {% component "unfold/components/button.html" with href="/admin/" variant="default" size="sm" %}
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

Chart inside card (component class mode):
  {% component "unfold/components/card.html" with title="Signups" %}
      {% component "unfold/components/chart/bar.html" with component_class="SignupChartComponent" %}{% endcomponent %}
  {% endcomponent %}

Table (data mode) - table dict: {"headers": [...], "rows": [[...], ...]}:
  {% component "unfold/components/card.html" with title="Top products" %}
      {% component "unfold/components/table.html" with table=table_data card_included=1 striped=1 %}{% endcomponent %}
  {% endcomponent %}

Progress:
  {% for item in queue %}
      {% component "unfold/components/progress.html" with title=item.title description=item.description value=item.value %}{% endcomponent %}
  {% endfor %}

Tracker / Cohort via component classes:
  {% component "unfold/components/tracker.html" with component_class="PlanDistributionTrackerComponent" %}{% endcomponent %}
  {% component "unfold/components/cohort.html" with component_class="MyCohortComponent" %}{% endcomponent %}

Layer (overlay content wrapper):
  {% component "unfold/components/layer.html" with component_class="SomeComponent" %}
      {% for item in some_variable %}{{ item.title }}{% endfor %}
  {% endcomponent %}

Tabs on custom pages:
  {% tab_list "custom_page" %}
"""

# Table component params (verified): table (dict, required), title, striped,
# card_included, height (max-height + scrollbar).

# Chart dataset options (verified): displayYAxis, maxTicksXLimit, suffixYAxis;
# global "options" JSON override.

# Rules:
# - Colors: always var(--color-*) so dark mode works.
# - Precompute data in views/callbacks; components only format.
# - Do not concatenate HTML strings in Python - pass dicts/lists.
