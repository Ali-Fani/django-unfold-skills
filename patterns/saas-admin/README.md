# Pattern: SaaS Admin

Multi-tenant SaaS backoffice: subscription CRUD, plan tracking, impersonation, tenant-scoped everything.

## When
Staff operating a SaaS: users, subscriptions, plan changes, refund tooling.

## Reference implementation

```python
# settings.py (excerpt)
UNFOLD = {
    "SITE_HEADER": "Acme Console",
    "ENVIRONMENT": "core.environment_callback",
    "SIDEBAR": {"navigation": [
        {"title": _("Billing"), "collapsible": True, "items": [
            {"title": _("Subscriptions"), "icon": "card_membership",
             "link": reverse_lazy("admin:billing_subscription_changelist"),
             "badge": "billing.overdue_count", "badge_variant": "danger"},
            {"title": _("Invoices"), "icon": "receipt_long",
             "link": reverse_lazy("admin:billing_invoice_changelist")},
        ]},
        {"title": _("People"), "collapsible": True, "items": [
            {"title": _("Users"), "icon": "people",
             "link": reverse_lazy("admin:accounts_user_changelist"),
             "permission": "accounts.user_tab_permission"},
        ]},
    ]},
}
```

```python
# billing/admin.py
from django.contrib import messages
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse_lazy

from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.enums import ActionVariant

from .models import Subscription
from .services import subscription_cancel, subscription_change_plan
from .forms import ChangePlanDialogForm


@admin.register(Subscription)
class SubscriptionAdmin(ModelAdmin):
    list_display = ["customer", "plan", "status", "mrr", "renews_at"]
    search_fields = ["customer__email"]
    readonly_fields = ["mrr", "provider_ref"]
    actions_list = ["cancel_subscriptions", "change_plan"]
    actions_list_hide_default = True

    @action(description="Cancel", variant=ActionVariant.DANGER,
            dialog={"title": "Cancel subscription",
                    "description": "Immediate cancellation, prorated refund issued."})
    def cancel_subscriptions(self, request: HttpRequest, queryset: QuerySet):
        subscription_cancel([s.pk for s in queryset], actor=request.user)
        messages.success(request, "Subscriptions cancelled.")
        return redirect(reverse_lazy("admin:billing_subscription_changelist"))

    @action(description="Change plan",
            dialog={"title": "Change plan", "form_class": ChangePlanDialogForm})
    def change_plan(self, request: HttpRequest, queryset: QuerySet):
        ...
```

```python
# billing/services.py — service layer with audit + idempotency
from django.db import transaction
from django.utils import timezone


@transaction.atomic
def subscription_cancel(ids: list[int], *, actor) -> None:
    subs = Subscription.objects.select_for_update().filter(
        pk__in=ids, status=Subscription.Status.ACTIVE
    )
    for s in subs:
        s.status = Subscription.Status.CANCELLED
        s.cancelled_at = timezone.now()
        s.save(update_fields=["status", "cancelled_at"])
        AuditLog.objects.create(actor=actor, target=s, action="subscription.cancel")
    refund.prorate(subs)
```

## Rules
- Tenant scoping in `get_queryset` (`unfold-security`) — every admin.
- Money mutations → service + transaction + audit (`unfold-production`).
- Dialogs on all irreversible ops.
- Sidebar badges = live queue counters (cached).
- Impersonation (django-hijack) → superuser-only + audited.

## Dashboard
SaaS metrics landing (MRR, churn, cohorts) via `unfold-dashboard` archetype #2; plan distribution via tracker component.

## Related
`patterns/user-management`, `unfold-navigation`, `unfold-actions`, `unfold-security`.
