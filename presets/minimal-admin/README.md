# Preset: Minimal Admin

Own conceptual preset (not official). Least chrome, single purpose.

- **Visual goal**: near-vanilla Unfold; only branding applied. Fast to ship.
- **Intended for**: MVPs, internal tools, small teams, minimal maintenance.
- **Unfold config**:
  ```python
  UNFOLD = {
      "SITE_TITLE": "Admin",
      "SITE_HEADER": "Project",
      "SITE_SYMBOL": "rocket_launch",
      "BORDER_RADIUS": "4px",
      "SHOW_HISTORY": True,
  }
  # No COLORS override — ship defaults.
  ```
- **Tailwind/CSS**: none.
- **Sidebar**: default auto-generated model list only; no custom navigation.
- **Density**: defaults (20–50 rows/page).
- **Border radius**: 4px default.
- **Color philosophy**: Unfold defaults.
- **Dashboard**: skip custom index; default admin landing.
- **Accessibility**: defaults already conformant; keep.
