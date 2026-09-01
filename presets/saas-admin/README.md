# Preset: SaaS Admin

Own conceptual preset (not official). Customer-facing-adjacent backoffice polish.

- **Visual goal**: brand-matched, friendly; echoes product marketing colors.
- **Intended for**: SaaS ops, support, success teams.
- **Unfold config**:
  ```python
  UNFOLD = {
      "SITE_HEADER": "Acme Console",
      "SITE_LOGO": {"light": lambda r: static("img/logo-light.svg"),
                    "dark": lambda r: static("img/logo-dark.svg")},
      "BORDER_RADIUS": "8px",
      "COLORS": {...brand ramp...},          # snippets/settings.py
      "ENVIRONMENT": "core.environment_callback",
      "LOGIN": {"image": lambda r: static("img/login-bg.jpg")},
      "SIDEBAR": {"navigation": [
          {"title": _("Customers"), "icon": "group", "collapsible": True, "items": [
              {"title": _("Subscriptions"), "link": ..., "badge": "billing.overdue_count",
               "badge_variant": "danger"},
          ]},
      ]},
  }
  ```
- **Tailwind/CSS**: brand typography via compiled CSS if product font differs from Inter.
- **Sidebar**: task-oriented groups (Customers, Billing, People), live badges.
- **Density**: comfortable (25–50/page).
- **Border radius**: 8px.
- **Color philosophy**: brand primary on actions only; semantic colors for status (success/danger chips); base neutral.
- **Dashboard**: SaaS metrics (#2): MRR/ARR/churn KPIs, cohort chart, recent signups.
- **Accessibility**: brand colors must still pass AA on both themes — check contrast when converting marketing palette (marketing backgrounds often fail on admin surfaces).
- **Guardrails**: tenant scoping everywhere; impersonation superuser-only.
