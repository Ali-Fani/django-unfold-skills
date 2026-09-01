---
name: unfold-performance
description: Diagnoses and fixes slow admin pages — N+1 elimination (select_related/prefetch_related/annotate, the "500 queries" procedure), InfinitePaginator for huge tables (skips COUNT), search_fields indexing (trigram), filter cost, dashboard query budgets, and caching patterns. Use when an admin page is slow, when query counts explode with list_display methods, when a table has millions of rows, or when adding performance regression tests.
---
# Verified against: django-unfold 0.104.1
# Docs: /docs/configuration/paginator/ + general docs
# Dependencies: unfold-core, unfold-modeladmin. Related: unfold-production, unfold-dashboard, unfold-filters.

# Performance

## Purpose

Diagnose and fix slow admin pages. The dominant admin performance killer is N+1 queries from `list_display` methods; the second is expensive COUNT/pagination on huge tables; the third is dashboard query storms.

## N+1 in changelists (bad vs good)

```python
# BAD — obj.customer triggers 1 query per row × 100 rows/page
class OrderAdmin(ModelAdmin):
    list_display = ["number", "customer_name", "total_with_tax"]
    def customer_name(self, obj): return obj.customer.name        # 100 queries
    def total_with_tax(self, obj):
        return obj.total + sum(i.tax for i in obj.items.all())   # 200 more

# GOOD — 2-3 queries total
class OrderAdmin(ModelAdmin):
    list_display = ["number", "customer_name", "items_count"]

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related("customer")                       # FK join
            .prefetch_related("items")                        # M2M/reverse
            .annotate(items_count=Count("items", distinct=True))  # aggregate in SQL
        )

    def customer_name(self, obj): return obj.customer.name    # no query
    @display(description="Items", ordering="items_count")
    def items_count(self, obj): return obj.items_count        # no query
```

Diagnostic procedure for "500 queries":
1. Reproduce page with `django_assert_num_queries` / django-debug-toolbar / silk.
2. Count queries vs `list_per_page` — ratio ≈ per-row method count.
3. Grep each `list_display` method for related-object access (`obj.x.y`, loops).
4. Convert: FK access → `select_related`; reverse/M2M loops → `prefetch_related` (or annotation when only counting/aggregating); each `@display(ordering=...)` on computed value → annotation.
5. Re-measure; target ≤ ~10 queries per changelist page regardless of row count.

Rules:
- Annotation > prefetch when you only need counts/sums (`Count`, `Sum` — computed in DB).
- `select_related` for FK/OneToOne; `prefetch_related` for M2M/reverse FK/GenericFK.
- `distinct=True` on `Count` inside `annotate` when joining M2M (prevents row multiplication).
- Prefetched related managers are cached — safe for per-row display loops.
- `values()`/`values_list()` in display methods: no — breaks Unfold rendering helpers; annotate instead.

## Huge tables: COUNT + pagination

Standard Django changelist runs `COUNT(*)` for result count display — painful at millions of rows.

```python
from unfold.admin import ModelAdmin
from unfold.paginator import InfinitePaginator

class HugeTableAdmin(ModelAdmin):
    paginator = InfinitePaginator
    show_full_result_count = False   # required pairing
```

Verified behavior: no COUNT query, only Previous/Next, no page-count ceiling. Combine with sensible ordering (indexed column — avoid ordering on non-indexed field causing full scans).

Also: `list_select_related` [DJANGO] as tuple when every row needs the same FK.

## Search

- `search_fields = ["name"]` → `WHERE name ILIKE '%term%'` → no index usage on most DBs. Large tables: `istartswith` (`^name`) keeps index; Postgres trigram (pg_trgm + GIN) for contains-scale search.
- `autocomplete_fields` — each keystroke queries target admin's `search_fields`; keep target searchable fields narrow and indexed.
- Command palette `search_models=True` searches all admins — scope to a list.

## Filters

- Value-enumerating filters (AllValues, choices from DISTINCT) scan tables — prefer dropdown/autocomplete variants on big data (see `unfold-filters`).
- Ranged filters (date/numeric): index the filtered columns; ranges otherwise scan.

## Dashboard query storms

See `unfold-dashboard`: one context builder, SQL aggregation, `[:N]` slices, cache TTL 60–600s. Ceiling per dashboard page: ~15 queries.

## Caching

```python
from django.core.cache import cache

def get_admin_stats():
    stats = cache.get("admin_stats")
    if stats is None:
        stats = compute_stats()          # SQL aggregates
        cache.set("admin_stats", stats, 300)
    return stats
```

- Cache aggregates, not model instances, when used for display dicts.
- Per-user dashboards: user-keyed cache or skip caching for user-scoped numbers.

## Changeform

- Inlines: each inline = its own queryset + formset; paginate heavy ones (`per_page`), drop inline if 100+ rows (`unfold-inlines`).
- Datasets (`change_form_datasets`) render a full changelist on the changeform — cap `list_per_page` there.
- `readonly_preprocess_fields` running heavy transforms per render → precompute or cheap functions.

## Anti-patterns

- Per-row service/API calls in display methods (external HTTP) — hard timeout multiplier.
- `show_full_result_count = True` (default) on multi-million tables.
- `list_per_page = 200` "because users want" — paginate + filters instead.
- Annotations with `Count` missing `distinct` on M2M joins → inflated numbers + slower query.
- Sorting on Python-computed `@display` — impossible; sorting forces annotation path anyway.

## Testing

```python
@pytest.mark.django_db
def test_changelist_queries(admin_client, django_assert_num_queries):
    CustomerFactory()
    OrderFactory.create_batch(25)
    with django_assert_num_queries(8):    # fixed ceiling, fails on regressions
        admin_client.get("/admin/shop/order/")
```

## Related skills

`unfold-modeladmin` (queryset mechanics), `unfold-dashboard`, `unfold-filters`, `unfold-production` (service/reporting layer).
