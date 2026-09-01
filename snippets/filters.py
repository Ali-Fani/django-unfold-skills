# Unfold filters snippet bundle — requires "unfold.contrib.filters" in INSTALLED_APPS
# Doc: https://unfoldadmin.com/docs/filters/ — verified 0.104.x
from django.contrib import admin
from django.contrib.admin.filters import ChoicesFieldListFilter
from django.core.validators import EMPTY_VALUES
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    AutocompleteSelectFilter,          # FK single
    AutocompleteSelectMultipleFilter,  # M2M
    ChoicesDropdownFilter,             # choices single
    CheckboxFilter,                    # custom checkbox list
    DropdownFilter,                   # custom dropdown base
    FieldTextFilter,                   # text filter on model field
    MultipleChoicesDropdownFilter,
    MultipleDropdownFilter,
    MultipleRelatedDropdownFilter,
    RadioFilter,                       # custom radio list
    RangeDateFilter,
    RangeDateTimeFilter,
    RangeNumericFilter,
    RangeNumericListFilter,            # range over annotation (custom subclass)
    RelatedDropdownFilter,
    SingleNumericFilter,
    SliderNumericFilter,
    TextFilter,                        # custom text filter base
)


@admin.register(Order)
class OrderFiltersAdmin(ModelAdmin):
    list_filter_submit = True  # REQUIRED for input-based filters

    list_filter = (
        ("status", ChoicesDropdownFilter),
        ("customer", RelatedDropdownFilter),
        ("tags", AutocompleteSelectMultipleFilter),     # TagAdmin needs search_fields
        ("placed_at", RangeDateTimeFilter),
        ("total", RangeNumericFilter),
        ("number", FieldTextFilter),
    )

    list_filter_options = {
        "status": {"label": _("Status"), "horizontal": True},
    }


# --- Custom text filter ---
class EmailDomainFilter(TextFilter):
    title = _("Email domain")
    parameter_name = "email_domain"

    def queryset(self, request, queryset: QuerySet):
        if self.value() not in EMPTY_VALUES:
            return queryset.filter(email__endswith=self.value())
        return queryset


# --- Custom dropdown filter ---
class WarehouseFilter(DropdownFilter):
    title = _("Warehouse")
    parameter_name = "warehouse"

    def lookups(self, request, model_admin):
        return [["eu", "EU"], ["us", "US"]]

    def queryset(self, request, queryset: QuerySet):
        if self.value() not in EMPTY_VALUES:
            return queryset.filter(warehouse__code=self.value())
        return queryset


# --- Custom radio filter ---
class PaidFilter(RadioFilter):
    title = _("Payment state")
    parameter_name = "paid_state"

    def lookups(self, request, model_admin):
        return [["paid", _("Paid")], ["unpaid", _("Unpaid")]]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == "paid":
            return queryset.filter(paid_at__isnull=False)
        if self.value() == "unpaid":
            return queryset.filter(paid_at__isnull=True)
        return queryset


# --- Range over annotation ---
class ItemsCountFilter(RangeNumericListFilter):
    parameter_name = "items_count"
    title = _("Items")


class MerchantAdmin(ModelAdmin):
    list_filter = (ItemsCountFilter,)

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return super().get_queryset(request).annotate(
            items_count=Count("product", distinct=True)
        )


# --- Horizontal choices (Django filter class + horizontal attr) ---
class HorizontalStatusFilter(ChoicesFieldListFilter):
    horizontal = True
