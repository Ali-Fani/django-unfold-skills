# Unfold ModelAdmin snippet bundle — django-unfold 0.104.x
from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from unfold.admin import ModelAdmin
from unfold.decorators import display


# --- 1. Minimal correct registration ---
@admin.register(MyModel)
class MyModelAdmin(ModelAdmin):
    list_display = ["name", "status"]
    search_fields = ["name"]


# --- 2. Badges, headers, sortable computed columns (no N+1) ---
class OrderAdminBase(ModelAdmin):
    list_display = ["number", "customer_heading", "status_badge", "items_count"]

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        return (
            super().get_queryset(request)
            .select_related("customer")
            .annotate(items_count=Count("items", distinct=True))
        )

    @display(header=True)
    def customer_heading(self, obj):
        return [
            obj.customer.get_full_name(),     # main line
            obj.customer.email,               # secondary line
            "AB",                             # initials (ignored if image dict passed as 4th)
        ]

    @display(description=_("Status"), ordering="status", label={
        "PAID": "success",
        "OPEN": "info",
        "CANCELLED": "danger",
    })
    def status_badge(self, obj):
        return obj.get_status_display()

    @display(description=_("Items"), ordering="items_count")
    def items_count(self, obj):
        return obj.items_count               # annotation — zero queries


# --- 3. Fieldsets with tabs ---
class ProductAdmin(ModelAdmin):
    fieldsets = (
        (None, {"fields": ["name", "sku"]}),
        (_("Pricing"), {"classes": ["tab"], "fields": ["price", "tax_rate"]}),
        (_("Inventory"), {"classes": ["tab"], "fields": ["stock", "warehouse"]}),
    )


# --- 4. Unfold-only useful flags ---
class FlagsAdmin(ModelAdmin):
    warn_unsaved_form = True
    change_form_show_cancel_button = True
    list_filter_submit = True        # required for text/numeric/date input filters
    list_fullwidth = False
    list_filter_sheet = True
    list_disable_select_all = False
    readonly_preprocess_fields = {"description": lambda c: c.strip()}
    change_form_before_template = "app/pre_form.html"
    change_form_after_template = "app/post_form.html"


# --- 5. Custom view on ModelAdmin (see unfold-custom-pages) ---
class WithPageAdmin(ModelAdmin):
    def get_urls(self):
        from django.urls import path
        from .views import ReportView  # UnfoldModelAdminViewMixin-based
        return super().get_urls() + [
            path("report/", self.admin_site.admin_view(
                ReportView.as_view(model_admin=self)), name="mymodel_report"),
        ]


# --- 6. Huge table pagination ---
from unfold.paginator import InfinitePaginator

class HugeAdmin(ModelAdmin):
    paginator = InfinitePaginator
    show_full_result_count = False
    ordering = ["-created_at"]       # indexed column


# --- 7. Expandable rows / datasets (see unfold-modeladmin) ---
from unfold.sections import TableSection

class ChildRowsSection(TableSection):
    verbose_name = _("Items")
    related_name = "items"
    fields = ["pk", "title"]

from unfold.datasets import BaseDataset


class ChildDatasetAdmin(ModelAdmin):      # regular ModelAdmin; list_filter NOT supported here
    search_fields = ["title"]
    list_display = ["title", "created_at"]
    list_per_page = 20

    def get_queryset(self, request: HttpRequest) -> QuerySet:
        qs = super().get_queryset(request)
        obj = self.extra_context.get("object") if self.extra_context else None
        if not obj:
            return qs.none()              # add view → empty dataset
        return qs.filter(parent__pk=obj.pk)


class RelatedDataset(BaseDataset):
    model = ChildModel
    model_admin = ChildDatasetAdmin
    tab = True                            # renders dataset as changeform tab

# Then on the parent admin: change_form_datasets = [RelatedDataset]
