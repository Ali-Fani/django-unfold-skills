# Django Unfold Agent Skill Suite

[![skills.sh](https://skills.sh/b/Ali-Fani/django-unfold-skills)](https://skills.sh/Ali-Fani/django-unfold-skills)

Agent-optimized knowledge and decision system for [django-unfold](https://unfoldadmin.com/), the Tailwind-based modern Django admin theme.

**This is not a documentation mirror.** It is an expert system that lets a coding agent behave like an experienced Django + Unfold engineer: know *which* mechanism to use, when configuration is enough vs. when a custom page/template/Tailwind override is required, and how the result scales in production.

- Verified against: **django-unfold 0.104.1** (current PyPI release, Sept 2026). Requires Python ≥3.12, Django ≥5.2.
- Primary sources: https://unfoldadmin.com/docs/ , https://unfoldadmin.com/studio/ , demo repo https://github.com/unfoldadmin/formula

---

## Install (works on every major agent)

Skills follow the open [Agent Skills](https://github.com/vercel-labs/skills) standard (`skills/<name>/SKILL.md` with `name` + `description` frontmatter). The universal installer detects your agents and copies skills to the right place:

```bash
npx skills add Ali-Fani/django-unfold-skills
```

Supported agents (auto-detected): Claude Code, Cursor, Codex, GitHub Copilot, Windsurf, Gemini CLI, Cline, Amp, Antigravity, OpenCode, Roo, Trae, VS Code, Zed, Goose, Droid, Kilo, Kiro CLI and more.

Install a single skill:

```bash
npx skills add Ali-Fani/django-unfold-skills --skill unfold-core
```

### Manual install (no CLI)

Copy the skill folders you want into your agent's skills directory:

| Agent | Destination |
|---|---|
| Claude Code | `~/.claude/skills/<skill-name>/` |
| OpenCode | `~/.config/opencode/skill/<skill-name>/` (or `~/.agents/skills/` — check your setup) |
| Cursor | copy `SKILL.md` into `.cursor/rules/<skill-name>.md` |
| Codex / others | see your agent's docs; any dir scanned for `SKILL.md` works |

```bash
# example: all skills for Claude Code
git clone https://github.com/Ali-Fani/django-unfold-skills.git
cp -r django-unfold-skills/skills/* ~/.claude/skills/

# example: single skill
cp -r django-unfold-skills/skills/unfold-modeladmin ~/.claude/skills/
```

### Minimal install (skills only)

The 22 skills in `skills/` are self-contained — an agent can operate with them alone. The companion material needs the full repo clone:

| Path | Needed when |
|---|---|
| `skills/` | always (installed by the CLI) |
| `docs/architecture.md` | routing decisions — the central decision table |
| `patterns/`, `presets/`, `snippets/` | larger implementations; copy-paste verified code |

If your agent installed only `skills/`, fetch the rest when a task references `patterns/...` or `snippets/...`:

```bash
npx degit Ali-Fani/django-unfold-skills/patterns patterns   # or clone the repo
```

---

## Repository layout

| Path | Contents |
|---|---|
| `skills/unfold-core/` | Mental model, layering rules (Django vs Unfold vs custom), routing to other skills. **Start here.** |
| `skills/unfold-installation/` | Quickstart, INSTALLED_APPS ordering, User/Group admin re-registration. |
| `skills/unfold-settings/` | Complete `UNFOLD = {...}` dictionary: branding, colors, sidebar, tabs, login, command palette, environment labels. |
| `skills/unfold-modeladmin/` | Deep `unfold.admin.ModelAdmin` coverage: displays, querysets, actions routing, sections, datasets, sortable changelist. |
| `skills/unfold-navigation/` | Sidebar navigation, badges, site dropdown, top tab bar, command palette, avatar. |
| `skills/unfold-tabs/` | Changelist/changeform tabs, fieldsets tabs, inline tabs, dynamic `tab_list`. |
| `skills/unfold-filters/` | All `unfold.contrib.filters` types + when to use Django vs Unfold vs custom. |
| `skills/unfold-actions/` | `actions_list/row/detail/submit_line`, dialogs, forms, permissions, destructive ops. |
| `skills/unfold-inlines/` | Tabular/Stacked/Generic/Nonrelated, sortable, paginated, nested, tabbed inlines. |
| `skills/unfold-fields/` | Widgets (Wysiwyg, Array), conditional fields, JSON, autocomplete, crispy forms. |
| `skills/unfold-components/` | Card/Table/Chart/Link/Button/Progress/Tracker/Cohort/Layer + `BaseComponent`. |
| `skills/unfold-dashboard/` | Dashboard design system: KPI, SaaS, operations, analytics, admin overview. |
| `skills/unfold-custom-pages/` | `UnfoldModelAdminViewMixin`, custom URLs, forms, POST handling. |
| `skills/unfold-theming/` | Colors, dark mode, border radius, forced themes, font tokens. |
| `skills/unfold-tailwind/` | Tailwind v4 pipeline, CSS variables, custom styles compilation. |
| `skills/unfold-integrations/` | 12 supported third-party packages + re-registration pattern. |
| `skills/unfold-performance/` | N+1, annotations, InfinitePaginator, search, dashboard queries. |
| `skills/unfold-security/` | Admin as high-privilege surface: permissions, custom views, data exposure. |
| `skills/unfold-debugging/` | Structured troubleshooting procedure. |
| `skills/unfold-testing/` | Testing admin behavior, actions, filters, custom views. |
| `skills/unfold-production/` | Service-layer architecture, transactions, background jobs, audit logging. |
| `skills/unfold-studio/` | Unfold Studio capability mapping → public implementation strategies. |
| `patterns/` | 8 full reference implementations (crud-admin, analytics-dashboard, saas-admin, user-management, audit-log, ecommerce, reporting, settings-page). |
| `presets/` | 5 conceptual theme presets (compact, minimal, enterprise, analytics, saas). |
| `snippets/` | Copy-paste verified code: settings, model_admin, dashboard, filters, actions, navigation, components. |
| `docs/architecture.md` | **Central decision system** + skill dependency graph. Agent routing table. |
| `docs/feature-matrix.md` | Feature inventory: official vs Studio vs custom, per-skill mapping. |
| `docs/version-notes.md` | Version compatibility, Tailwind v3→v4 breaking change, changelog watch. |
| `docs/agent-install.md` | Detailed per-agent installation reference. |

## How an agent should use this

1. Read `skills/unfold-core/SKILL.md` once per session for the mental model.
2. Route via `docs/architecture.md` decision tables ("user wants X → use Y").
3. Load only the skill(s) matching the current task (each skill `description` contains "Use when..." triggers — that's what your agent matches against).
4. Copy from `snippets/` rather than inventing code; adapt via `patterns/` for larger features.
5. Check `docs/version-notes.md` whenever behavior seems inconsistent — Unfold evolves fast.

## Skill format

Every `skills/*/SKILL.md` follows the Agent Skills standard: YAML frontmatter with only `name` (matches directory, lowercase-hyphenated) and `description` (what it does + "Use when..." triggers, ≤1024 chars — injected into the agent system prompt for routing). Extended metadata (verified version, docs, dependencies, related skills) lives in comments directly under the frontmatter, so any skills loader can consume the files.

## Labeling convention

Every technique is labeled one of:

- `[UNFOLD]` — official django-unfold API/setting (verified in current docs).
- `[DJANGO]` — standard Django admin functionality Unfold merely restyles.
- `[CUSTOM]` — project-level implementation (template override, Tailwind, service layer).
- `[STUDIO]` — capability of the paid Unfold Studio plugin; this suite provides public-API equivalents only, never Studio source.

## Anti-hallucination rule

All config keys, class names, template paths, and signatures in this suite were verified against official documentation and the django-unfold source for 0.104.x. Anything unverified is explicitly marked `UNCERTAIN — verify against current docs`. Agents must not invent settings; when in doubt, check https://unfoldadmin.com/docs/ or the source at https://github.com/unfoldadmin/django-unfold.
