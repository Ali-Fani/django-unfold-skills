# Unfold actions snippet bundle — django-unfold 0.104.x
# Doc: https://unfoldadmin.com/docs/actions/
from django import forms
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy

from unfold.admin import ModelAdmin
from unfold.decorators import action
from unfold.enums import ActionVariant
from unfold.forms import BaseDialogForm
from unfold.widgets import UnfoldAdminTextInputWidget, UnfoldAdminSplitDateTimeWidget

from .services import orders_cancel


# --- Global changelist action (bulk) ---
@admin.register(Order)
class OrderAdmin(ModelAdmin):
    actions_list = ["mark_paid", {
        "title": "Danger zone",           # dropdown group
        "icon": "warning",
        "items": ["cancel_orders"],
    }]
    actions_row = ["duplicate_row"]

    @action(description="Mark as paid", icon="paid")
    def mark_paid(self, request: HttpRequest, queryset: QuerySet):
        from .services import orders_mark_paid
        orders_mark_paid([o.pk for o in queryset], actor=request.user)
        messages.success(request, "Orders marked as paid.")
        return redirect(reverse_lazy("admin:shop_order_changelist"))

    # --- Confirmation dialog (destructive) ---
    @action(
        description="Cancel orders",
        variant=ActionVariant.DANGER,
        dialog={
            "title": "Cancel orders",
            "description": "This cannot be undone.",
            "submit_text": "Cancel",
        },
    )
    def cancel_orders(self, request: HttpRequest, form):
        orders_cancel(request.POST.getlist("_selected_action"), actor=request.user)
        # Dialog handlers MUST return HX-Redirect (HTMX):
        return HttpResponse(headers={
            "HX-Redirect": reverse_lazy("admin:shop_order_changelist")
        })

    # --- Row action ---
    @action(description="Duplicate", url_path="duplicate")
    def duplicate_row(self, request: HttpRequest, object_id: int):
        obj = self.get_object(request, object_id)
        obj.pk = None
        obj.number = f"{obj.number}-copy"
        obj.save()
        return redirect(reverse_lazy("admin:shop_order_changelist"))

    def has_changelist_row_action_permission(self, request: HttpRequest) -> bool:
        # NOTE: no object_id available here (documented) — per-object checks in handler.
        return request.user.has_perm("shop.change_order")


# --- Dialog with custom form ---
class RefundDialogForm(BaseDialogForm):     # MUST inherit BaseDialogForm
    reason = forms.CharField(widget=UnfoldAdminTextInputWidget)
    window = forms.SplitDateTimeField(widget=UnfoldAdminSplitDateTimeWidget)

    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)   # request auto-available
        ...


@action(
    description="Refund",
    dialog={"title": "Refund", "form_class": RefundDialogForm},
)
def refund_action(self, request: HttpRequest, form):
    from .services import order_refund
    order_refund(form.cleaned_data, actor=request.user)   # request available in handler
    return HttpResponse(headers={
        "HX-Redirect": reverse_lazy("admin:shop_order_changelist")
    })


# --- Detail (changeform) action — register in actions_detail ---
class UserActionsMixin:
    actions_detail = ["block"]

    @action(description="Block", url_path="block", variant=ActionVariant.DANGER,
            permissions=["block"])
    def block(self, request: HttpRequest, object_id: int):
        from .services import user_block
        user_block(object_id, actor=request.user)
        return redirect(reverse_lazy("admin:auth_user_change", args=[object_id]))

    def has_block_permission(self, request: HttpRequest, obj=None) -> bool:
        return request.user.is_superuser


# --- Submit-line action (runs AFTER save) — register in actions_submit_line ---
class PublishActionsMixin:
    actions_submit_line = ["publish"]

    @action(description="Save & publish", permissions=["publish"])
    def publish(self, request: HttpRequest, obj):
        obj.status = "PUBLISHED"
        obj.save(update_fields=["status"])
