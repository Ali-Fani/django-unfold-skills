---
name: unfold-security
description: Treats the admin as a high-privilege surface — per-surface authorization matrix (model perms, get_queryset data boundary, action permissions, custom page permission_required, nav/tab callbacks being hide-only, command palette callback filtering, dashboard scoping), information disclosure (secrets in list_display, search leakage, DEBUG), uploads, and audit expectations. Use when writing any action/custom view/dashboard, when reviewing admin permissions, or when admin data must stay tenant/role-scoped.
---
# Verified against: django-unfold 0.104.1
# Docs: https://unfoldadmin.com/docs/ + Django admin docs
# Dependencies: unfold-core, unfold-custom-pages, unfold-actions. Related: unfold-production, unfold-navigation.

# Security

## Purpose

Treat the admin as a **high-privilege surface**. Unfold adds surfaces (actions, custom pages, dashboards, command palette) — each new surface needs explicit authorization.

## Threat model

- Staff ≠ trusted: low-privilege staff accounts exist (support, content editors); every feature must enforce *its* permission, not assume "they're in admin already".
- Admins are targets: object data, user PII, secrets in model fields.
- Multi-tenant risk: scoping bugs leak other tenants' data via search/filters/exports.

## Authorization rules

| Surface | Enforcement |
|---|---|
| Model CRUD | Django model perms (`has_*_permission`) [DJANGO] — default-correct, override carefully |
| Object-level visibility | `get_queryset` filtering — the data boundary [DJANGO] |
| Unfold actions | `permissions=[...]` + `has_{name}_permission`; **row-action permission has no object_id** (verified) — per-object checks go inside the handler |
| Custom pages | `UnfoldModelAdminViewMixin.permission_required` tuple; standalone pages need `staff_member_required` + manual checks |
| Nav items / tabs | `permission` callback hides links **only** — target must still enforce |
| Command palette results | `search_callback` must filter by user (documented requirement) |
| Dashboard | context builder must scope data by role/tenant |
| Exports/actions on queryset | they inherit `get_queryset` — good; never build fresh unscoped querysets in handlers |

```python
# get_queryset as data boundary [DJANGO]
def get_queryset(self, request):
    qs = super().get_queryset(request)          # keep base scoping
    if not request.user.is_superuser:
        qs = qs.filter(tenant=request.user.tenant)
    return qs
```

Rules:
- Permission methods fail **closed**: exceptions → False.
- Object-level perms (django-guardian) not automatic in custom code — check explicitly where used.

## Information disclosure

- `list_display`/`readonly_fields`/fieldsets render values to every user with view perm — never expose secrets (API keys, tokens, password hashes) even readonly. Remove from forms+lists; access via separate permissioned page.
- Search/filters/autocomplete leak existence: `search_fields` on email lets staff enumerate users. Scope `get_search_results` when needed.
- Admin search (`search_fields`) is logged in URL params — sensitive query terms land in browser history/proxy logs. Command palette `show_history` (localStorage) — same concern.
- Error pages/DEBUG: never production DEBUG=True; admin error pages leak stack/config.

## Custom actions/views

- Handlers are plain views — validate object ownership/tenant before mutating.
- POST flows: CSRF automatic in admin forms; custom forms need `{% csrf_token %}` (`unfold-custom-pages`).
- Destructive actions: dialog confirmation + permission + transaction + idempotency + audit (`unfold-actions` checklist).

## File uploads

- Custom admin pages with uploads: validate content type/size, generate random filenames, restrict storage location, never serve uploads as `text/html` inline (XSS via uploaded SVG/HTML), virus-scan if feasible.

## Queryset customization

- Never `qs._result_cache` hacks or raw `.extra()` with user input (injection).
- Custom filter `queryset()` methods receive URL-controlled values — treat as untrusted; use ORM comparisons only.

## Environment visibility

- `ENVIRONMENT` label visible to all staff — label generically ("Production"), no hostnames/IPs.
- `SHOW_UI_WARNINGS` default False; enabling may surface config details.

## Audit

- Sensitive admin mutations (user role changes, deletes, permission grants, impersonation) → audit log: actor, action, object, timestamp, before/after where cheap. Implement in service layer called from actions/`save_model` (`unfold-production`).

## Testing

```python
def test_other_tenant_hidden(tenant_a_client, tenant_b_order):
    res = tenant_a_client.get("/admin/shop/order/")
    assert tenant_b_order.number not in res.content.decode()

def test_no_secret_in_changelist(admin_client, api_key_factory):
    res = admin_client.get("/admin/shop/webhook/")
    assert api_key_factory().key not in res.content.decode()
```

## Related skills

`unfold-production` (service layer + audit), `unfold-custom-pages`, `unfold-actions`, `unfold-navigation`.
