# AGENTS.md

Guidance for agents working ON this skill suite (maintainers), not agents USING it.

## What this repo is

Agent skill suite for django-unfold (verified against 0.104.1). 22 skills in `skills/`, plus reference material: `patterns/`, `presets/`, `snippets/`, `docs/`.

## Invariants — do not break

1. **Skill format**: every `skills/*/SKILL.md` has frontmatter with ONLY `name` (matches dir, `[a-z0-9-]+`) and `description` (≤1024 chars, must contain "Use when"). No other frontmatter keys — loaders reject or ignore them. Extended metadata goes in `#` comments under the frontmatter.
2. **Anti-hallucination**: every config key, class, template path, signature must be verifiable against https://unfoldadmin.com/docs/ or the source (github.com/unfoldadmin/django-unfold). Unverifiable claims must carry `UNCERTAIN — verify against current docs`.
3. **Labels**: capabilities are tagged `[UNFOLD]` / `[DJANGO]` / `[CUSTOM]` / `[STUDIO]`. Never attribute Django features to Unfold or vice versa.
4. **No proprietary Studio code**: Studio capabilities are mapped to public-API strategies only.
5. **Snippets must stay valid Python**: `python -m py_compile snippets/*.py` must pass.
6. **Presets are ours**: `presets/` are our own conceptual presets — never call them official Studio presets.

## Commands

```bash
# validate skill frontmatter + snippet syntax
python scripts/lint_skills.py
python -m py_compile snippets/*.py
```

## Structure rules

- New skill: `skills/<kebab-name>/SKILL.md` + registration in README table + `docs/feature-matrix.md` + routing row in `docs/architecture.md`.
- New pattern/preset: README.md in its folder, labeled own-design if visual.
- Skill content sections: Purpose, Activation/Triggers (inside description), Decision Rules, API Reference, Canonical/Advanced Patterns, Anti-Patterns, Performance, Security, Testing, Related Skills.

## When Unfold releases a new version

Follow `docs/version-notes.md` changelog-watch procedure: check releases, diff settings docs, update `verified_against` fields, note breaking changes.
