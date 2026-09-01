---
name: unfold-testing
description: Tests admin behavior — permission tests (the most valuable), action handler tests (row/detail/dialog URLs), filter tests via query params, custom page GET/POST tests, dashboard/query-count regression guards (django_assert_num_queries), and what NOT to test. Use when writing tests for ModelAdmins, actions, filters, or custom admin pages, or when locking in performance budgets.
---
# Verified against: django-unfold 0.104.1
# Docs: Django testing tools (pytest-django patterns)
# Dependencies: unfold-core. Related: unfold-actions, unfold-filters, unfold-custom-pages, unfold-performance.

# Testing

## Purpose

Test admin behavior: permissions, actions, filters, custom views, query counts. Unfold surfaces (row actions, dialogs, datasets) need specific techniques.

## Setup

```python
# pytest-django + admin client
@pytest.fixture
def admin_client(db, django_user_model):
    user = django_user_model.objects.create_superuser("a", "a@x.io", "p")
    client = Client()
    client.force_login(user)
    return client
```

`admin_client` builtin fixture exists in pytest-django but role-specific fixtures are better (superuser vs staff vs restricted).

## Permission tests (most valuable admin tests)

```python
def test_staff_cannot_change_pricing(limited_staff_client):
    res = limited_staff_client.get("/admin/shop/order/1/change/")
    # view allowed, save blocked:
    res2 = limited_staff_client.post("/admin/shop/order/1/change/", {...})
    assert res2.status_code == 403

def test_queryset_scoping(tenant_a_client, tenant_b_order):
    res = tenant_a_client.get("/admin/shop/order/")
    assert tenant_b_order.pk not in [o.pk for o in res.context["cl"].queryset]
```

`res.context["cl"]` (ChangeList) exposes the filtered queryset for assertions.

## Action tests

```python
def test_row_action(admin_client, order):
    url = f"/admin/shop/order/{order.pk}/changelist-row-action/cancel/"   # url_path given
    res = admin_client.post(url)
    order.refresh_from_db()
    assert order.status == Order.Status.CANCELLED
    assert res.status_code == 302

def test_bulk_action(admin_client):
    orders = OrderFactory.create_batch(3, status=Order.Status.OPEN)
    sel = [o.pk for o in orders]
    res = admin_client.post("/admin/shop/order/", data={"action": "mark_paid", "_selected_action": sel})
    assert Order.objects.filter(status=Order.Status.PAID).count() == 3

def test_dialog_action_permission(non_perm_client):
    res = non_perm_client.post("/admin/shop/order/action/cancel_orders/")
    assert res.status_code == 403
```

## Filter tests

```python
def test_range_date_filter(admin_client):
    OrderFactory(placed_at="2026-01-15 12:00")
    OrderFactory(placed_at="2026-03-15 12:00")
    res = admin_client.get("/admin/shop/order/", data={
        "placed_at__range__gte": "2026-01-01",
        "placed_at__range__lte": "2026-01-31",
    })
    assert res.context["cl"].queryset.count() == 1
```

## Custom page tests

```python
def test_custom_page_form(admin_client):
    res = admin_client.get("/admin/shop/order/report/")
    assert res.status_code == 200
    res = admin_client.post("/admin/shop/order/report/", {"frequency": "daily"})
    assert res.status_code == 302          # PRG pattern
```

## Query count tests (performance regression guards)

```python
@pytest.mark.django_db
def test_no_n_plus_one(admin_client, django_assert_num_queries):
    OrderFactory.create_batch(list_per_page_count)
    with django_assert_num_queries(8):
        admin_client.get("/admin/shop/order/")
```

Set explicit ceilings; the ceiling is the spec.

## Display decorator rendering

```python
def test_status_badge(admin_client, order):
    res = admin_client.get("/admin/shop/order/")
    assert res.content.decode().count("badge") >= 1
```

## What NOT to test

- Unfold's own rendering (their test suite covers it).
- Exact CSS/markup strings — brittle; test semantics (badge present, tab title present, result counts).
- Django's admin internals — test your configs/overrides.

## Anti-patterns

- Testing only superuser paths — restricted-role tests catch real bugs.
- Skipping POST tests (only GETs) — permission holes live in POST handlers.
- Not covering destructive actions (mock the service; assert it called with right ids and actor).
- Using `admin.E403` etc. admin checks only as proxy — real request tests better.

## Related skills

`unfold-actions`, `unfold-filters`, `unfold-custom-pages`, `unfold-performance`.
