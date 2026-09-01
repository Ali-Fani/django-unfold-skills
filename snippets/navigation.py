# Navigation snippet bundle — SIDEBAR, SITE_DROPDOWN, command palette (django-unfold 0.104.x)
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

UNFOLD = {
    "SIDEBAR": {
        "show_search": True,            # filter apps/models by name
        "show_all_applications": False,  # dropdown with all apps/models
        "navigation": [
            {
                "title": _("Overview"),
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",                     # Material Symbols name
                        "link": reverse_lazy("admin:index"),
                        "link_attrs": {"title": "Go to dashboard"},
                    },
                ],
            },
            {
                "title": _("Shop"),
                "separator": True,         # border above group
                "collapsible": True,       # collapse toggle
                "items": [
                    {
                        "title": _("Orders"),
                        "icon": "shopping_cart",
                        "link": reverse_lazy("admin:shop_order_changelist"),
                        "badge": "shop.open_orders_count",        # dotted path or lambda
                        "badge_variant": "danger",
                        "badge_style": "solid",
                        "badge_class": "ml-auto",
                        "permission": "shop.shop_permission_callback",
                    },
                    {
                        "title": _("Products"),
                        "icon": "inventory_2",
                        "link": reverse_lazy("admin:shop_product_changelist"),
                        "icon_template": "helpers/icon/custom.svg",  # custom SVG template (alternative to icon)
                    },
                ],
            },
        ],
    },
    "SITE_DROPDOWN": [
        {
            "icon": "diamond",
            "title": _("Website"),
            "link": "https://example.com",
            "attrs": {"target": "_blank"},
        },
    ],
    "SITE_VIEWS": [
        # makes custom views discoverable; verify exact tuple shape per current docs
        ("status/", "admin_status", "app.views.SystemStatusView"),
    ],
    "COMMAND": {
        # True = all admins with search_fields (DB-heavy). Prefer explicit list:
        "search_models": ["shop.order"],
        "search_callback": "app.utils.search_callback",
        "show_history": False,  # localStorage — mind sensitive query leakage
    },
}

# --- callbacks ---
def open_orders_count(request):
    from shop.models import Order
    return Order.objects.filter(status="open").count()   # keep indexed/cheap


def shop_permission_callback(request):
    return request.user.has_perm("shop.view_order")


# app/utils.py — custom command palette results
from unfold.dataclasses import SearchResult


def search_callback(request, search_term):
    if not request.user.has_perm("shop.view_order"):
        return []
    hits = Order.objects.filter(number__icontains=search_term)[:5]
    return [
        SearchResult(
            title=f"Order {h.number}",
            description=f"{h.total} €",
            link=f"/admin/shop/order/{h.pk}/change/",
            icon="receipt_long",
        )
        for h in hits
    ]


# models.py — avatar (rendered in header)
class User(AbstractUser):
    @property
    def avatar_url(self) -> str:
        return self.profile.avatar.url if self.profile.avatar else ""

    @property
    def avatar_badge_variant(self) -> str | None:
        return "primary"          # danger, warning, success, info, primary, default

    @property
    def avatar_badge_count(self) -> str | int | None:
        return self.notifications.unread().count()

    @property
    def avatar_badge_url(self) -> str | None:
        return "/admin/notifications/"
