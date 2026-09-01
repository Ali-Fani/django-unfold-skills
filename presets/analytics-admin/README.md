# Preset: Analytics Admin

Own conceptual preset (not official). Chart-forward data surface.

- **Visual goal**: dashboards first; charts and tables dominate; nav to reports.
- **Intended for**: analytics products, BI-lite backoffices, growth teams.
- **Unfold config**:
  ```python
  UNFOLD = {
      "BORDER_RADIUS": "6px",
      "THEME": None,                    # let users switch light/dark (charts adapt via CSS vars)
      "DASHBOARD_CALLBACK": "app.views.dashboard_callback",
      "SIDEBAR": {"navigation": [
          {"title": _("Insights"), "items": [
              {"title": _("Overview"), "icon": "monitoring", "link": reverse_lazy("admin:index")},
              {"title": _("Cohorts"), "icon": "grid_view", "link": reverse_lazy("admin:cohorts")},
          ]},
      ]},
  }
  ```
- **Tailwind/CSS**: compiled build required (dashboard templates use custom grid classes) — `unfold-tailwind` pipeline.
- **Sidebar**: minimal — dashboards + raw model admins under one group.
- **Density**: moderate; KPI cards sparse (≤4 top row).
- **Border radius**: 6–8px (friendly data look).
- **Color philosophy**: one strong primary; charts use primary ramp shades (`var(--color-primary-400/700)`); base stays neutral.
- **Dashboard**: archetype #4 (filters + KPI + charts + table) as custom page; index override for landing KPIs.
- **Accessibility**: chart data available as table alternative (or `aria` labels); color not sole channel (labels on datasets).
- **Performance**: cached aggregates mandatory (`unfold-dashboard` rules); query ceiling tests.
