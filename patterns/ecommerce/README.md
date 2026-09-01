# Pattern: E-commerce Admin

Orders, products, refunds, fulfillment ops.

## When
Ops team managing shop: order search/filter, refund tooling, stock checks, tabbed product forms.

## Reference implementation

```python
from django.contrib import admin
from django import forms
from django.db.models import Count, QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    ChoicesDropdownFilter, RangeDateTimeFilter, RangeNumericFilter,
    RelatedDropdownFilter, AutocompleteSelectMultipleFilter,
)
from unfold.decorators import action, display
from unfold.enums import ActionVariant
from unfold.forms import BaseDialogForm
from unfold.paginator import InfinitePaginator

from .models import Order, Product
from .services import order_refund


class RefundDialogForm(BaseDialogForm):
    reason = forms.ChoiceField(choices=[("damaged", "Damaged"), ("late", "Late delivery")])


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    # huge table → infinite pagination
    paginator = InfinitePaginator
    show_full_result_count = False

    search_fields = ["number", "customer__email"]
    list_display = ["number", "customer", "total", "status_badge",
                    "item_count", "placed_at"]
    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("placed_at", RangeDateTimeFilter),
        ("total", RangeNumericFilter),
        ("warehouse", RelatedDropdownFilter),
        ("tags", AutocompleteSelectMultipleFilter),
    )
    list_filter_submit = True
    ordering = ["-placed_at"]

    actions_list = ["refund_orders"]
    actions_list_hide_default = True

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super().get_queryset(request)
            .select_related("customer", "warehouse")
            .annotate(item_count=Count("items", distinct=True))
        )

    @display(description="Status", ordering="status", label={
        Order.Status.PENDING: "warning",
        Order.Status.PAID: "info",
        Order.Status.SHIPPED: "success",
        Order.Status.REFUNDED: "danger",
    })
    def status_badge(self, obj): return obj.get_status_display()

    @display(description="Items", ordering="item_count")
    def item_count(self, obj): return obj.item_count

    @action(description="Refund", variant=ActionVariant.DANGER,
            dialog={"title": "Refund orders", "form_class": RefundDialogForm})
    def refund_orders(self, request, form, queryset):
        order_refund([o.pk for o in queryset], reason=form.cleaned_data["reason"],
                     actor=request.user)
        return HttpResponse(headers={
            "HX-Redirect": reverse_lazy("admin:shop_order_changelist")})


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    search_fields = ["name", "sku"]
    autocomplete_fields = ["category", "related"]   # target admins need search_fields
    list_display = ["name", "sku", "stock", "price"]
    fieldsets = (
        (None, {"fields": [("name", "sku")]}),
        (_("Pricing"), {"classes": ["tab"], "fields": ["price", "tax_rate", "currency"]}),
        (_("Stock"), {"classes": ["tab"], "fields": ["stock", "warehouse", "low_stock_threshold"]}),
        (_("Media"), {"classes": ["tab"], "fields": ["image", "gallery"]}),
    )
    list_filter_sheet = False     # persistent filter sidebar for power users
```

## Rules
- Order tables grow unbounded: `InfinitePaginator` + indexed `placed_at` + ranged filters only (never AllValues filters).
- Refunds = money mutation: dialog with reason form, service call, transaction, audit.
- Product tabs for sectioned changeform; autocomplete for FKs.
- Warehouse pickers: RelatedDropdownFilter (few) or autocomplete (many).

## Dashboard
Ops overview via `unfold-dashboard` archetype #3: queue progress, incidents, revenue chart.

## Related
`patterns/crud-admin`, `unfold-filters`, `unfold-actions`, `unfold-performance`.
