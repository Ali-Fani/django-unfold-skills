---
name: unfold-settings
description: Complete reference for the UNFOLD settings dictionary — site identity (SITE_TITLE/HEADER/LOGO/FAVICONS), UI toggles, environment label, login page, command palette, styles/scripts, dashboard callback. Use when changing admin branding/titles/logos, adding an environment badge, customizing the login page, or configuring global admin behavior.
---
# Verified against: django-unfold 0.104.1
# Docs: https://unfoldadmin.com/docs/configuration/settings/ , site-dropdown, command, avatar, paginator
# Dependencies: unfold-core, unfold-installation. Related: unfold-navigation, unfold-theming, unfold-dashboard, unfold-components.

# UNFOLD Settings Dictionary

## Purpose

Single source of truth for `UNFOLD = {...}` configuration. All keys below verified against current docs. Do not invent keys — unknown keys are ignored silently.

## Decision rules

- Global visual/branding → `UNFOLD` dict.
- Per-model behavior → ModelAdmin attributes (see `unfold-modeladmin`).
- Value that depends on request/user → callable/lazy (lambda), not constant.
- String settings that reference code (callbacks) use **dotted import paths**, e.g. `"app.module.func"`.
- Logo values use `lambda request: static("...")` so staticfiles works in production.

## Complete settings reference

### Site identity / branding

| Key | Type | Purpose |
|---|---|---|
| `SITE_TITLE` | str | Suffix in `<title>` tag |
| `SITE_HEADER` | str | Top text in sidebar |
| `SITE_SUBHEADER` | str | Text under `SITE_HEADER` |
| `SITE_VERSION` | str | Version shown near header |
| `SITE_SYMBOL` | str | Material Symbol name shown when no logo |
| `SITE_URL` | str | Link target of the header logo/title |
| `SITE_LOGO` | callable or dict | Sidebar logo; `{"light": fn, "dark": fn}` for theme variants; optimize for 32px height |
| `SITE_ICON` | callable or dict | Small icon variant of logo; same dict form |
| `SITE_FAVICONS` | list[dict] | Favicons: `{"rel", "sizes", "type", "href"}` dicts |
| `SITE_DROPDOWN` | list[dict] | Menu under site header: `{"icon", "title", "link", "attrs"}` |
| `SITE_VIEWS` | list[tuple] | Registered custom views for command palette: `("path", "name", "path.to.view")` |

```python
from django.templatetags.static import static
from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE": "Panel",
    "SITE_HEADER": "Acme Inc",
    "SITE_LOGO": {
        "light": lambda request: static("images/logo-light.svg"),
        "dark": lambda request: static("images/logo-dark.svg"),
    },
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "sizes": "32x32",
            "type": "image/svg+xml",
            "href": lambda request: static("favicon.svg"),
        },
    ],
    "SITE_DROPDOWN": [
        {
            "icon": "diamond",
            "title": "Website",
            "link": "https://example.com",
            "attrs": {"target": "_blank"},
        },
        {"icon": "dashboard", "title": "Admin", "link": reverse_lazy("admin:index")},
    ],
}
```

### UI toggles

| Key | Type | Default | Purpose |
|---|---|---|---|
| `SHOW_HISTORY` | bool | True | Show History button on changeform |
| `SHOW_VIEW_ON_SITE` | bool | True | Show "View on site" button |
| `SHOW_BACK_BUTTON` | bool | False | Back button on changeform header |
| `SHOW_UI_WARNINGS` | bool | False | Show UI warnings |
| `THEME` | str | None | Force `"dark"` or `"light"` — **disables theme switcher** |
| `BORDER_RADIUS` | str | — | Global corner radius, e.g. `"6px"`; smaller for technical/compact UIs |

### Environment label

Header badge distinguishing environments — strongly recommended for production safety (prevents "oops, I deleted prod data" incidents):

```python
# settings.py
UNFOLD = {
    "ENVIRONMENT": "core.environment_callback",
    "ENVIRONMENT_TITLE_PREFIX": "core.env_prefix_callback",
}

# core.py
def environment_callback(request):
    return ["Production", "danger"]  # variants: info, danger, warning, success
```

### Styles & scripts (global)

```python
UNFOLD = {
    "STYLES": [lambda request: static("css/admin.css")],
    "SCRIPTS": [lambda request: static("js/admin.js")],
}
```

Use for global additions. Per-ModelAdmin styles/scripts: `ModelAdmin` also supports `styles`/`scripts` attributes (see unfold-modeladmin). Anything using custom Tailwind classes must be compiled — see `unfold-tailwind`.

### Login page

```python
UNFOLD = {
    "LOGIN": {
        "image": lambda request: static("images/login-bg.jpg"),
        "redirect_after": lambda request: reverse_lazy("admin:index"),
        "form": "app.forms.CustomLoginForm",  # inherit unfold.forms.AuthenticationForm
    },
}
```

### Command palette (cmd/ctrl+K)

```python
UNFOLD = {
    "COMMAND": {
        "search_models": True,          # or list/tuple: ["app_label.model"]  or dotted callback path
        "search_callback": "app.utils.search_callback",
        "show_history": False,         # localStorage-based history
    },
}
```

- `search_models=True` searches **all** registered admins with `search_fields` → DB-intensive. Prefer explicit model list.
- Custom callback returns `SearchResult(title=..., description=..., link=..., icon=...)` from `unfold.dataclasses` — permissions must be checked manually inside callback.
- `show_history` stores queries in browser localStorage — consider data sensitivity before enabling.

### Dashboard callback

```python
UNFOLD = {"DASHBOARD_CALLBACK": "app.views.dashboard_callback"}

# app/views.py
def dashboard_callback(request, context):
    context.update({"kpi": compute_kpi(request.user)})
    return context
```

Injects variables into `templates/admin/index.html` (overridden by project). See `unfold-dashboard`.

### Colors & theme

`COLORS` maps to Tailwind palette variables — full coverage in `unfold-theming`. Summary: `{"primary": {50..950}, "base": {50..950}, "font": {subtle-light, subtle-dark, default-light, default-dark, important-light, important-dark}}`.

## Verified defaults worth knowing

- `BORDER_RADIUS` unset → Unfold default rounded corners.
- `THEME` unset → light/dark switcher available to users; set → forced, switcher hidden.
- `SHOW_UI_WARNINGS` default False.

## Anti-patterns

- Inventing keys (e.g. `SIDEBAR_BACKGROUND`) — silent ignore, wasted time. Full sidebar config lives under `SIDEBAR` (see `unfold-navigation`).
- Using string paths where lambdas required (logo/favicon accept callables; nav `link` accepts `reverse_lazy`).
- Forgetting `lambda request:` in `STYLES`/`SITE_LOGO` — breaks when staticfiles storage differs per environment.
- Setting `THEME: "dark"` when users want choice — forcing removes switcher.
- Putting business logic in callbacks referenced from settings (import path must stay cheap at import time — use lazy evaluation inside the callback).

## Performance

- `SITE_LOGO`/`SITE_FAVICONS` lambdas run per request — keep them trivial (`static()` calls only).
- `ENVIRONMENT`/`DASHBOARD_CALLBACK` are dotted-path imported once; per-request work happens in the function — keep queries minimal or cache (see `unfold-performance`).

## Security

- `ENVIRONMENT` label: do NOT leak deployment details (hostnames, IPs) to low-privilege staff — label is rendered to every admin user.
- `COMMAND.search_callback`: custom results bypass admin permission filtering unless callback checks `request.user` itself (documented requirement).
- `LOGIN.redirect_after` is a lambda receiving request — validate role there if redirecting per-role.

## Testing

```python
def test_environment_label(admin_client):
    res = admin_client.get("/admin/")
    assert "Production" in res.content.decode()
```

## Related skills

`unfold-navigation` (SIDEBAR/TABS sub-dicts), `unfold-theming` (COLORS), `unfold-dashboard` (DASHBOARD_CALLBACK), `unfold-tailwind` (STYLES pipeline).
