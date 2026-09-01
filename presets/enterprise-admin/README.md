# Preset: Enterprise Admin

Own conceptual preset (not official). Governance-heavy, audit-first.

- **Visual goal**: conservative, structured; multi-section navigation; explicit state everywhere.
- **Intended for**: regulated industries, large orgs, multi-role staff.
- **Unfold config**:
  ```python
  UNFOLD = {
      "SITE_HEADER": "Acme Operations",
      "SITE_VERSION": __version__,
      "ENVIRONMENT": "core.environment_callback",       # mandatory here
      "SHOW_UI_WARNINGS": False,
      "BORDER_RADIUS": "4px",
      "COLORS": {...enterprise blue palette...},         # see snippets/settings.py
      "SIDEBAR": {"navigation": [
          {"title": _("Governance"), "separator": True, "collapsible": True, "items": [
              {"title": _("Audit log"), "icon": "history_edu", "link": ...,
               "permission": "governance.view_audit"},
          ]},
          {"title": _("Operations"), "collapsible": True, "items": [...]},
      ]},
  }
  ```
- **Tailwind/CSS**: none required.
- **Sidebar**: grouped by domain, collapsible, permission-gated entries.
- **Density**: moderate (25–50/page); audit views 100/page.
- **Border radius**: 4px.
- **Color philosophy**: blue/neutral base; danger accents only for destructive ops (dialogs mandatory).
- **Dashboard**: ops + governance overview (#3/#5 hybrid): system health, recent audit events, queue states.
- **Accessibility**: WCAG AA contrast both themes; ENVIRONMENT label always on; test with restricted-role fixtures.
- **Extras (not presets but required)**: audit logging (`patterns/audit-log`), object-level permissions where multi-tenant, session hardening (`unfold-production` checklist).
