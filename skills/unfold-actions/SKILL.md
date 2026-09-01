---
name: unfold-actions
description: Unfold's four action surfaces — actions_list (changelist bulk), actions_row (per-row), actions_detail (changeform), actions_submit_line (save variants) — plus dialog confirmations, BaseDialogForm custom forms, full-page action forms, permissions, and a mandatory destructive-operations checklist (dialog + permission + transaction + idempotency + audit). Use when adding bulk or per-object operations, confirmation dialogs, or any dangerous admin action.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/actions/introduction/, dialog-actions, changelist, changelist-row, changeform, changeform-submitline, dropdown-actions, action-form-example, /docs/decorators/action/
# Dependencies: unfold-core, unfold-security. Related: unfold-modeladmin, unfold-production, unfold-testing.

# Actions

## Purpose

Unfold's four action surfaces plus dialogs/forms. Read Django's native action docs first — Unfold actions extend Django's.

## Action surface decision table

| Surface | Registration | Handler signature | Use for |
|---|---|---|---|
| Global (changelist top) | `actions_list = ["name"]` | `(self, request, queryset)` | Bulk ops on selected rows |
| Row (each changelist row) | `actions_row = ["name"]` | `(self, request, object_id)` | Per-object quick ops from list |
| Detail (changeform top) | `actions_detail = ["name"]` | `(self, request, object_id)` | Per-object ops from detail |
| Submit line | `actions_submit_line = ["name"]` | `(self, request, obj)` — runs **after save** | Save-variant buttons ("Save & Publish") |

Also verified:
- Dropdown grouping in `actions_list`: `{"title": ..., "icon": ..., "items": ["action1", "action2"]}`.
- `actions_list_hide_default = True` / `actions_detail_hide_default = True` hide built-in (Django/third-party) actions.
- `@action(description=..., icon="person", variant=ActionVariant.PRIMARY, url_path="...", attrs={"target": "_blank"}, permissions=[...])`.
- `ActionVariant` enum from `unfold.enums`: DEFAULT, PRIMARY, SUCCESS, INFO, WARNING, DANGER.
- All actions render as links to generated URLs; handlers are function-based views — return redirect when done.
- Permission method pattern: `has_{name}_permission(self, request, obj=None)`. Dotted built-in perms (`"auth.view_user"`) never receive the object instance.

## Canonical: global changelist action

```python
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from unfold.admin import ModelAdmin
from unfold.decorators import action

@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    actions_list = ["mark_paid"]

    @action(description="Mark as paid", icon="paid", permissions=["mark_paid"])
    def mark_paid(self, request: HttpRequest, queryset: QuerySet):
        from app.services import invoices_mark_paid
        invoices_mark_paid(queryset)     # service layer — see unfold-production
```

Django's classic `actions = [...]` list still works (renders in the legacy dropdown); prefer Unfold surfaces for visible buttons.

## Dialog confirmation (recommended for destructive ops) [UNFOLD]

```python
from django.http import HttpResponse
from django.urls import reverse_lazy
from unfold.admin import ModelAdmin
from unfold.decorators import action

class OrderAdmin(ModelAdmin):
    actions_list = ["cancel_orders"]
    actions_row = ["cancel_order"]

    @action(
        description="Cancel selected orders",
        variant=ActionVariant.DANGER,
        dialog={
            "title": "Cancel orders",
            "description": "This cannot be undone. Continue?",
            "submit_text": "Cancel orders",      # default "Submit"
        },
    )
    def cancel_orders(self, request, form):
        # form is a BaseDialogForm instance (empty unless form_class given)
        ids = request.POST.getlist("_selected_action")  # when triggered from changelist selection
        from app.services import orders_cancel
        orders_cancel(ids, actor=request.user)
        return HttpResponse(headers={"HX-Redirect": reverse_lazy("admin:shop_order_changelist")})

    @action(description="Cancel order", dialog={"title": "Cancel order"})
    def cancel_order(self, request, form, object_id):
        from app.services import order_cancel
        order_cancel(object_id, actor=request.user)
        return HttpResponse(headers={"HX-Redirect": reverse_lazy("admin:shop_order_changelist")})
```

Key verified detail: dialog handlers return `HttpResponse(headers={"HX-Redirect": ...})` — HTMX uses this header to redirect after the dialog closes.

### Dialog with custom form

```python
from django import forms
from unfold.forms import BaseDialogForm

class RefundForm(BaseDialogForm):                 # MUST inherit BaseDialogForm
    reason = forms.CharField(label="Reason")

    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)   # request auto-injected
        ...

    def clean_reason(self):
        value = self.cleaned_data["reason"]
        if not value:
            raise forms.ValidationError("Reason required.")
        return value

    # optional per-form templates:
    # form_before_template / form_after_template
    # get_before_template_context(request, object_id) / get_after_template_context(...)

@action(
    description="Refund",
    dialog={"title": "Refund order", "description": "Enter reason", "form_class": RefundForm},
)
def refund(self, request, form):
    process_refund(form.cleaned_data["reason"])
    return HttpResponse(headers={"HX-Redirect": reverse_lazy("admin:shop_order_changelist")})
```

## Row action

```python
actions_row = ["duplicate"]

@action(description="Duplicate", permissions=["duplicate"], url_path="duplicate")
def duplicate(self, request: HttpRequest, object_id: int):
    obj = self.get_object(request, object_id)     # [DJANGO] ModelAdmin helper
    obj.pk = None; obj.name = f"{obj.name} (copy)"; obj.save()
    return redirect(reverse_lazy("admin:shop_order_changelist"))

def has_changelist_row_action_permission(self, request: HttpRequest):
    # NOTE (verified): row-action permission callback does NOT receive object_id —
    # row-specific permission logic is impossible here; enforce per-object checks in handler.
    return True
```

## Changeform (detail) action

```python
actions_detail = ["block_user"]

@action(description="Block", url_path="block", permissions=["block_user"])
def block_user(self, request: HttpRequest, object_id: int):
    user = get_object_or_404(User, pk=object_id)
    user.is_active = False
    user.save()
    return redirect(reverse_lazy("admin:auth_user_change", args=(object_id,)))

def has_changeform_action_permission(self, request: HttpRequest, object_id):
    ...
```

## Submit-line action

```python
actions_submit_line = ["publish"]

@action(description="Save & publish", permissions=["publish"])
def publish(self, request: HttpRequest, obj):
    # Handler runs AFTER the instance is saved — modify + save explicitly if needed.
    obj.status = Status.PUBLISHED
    obj.save()
```

Permission hook: `has_changeform_submitline_action_permission(self, request, object_id)`.

## Action with full custom form page

For multi-field forms needing a full page (not dialog):

```python
@action(description="Import rates", url_path="import-rates")
def import_rates(self, request: HttpRequest, object_id: int):
    obj = get_object_or_404(RateCard, pk=object_id)
    form = RatesForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        process(obj, form.cleaned_data)
        messages.success(request, "Rates imported.")
        return redirect(reverse_lazy("admin:shop_ratecard_change", args=[object_id]))
    return render(request, "admin/rates_import.html", {
        "form": form, "object": obj,
        "title": "Import rates",
        **self.admin_site.each_context(request),   # keeps Unfold chrome
    })
```

Template must extend `admin/base_site.html`, include `{% csrf_token %}`, render fields via `{% include "unfold/helpers/field.html" with field=field %}`, and include `form.media` in `extrahead` when using date widgets (jQuery + DateTimeShortcuts JS required — see docs action-form-example).

## Destructive operations checklist (mandatory)

For any destructive/irreversible action:

1. **Confirmation** — use `dialog={...}`; never execute on plain click.
2. **Permission check** — `permissions=[...]` + `has_{name}_permission`; verify handler re-checks object-level rules (row permissions are global-only).
3. **Transaction** — wrap multi-row mutations in `transaction.atomic()` in the service layer.
4. **Idempotency** — repeated submits (double-click, HTMX retry) must not double-apply; guard on state transitions.
5. **Audit log** — record actor, object ids, timestamp for sensitive models (see `unfold-production`).
6. **Messaging** — `messages.success/error` so the user sees outcome after redirect.

## Anti-patterns

- Mutating rows directly in the handler body for complex flows — call a service function; keeps testability and reuse.
- Missing `HX-Redirect` in dialog handler → user stuck on blank/dialog page.
- Using `actions_row` for operations needing per-object permission → impossible in the permission callback; enforce in handler or use detail actions.
- Forgetting `url_path` when two actions share a Python name across admins (URL collisions).
- Relying on `attrs={"target": "_blank"}` for state changes → new-tab flows skip messages framework feedback.
- Hiding default actions (`actions_list_hide_default`) without re-implementing "Delete selected" — deletes become unreachable.

## Performance

- Global actions receive `queryset` of selected rows — batch with `queryset.update()` where safe, or chunked iteration for signals-heavy models.
- Dialog forms with heavy choices (e.g. all warehouses) → lazy queryset in form `__init__`.

## Security

- Handler is a plain view registered under admin URLs — Django admin auth applies, but **object-level** authorization is the handler's job.
- `permissions=["auth.view_user"]` style checks never see the object — do per-object checks manually (`obj.owner == request.user` etc.).
- CSRF: dialog/form actions go through Django's CSRF middleware automatically; custom action-form pages must include `{% csrf_token %}`.

## Testing

```python
def test_cancel_action(admin_client):
    order = OrderFactory(status=Order.Status.OPEN)
    url = reverse("admin:shop_order_changelist")
    res = admin_client.post(f"{url}action/cancel_orders/", data={...})
    order.refresh_from_db()
    assert order.status == Order.Status.CANCELLED

def test_action_permission_denied(non_staff_client):
    assert non_staff_client.get("/admin/shop/order/action/cancel_orders/").status_code == 403
```

## Related skills

`unfold-modeladmin` (registration home), `unfold-production` (service layer, transactions, audit), `unfold-security`, `unfold-testing`.
