---
name: unfold-navigation
description: Configures admin navigation — SIDEBAR groups with icons/badges/collapsible sections/permissions, SITE_DROPDOWN, SITE_VIEWS, command palette (cmd+K) with search_models/search_callback, and user avatar/badge via model properties. Use when customizing the sidebar menu, adding badges or permission-gated menu items, configuring the site dropdown, enabling admin search palette, or changing the header avatar.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/configuration/settings/ (SIDEBAR), site-dropdown, command, avatar
# Dependencies: unfold-core, unfold-settings. Related: unfold-tabs, unfold-custom-pages, unfold-security, unfold-theming.

# Sidebar Navigation, Site Dropdown, Command Palette, Avatar

## Purpose

Control admin navigation: sidebar groups/items (icons, badges, collapsible, separators, permissions), the site dropdown, top-level custom views, the cmd+K command palette, and the user avatar area.

## Decision rules

- Menu entry for an admin model → nav item with `reverse_lazy("admin:app_model_changelist")`.
- Menu entry for a custom page → nav item linking to custom view URL (see `unfold-custom-pages`).
- Live count on a menu entry → `badge` callback.
- Menu entry visible only to some roles → `permission` callback (string dotted path or lambda).
- Hierarchy of 2+ levels → nested navigation: recent Unfold versions support child `items` under an item; **UNCERTAIN for OSS in some versions — verify in current settings docs before using nested `items`; Studio documents it as guaranteed.** Fallback: collapsible groups (verified).
- Quick model search across admin → command palette, not sidebar clutter.
- Brand links (docs, website, status page) → `SITE_DROPDOWN`.

## Sidebar configuration [UNFOLD]

```python
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SIDEBAR": {
        "show_search": True,             # search box filtering apps/models
        "show_all_applications": False,  # dropdown listing all apps+models
        "navigation": [
            {
                "title": _("Analytics"),
                "separator": True,        # top border divider
                "collapsible": True,      # group collapses
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",          # Material Symbols name
                        "link": reverse_lazy("admin:index"),
                        "link_attrs": {"title": "Go to dashboard"},
                        "badge": "app.badge_callback",
                        "badge_variant": "danger",    # info, success, warning, primary, danger
                        "badge_style": "solid",
                        "badge_class": "ml-auto",
                        "permission": "app.dashboard_permission_callback",
                    },
                    {
                        "title": _("Users"),
                        "icon": "people",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                ],
            },
        ],
    },
}
```

Callback signatures (verified):

```python
def badge_callback(request) -> int: ...
def permission_callback(request) -> bool: ...
```

Icon source: Google Material Symbols (https://fonts.google.com/icons). Custom icon file: `icon_template` pointing to an SVG template.

## Site dropdown [UNFOLD]

```python
UNFOLD = {
    "SITE_DROPDOWN": [
        {"icon": "diamond", "title": _("Website"), "link": "https://example.com",
         "attrs": {"target": "_blank"}},
    ],
}
```

## Top-level custom views [UNFOLD]

`SITE_VIEWS` registers views for command-palette discoverability:

```python
UNFOLD = {
    "SITE_VIEWS": [
        ("some-path-to-view", "name_of_view_1", "path.to.view_itself_1"),
    ],
}
```

## Command palette [UNFOLD]

Activated by cmd+K / ctrl+K. Default: searches application and model names only.

```python
UNFOLD = {
    "COMMAND": {
        "search_models": True,                    # or ["app.model", ...] or dotted callback
        "search_callback": "app.utils.search_callback",
        "show_history": False,
    },
}
```

Custom results:

```python
# app/utils.py
from unfold.dataclasses import SearchResult

def search_callback(request, search_term):
    if not request.user.is_staff:
        return []
    return [
        SearchResult(
            title="Invoice #1042",
            description="Extra context",
            link="/admin/shop/invoice/1042/change/",
            icon="receipt_long",
        )
    ]
```

Rules:
- `search_models=True` queries **every** admin with `search_fields` — expensive on big DBs; prefer explicit model list or callback.
- Custom callback **must handle permissions itself** (documented).
- Infinite scrolling, page size 100.

## Avatar [UNFOLD]

Defined on the **user model** as properties (not settings):

```python
class User(AbstractUser):
    @property
    def avatar_url(self) -> str:
        return static("images/avatars/default.webp")

    @property
    def avatar_badge_variant(self) -> str | None:
        return "primary"    # danger, warning, success, info, primary, default

    @property
    def avatar_badge_count(self) -> str | int | None:
        return self.notifications.filter(read=False).count()

    @property
    def avatar_badge_url(self) -> str | None:
        return "/admin/notifications/"
```

Keep badge-count query cheap (cached or indexed); it renders in the header on every admin page.

## Anti-patterns

- Duplicating Django's auto model listing for every model in `navigation` — link only the primary surfaces; `show_all_applications` covers the long tail.
- Badge callbacks with unindexed count queries — rendered per request.
- `permission` lambdas with DB hits — run per request per item.
- Building a custom sidebar template before checking `SIDEBAR` config — most needs (icons, badges, collapsible, separators, search) are settings.
- Forcing users to memorize URLs — register important pages in command palette (`SITE_VIEWS` + search callback).

## Performance

- Badge/permission callbacks: memoize per request (`request` object caching), keep O(1) queries.
- Sidebar renders on every page — heavy callbacks multiply cost.

## Security

- `permission` callback is the **only** visibility control for nav items — hiding a link does NOT protect the target view. Custom view targets must enforce permissions themselves (`unfold-custom-pages`, `unfold-security`).
- Command search callback must filter by user access; leaking other users' object titles via palette is a real exfiltration path.

## Testing

```python
def test_nav_badge(admin_client):
    res = admin_client.get("/admin/")
    assert "3" in res.content.decode()  # badge value from callback

def test_nav_permission_hidden(client):
    assert not client2_sees_item  # low-priv user does not render restricted item
```

## Related skills

`unfold-settings` (parent dict), `unfold-tabs` (in-content tabs), `unfold-custom-pages` (nav targets), `unfold-security`.
