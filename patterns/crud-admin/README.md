# Pattern: CRUD Admin

Standard model management with Unfold polish.

## When
Any model needing list/edit/create/delete with good UX: badges, search, filters, pagination.

## Reference implementation

```python
from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from unfold.admin import ModelAdmin, TabularInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RangeDateFilter
from unfold.decorators import display
from unfold.paginator import InfinitePaginator

from .models import Order, OrderItem


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    fields = ["product", "quantity", "unit_price"]


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    search_fields = ["number", "customer__email"]
    list_display = ["number", "customer_heading", "status_badge", "items_count", "placed_at"]
    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("placed_at", RangeDateFilter),
    )
    list_per_page = 50
    list_filter_submit = True
    warn_unsaved_form = True
    change_form_show_cancel_button = True
    inlines = [OrderItemInline]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super().get_queryset(request)
            .select_related("customer")
            .annotate(items_count=Count("items", distinct=True))
        )

    @display(header=True)
    def customer_heading(self, obj):
        return [obj.customer.get_full_name(), obj.customer.email, obj.customer.initials]

    @display(description="Status", ordering="status", label={
        Order.Status.OPEN: "info",
        Order.Status.PAID: "success",
        Order.Status.CANCELLED: "danger",
    })
    def status_badge(self, obj):
        return obj.status

    @display(description="Items", ordering="items_count")
    def items_count(self, obj):
        return obj.items_count
```

## Checklist
- [ ] Inherits `unfold.admin.ModelAdmin`
- [ ] No per-row queries (annotations/prefetch only)
- [ ] Status column uses `@display(label=...)`
- [ ] Filters: dropdown for enums, range for dates
- [ ] Huge table? → `InfinitePaginator` (`unfold-performance`)
- [ ] Destructive ops → dialog actions (`unfold-actions`)

## Related
`unfold-modeladmin`, `unfold-filters`, `unfold-actions`.
