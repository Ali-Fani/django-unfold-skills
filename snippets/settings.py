# Verified UNFOLD settings template — django-unfold 0.104.x
# Doc: https://unfoldadmin.com/docs/configuration/settings/
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    # --- identity ---
    "SITE_TITLE": "Panel",
    "SITE_HEADER": "Acme Inc",
    "SITE_SUBHEADER": "Backoffice",
    "SITE_VERSION": "1.4.0",
    "SITE_SYMBOL": "speed",  # Material Symbol name
    "SITE_URL": "/",
    "SITE_LOGO": {
        "light": lambda request: static("img/logo-light.svg"),
        "dark": lambda request: static("img/logo-dark.svg"),
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
        {"icon": "diamond", "title": _("Website"),
         "link": "https://example.com", "attrs": {"target": "_blank"}},
        {"icon": "dashboard", "title": _("Admin"),
         "link": reverse_lazy("admin:index")},
    ],
    "SITE_VIEWS": [
        # ("path-to-view", "url-name", "path.to.ViewClass")
    ],

    # --- toggles ---
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": False,
    "SHOW_UI_WARNINGS": False,

    # --- theming ---
    "BORDER_RADIUS": "6px",
    "THEME": None,  # "dark" / "light" forces + disables switcher; None = switcher
    "COLORS": {
        # Values are CSS color strings — any format works; docs use oklch (Tailwind v4 palette).
        # Full 50–950 ramps REQUIRED for both palettes. Example ramps below (Tailwind v4 defaults):
        "base": {
            "50": "oklch(98.5% .002 247.839)",
            "100": "oklch(96.7% .003 264.542)",
            "200": "oklch(92.8% .006 264.531)",
            "300": "oklch(87.2% .01 258.338)",
            "400": "oklch(70.7% .022 261.325)",
            "500": "oklch(55.1% .027 264.364)",
            "600": "oklch(44.6% .03 256.802)",
            "700": "oklch(37.3% .034 259.733)",
            "800": "oklch(27.8% .033 256.848)",
            "900": "oklch(21% .034 264.665)",
            "950": "oklch(13% .028 261.692)",
        },
        "primary": {
            "50": "oklch(97.7% .014 308.299)",
            # ... full 50–950 ramp required ...
            "950": "oklch(29.1% .149 302.717)",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-600)",
            "default-dark": "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark": "var(--color-base-100)",
        },
    },

    # --- environment label ---
    "ENVIRONMENT": "core.environment_callback",

    # --- login ---
    "LOGIN": {
        "image": lambda request: static("img/login-bg.jpg"),
        "redirect_after": lambda request: reverse_lazy("admin:index"),
        # "form": "app.forms.CustomLoginForm",
    },

    # --- styles & scripts (global) ---
    "STYLES": [lambda request: static("css/admin.css")],
    "SCRIPTS": [lambda request: static("js/admin.js")],

    # --- sidebar ---
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Main"),
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                        "badge": "core.inbox_count",
                        "badge_variant": "danger",
                        "permission": lambda request: request.user.is_staff,
                    },
                ],
            },
        ],
    },

    # --- tabs (changelist / changeform / custom pages) ---
    "TABS": [
        {
            "models": [
                {"name": "shop.order", "detail": True},   # detail: True → changeform tabs too
            ],
            "items": [
                {"title": _("Orders"),
                 "link": reverse_lazy("admin:shop_order_changelist")},
            ],
        },
        # {"page": "custom_page", "items": [...]}   # + {% tab_list "custom_page" %}
    ],

    # --- command palette (cmd/ctrl+K) ---
    "COMMAND": {
        "search_models": ["shop.order"],   # True = all admins (expensive); list = scoped
        "search_callback": "core.search_callback",
        "show_history": False,
    },

    # --- dashboard ---
    "DASHBOARD_CALLBACK": "core.views.dashboard_callback",
}


# --- callbacks referenced above (dotted paths resolve to importable callables) ---
def environment_callback(request):
    return ["Production", "danger"]  # info, danger, warning, success


def inbox_count(request):
    from core.models import Ticket
    return Ticket.objects.filter(status="open").count()  # keep cheap/indexed


def search_callback(request, search_term):
    from unfold.dataclasses import SearchResult
    if not request.user.is_staff:
        return []
    return [SearchResult(title="...", description="...", link="...", icon="search")]
