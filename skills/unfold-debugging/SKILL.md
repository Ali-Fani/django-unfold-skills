---
name: unfold-debugging
description: Structured troubleshooting for Unfold — version check, symptom-to-cause table (unstyled pages, settings silently ignored, missing nav/tabs/filters/actions, custom page 404s, template errors, query explosions, pagination slowness), layer isolation procedure (minimal admin vs config vs production), and escalation channels. Use when any Unfold feature misbehaves, renders unstyled, doesn't appear, or when behavior differs from documentation.
---
# Verified against: django-unfold 0.104.1
# Docs: https://unfoldadmin.com/docs/
# Dependencies: unfold-core, unfold-installation. Related: unfold-tailwind, unfold-settings, unfold-performance.

# Debugging

## Purpose

Structured troubleshooting procedure for the most common Unfold failures. Work top-down: environment → wiring → config → template → data.

## Troubleshooting procedure

### Step 1 — Version & environment

```bash
pip show django-unfold          # version?
python -c "import django; print(django.get_version())"   # >= 5.2
```

Known breaking points: Tailwind v3 stylesheets vs Unfold ≥0.56.0 (v4); old snippets using removed settings. Check `docs/version-notes.md` and the changelog before deep-diving.

### Step 2 — Symptom → cause table

| Symptom | Likely cause | Fix |
|---|---|---|
| Whole admin unstyled | `"unfold"` after `django.contrib.admin` in INSTALLED_APPS; or missing `collectstatic` | Fix order; run collectstatic |
| Some models unstyled, others fine | Those admins inherit `django.contrib.admin.ModelAdmin` | Re-register with `unfold.admin.ModelAdmin` (check third-party admins too) |
| User/Group pages unstyled | Default UserAdmin/GroupAdmin still registered | Re-register per `unfold-installation` |
| Custom CSS/Tailwind classes dead | No build step, or `content` glob misses template dir, or Tailwind v3 config with v4 Unfold | `unfold-tailwind` pipeline |
| Settings ignored silently | Key typo / invented key | Compare against `unfold-settings` reference; unknown keys don't error |
| SIDEBAR/TABS not appearing | Sub-dict typo (`SIDEBAR` vs `SIDEBARS`); `TABS.models` name wrong (must be lowercase `app.model`); changeform tabs missing `"detail": True` | Fix key/model strings |
| Nav item missing | `permission` callback returns False; nav dict malformed | Check callback; log its return |
| Badge not showing | callback path wrong / returns non-int | Verify dotted path imports |
| Filter invisible | `unfold.contrib.filters` missing from INSTALLED_APPS, or wrong position (must follow `"unfold"`) | Fix INSTALLED_APPS |
| Text/numeric/date filter no effect | `list_filter_submit = True` missing | Add flag |
| Custom page 404 | `path()` appended before `super().get_urls()`? URL name collision; forgot `admin_view()` wrap | Use documented get_urls pattern (`unfold-custom-pages`) |
| Custom page blank/unstyled chrome | Template doesn't extend `admin/base_site.html`; mixin missing `title`/`permission_required` | Fix template + mixin attrs |
| Action button missing | Not registered in correct `actions_*` list; `has_{name}_permission` returns False; `permissions` list denies | Trace permission method |
| Dialog action submits but nothing happens | Missing `HX-Redirect` header in response | Return `HttpResponse(headers={"HX-Redirect": ...})` |
| Component tag error "unknown tag" | `{% load unfold %}` missing | Add load |
| Chart renders empty | `data` not JSON-encoded (`json.dumps`) or component_class name wrong | Check component class registration |
| Inline unstyled | Inline inherits Django's inline classes | Use `unfold.admin.TabularInline`/`StackedInline` |
| Query explosion after adding column | N+1 in display method | `unfold-performance` procedure |
| Pagination slow on huge table | COUNT query | `InfinitePaginator` + `show_full_result_count = False` |
| Wysiwyg/Array widget missing | `unfold.contrib.forms` not installed | Add to INSTALLED_APPS |
| Third-party admin ugly | Not re-registered | `unfold-integrations` pattern |

### Step 3 — Isolate the layer

1. Does it fail with **all custom code removed** (minimal admin + Unfold)? → Unfold bug/version issue → check GitHub issues.
2. Fails only with your settings? → config error (Step 2 table).
3. Fails only in production? → static files (`collectstatic`), compiled CSS missing, cache.
4. Fails only for some users? → permissions/callback logic.

### Step 4 — Template errors

- `TemplateSyntaxError: Invalid filter/unknown tag` → missing `{% load unfold %}` or wrong tag name.
- `TemplateDoesNotExist: unfold/...` → INSTALLED_APPS order/wrong contrib app.
- Override conflicts: project `templates/admin/...` shadowing Unfold templates — rename/remove stale overrides after upgrades.

### Step 5 — Escalation channels

- Docs: https://unfoldadmin.com/docs/
- GitHub issues: https://github.com/unfoldadmin/django-unfold/issues
- Demo source (working examples): https://github.com/unfoldadmin/formula
- Discord community (linked from docs).

## Anti-patterns

- Debugging by guessing settings keys — always re-check the reference.
- Mixing several changes at once — one change, one reload.
- Caching observed behavior across versions — Unfold moves fast; re-verify against installed version's source (`pip show -f django-unfold` to locate templates/tags).

## Related skills

`unfold-installation`, `unfold-tailwind`, `unfold-settings`, `unfold-performance`.
