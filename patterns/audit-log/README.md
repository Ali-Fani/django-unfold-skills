# Pattern: Audit Log

Immutable action trail rendered read-only.

## When
Compliance, sensitive admin ops, security forensics. Pairs with service-layer writes (`unfold-production`).

## Reference implementation

```python
# models.py
from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                              on_delete=models.SET_NULL, related_name="+")
    action = models.CharField(max_length=128, db_index=True)
    target_type = models.ForeignKey(ContentType, null=True, on_delete=models.SET_NULL)
    target_id = models.CharField(max_length=64)
    target_repr = models.CharField(max_length=255)
    payload = models.JSONField(default=dict)

    class Meta:
        ordering = ["-created_at"]
        permissions = [("view_auditlog_report", "Can view audit reports")]
```

```python
# services.py — single choke point writes
from .models import AuditLog


def log_action(*, actor, target, action: str, payload: dict | None = None) -> None:
    AuditLog.objects.create(
        actor=actor,
        action=action,
        target_type=ContentType.objects.get_for_model(target),
        target_id=str(target.pk),
        target_repr=str(target)[:255],
        payload=payload or {},
    )
```

```python
# admin.py — read-only surface
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RangeDateTimeFilter, DropdownFilter
from unfold.decorators import display
from unfold.contrib.forms.widgets import ArrayWidget  # (not needed here) — keep only if used

@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ["created_at", "action_badge", "actor", "target_link"]
    list_filter = (
        ("action", DropdownFilter),
        ("created_at", RangeDateTimeFilter),
    )
    search_fields = ["target_repr", "actor__email"]
    list_filter_submit = True
    list_fullwidth = True
    list_per_page = 100

    # immutability:
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    readonly_fields = [f.name for f in AuditLog._meta.fields]  # JSONField renders pretty [UNFOLD]

    @display(description="Action", ordering="action", label=_action_labels)
    def action_badge(self, obj):
        return obj.action

    @display(description="Target", header=True)
    def target_link(self, obj):
        return [obj.target_repr, obj.action, None]
```

```python
# action labels for badges
_action_labels = {
    "user.block": "danger",
    "subscription.cancel": "warning",
    "order.refund": "warning",
    "settings.change": "info",
}
```

## Rules
- **Append-only**: staff get no add/change; deletes superuser-only (retention policy driven).
- Writes happen in services (`log_action(...)`) — never directly from ModelAdmin methods, so no path skips logging.
- Payload: before/after diffs for sensitive fields; never secrets.
- Performance: indexed `created_at`/`action`; RangeDateTimeFilter + dropdown keep lookups cheap; consider table partitioning at 10M+ rows.
- Retention: management command pruning old rows; audit tables grow unbounded otherwise.

## Related
`unfold-production`, `unfold-security`, `unfold-modeladmin`.
