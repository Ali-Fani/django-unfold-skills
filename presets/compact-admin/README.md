# Preset: Compact Admin

Own conceptual preset (not an official Unfold/Studio preset). Dense, operator-focused.

- **Visual goal**: maximum information density; keyboard-first operations.
- **Intended for**: internal ops/tools, data teams, technical users.
- **Unfold config**:
  ```python
  UNFOLD = {
      "BORDER_RADIUS": "2px",
      "SHOW_VIEW_ON_SITE": False,      # reduce chrome
      "SHOW_HISTORY": False,
      "SIDEBAR": {"show_search": True, "show_all_applications": True},
  }
  # ModelAdmin: list_fullwidth = True, list_filter_sheet = False, list_per_page = 100
  # Huge tables: paginator = InfinitePaginator + show_full_result_count = False
  ```
- **Tailwind/CSS**: none required; optional tighter padding via compiled CSS on table cells (`py-1` equivalents) — version-sensitive, verify DOM.
- **Sidebar**: flat, all apps visible, collapsible groups; no decorative badges.
- **Density**: high — 100 rows/page, persistent filter sidebar.
- **Border radius**: 0–2px.
- **Color philosophy**: neutral base ramp; primary used sparingly (active states only).
- **Dashboard**: admin overview archetype (#5 in unfold-dashboard) — counts + quick links, no charts.
- **Accessibility**: verify table density keeps focus rings visible; keyboard nav (command palette `search_models` scoped list).
