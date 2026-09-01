---
name: unfold-production
description: Production architecture for admin codebases — ModelAdmin as thin HTTP/permissions layer over a service layer, transactions for multi-step mutations, background jobs for long operations, audit logging, idempotency guards, environment/deployment checklist (collectstatic, Tailwind build, ENVIRONMENT label, session hardening). Use when admin features touch money/state/permissions, when designing service layers, or when preparing an Unfold admin for production.
---
# Verified against: django-unfold 0.104.1
# Docs: https://unfoldadmin.com/docs/
# Dependencies: unfold-core, unfold-actions, unfold-security. Related: unfold-performance, unfold-testing.

# Production Architecture

## Purpose

Keep admin codebases maintainable at scale: where logic lives, transactions, background jobs, audit trails.

## Architecture rule

```
ModelAdmin (HTTP + permissions + display)
    ↓ calls
service layer (mutations, invariants, audit)
    ↓ uses
query/select functions (reporting, aggregates)
    ↓ talks to
models / domain logic
```

```python
# services.py — the pattern
from django.db import transaction

def orders_cancel(order_ids: list[int], *, actor) -> None:
    with transaction.atomic():
        orders = Order.objects.select_for_update().filter(pk__in=order_ids, status=Order.Status.OPEN)
        if orders.count() != len(order_ids):
            raise OrderStateError("Some orders not cancellable")     # idempotency guard
        orders.update(status=Order.Status.CANCELLED, cancelled_by=actor, cancelled_at=timezone.now())
        AuditLog.objects.bulk_create(
            AuditLog(actor=actor, target=o, action="order.cancel", payload={}) for o in orders
        )

# admin.py — thin
@action(description="Cancel selected", dialog={...})
def cancel_orders(self, request, form):
    orders_cancel(request.POST.getlist("_selected_action"), actor=request.user)
    return HttpResponse(headers={"HX-Redirect": reverse_lazy("admin:shop_order_changelist")})
```

Why:
- ModelAdmin stays a thin HTTP layer → testable actions without admin harness.
- Service is reused by views/actions/management commands.
- Invariants and audit live in one place — no "forgotten audit" path.

## Rules

1. **No significant business logic in ModelAdmin methods.** `save_model` override calling `self.do_complex_stuff()` → move to service; admin calls it.
2. **Complex reporting = query functions**, not ModelAdmin display methods: `reports/monthly_revenue(user)` used by admin views AND exports.
3. **No N+1** — `unfold-performance` procedure is part of definition-of-done.
4. **Dashboard callbacks** — bounded queries + cache; no dozens-of-queries callbacks.
5. **Permissions explicit** — never rely on hidden; custom surfaces enforce their own.
6. **No sensitive fields in forms/lists** — `unfold-security`.
7. **Transactions for multi-step mutations** — `transaction.atomic()` in service; actions stay lock-free (lock lives with data logic).
8. **Background jobs for long operations** (>1-2s or >100 objects):

```python
def export_orders(self, request, queryset):
    task = export_orders_task.delay([o.pk for o in queryset], actor_id=request.user.pk)
    messages.info(request, f"Export queued ({task.id}).")   # non-blocking
    return None   # standard action flow redirects
```

   - Status surface: dashboard card or a Job ModelAdmin (progress field) — never browser-spinning.
9. **Audit logging for sensitive actions** — record actor/action/object/timestamp in service layer (see pattern above); render as read-only ModelAdmin (see `patterns/audit-log`).
10. **Idempotency for destructive/billable ops** — state-machine guards (transition checks) prevent double-submit damage; re-clicking "cancel" on cancelled order is a no-op, not an error storm.

## Environment & deployment checklist

- [ ] `DEBUG=False`; `ALLOWED_HOSTS` set; admin behind HTTPS (admin cookies = session creds).
- [ ] `collectstatic` + compiled Tailwind in deploy pipeline.
- [ ] `ENVIRONMENT` label configured ("Production", danger) — operator safety.
- [ ] `SHOW_UI_WARNINGS` False.
- [ ] Command palette `search_models` scoped (not True) on big DBs.
- [ ] Dashboard cache warmed/keys set.
- [ ] Admin URLs optionally on subpath/separate domain (staff-only ingress, IP allowlist, VPN) — defense in depth.
- [ ] Session security: `SESSION_COOKIE_SECURE`, short admin sessions where compliance requires.

## Anti-patterns

- God ModelAdmin (40 methods, business rules inline) — untestable, upgrade-hostile.
- Copy-pasting action logic across admins — services shared instead.
- Synchronous bulk email/S3/report generation in action handler → request timeouts, retry storms. Queue it.
- Audit logging only in some paths (model `.save()` scattered) — single choke point in services.
- Per-request heavy nav badges (uncached counts) — see `unfold-navigation` performance.

## Testing

- Service tests: state transitions, idempotency (call twice → same state), audit rows created.
- Admin tests: action calls service with right args (`unittest.mock.patch`), permission denied paths.

```python
def test_cancel_idempotent(db, order):
    orders_cancel([order.pk], actor=user)
    with pytest.raises(OrderStateError):
        orders_cancel([order.pk], actor=user)   # second call rejected
```

## Related skills

`unfold-actions` (surfaces), `unfold-security`, `unfold-performance`, `unfold-testing`.
