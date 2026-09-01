# Per-Agent Installation Reference

This suite follows the open Agent Skills standard ([vercel-labs/skills](https://github.com/vercel-labs/skills)): `skills/<name>/SKILL.md` with `name` + `description` frontmatter. Anything that reads that layout can consume it.

## Recommended: skills CLI (universal)

The `skills` CLI ([skills.sh](https://skills.sh)) auto-detects installed agents and copies skills to each one's correct location.

```bash
npx skills add Ali-Fani/django-unfold-skills            # all 22 skills
npx skills add Ali-Fani/django-unfold-skills --skill unfold-modeladmin   # single skill
```

Interactive prompt lets you pick target agents (Claude Code, Cursor, Codex, Copilot, Windsurf, Gemini, Cline, OpenCode, Amp, Antigravity, Roo, Trae, VS Code, Zed, Goose, Droid, Kilo, Kiro CLI, ...).

Opt out of anonymous telemetry: `DISABLE_TELEMETRY=1 npx skills add ...`.

## Manual install per agent

### Claude Code

```bash
# all skills
git clone https://github.com/Ali-Fani/django-unfold-skills.git && cp -r django-unfold-skills/skills/* ~/.claude/skills/
# one skill
cp -r skills/unfold-modeladmin ~/.claude/skills/
```

Also works via [plugin marketplace](https://docs.claude.com/en/docs/claude-code/plugins): add this repo as a marketplace if you add a `.claude-plugin/marketplace.json` (optional, not included).

### OpenCode

OpenCode reads skills from its skill directories and has the `skill` tool for loading:

```bash
# user-level (available in all projects)
cp -r skills/* ~/.agents/skills/
# or, depending on your setup:
cp -r skills/* ~/.config/opencode/skill/

# project-level
mkdir -p .opencode/skill && cp -r skills/* .opencode/skill/
```

### Cursor

Cursor has no native skills loader; two options:

```bash
# rules files (recommended) — one file per skill
for d in skills/*/; do cp "$d/SKILL.md" ".cursor/rules/$(basename $d).md"; done

# or single legacy file
cat skills/*/SKILL.md > .cursorrules
```

### Codex / Copilot / Windsurf / Gemini / Cline / Amp / Roo / Trae / VS Code / Zed

```bash
npx skills add Ali-Fani/django-unfold-skills   # CLI handles each agent's path
```

Or copy `skills/<name>/` into the agent's documented skills/instructions directory — the CLI source ([github.com/vercel-labs/skills](https://github.com/vercel-labs/skills)) lists exact paths per agent.

### claude.ai (web)

Paste a SKILL.md into project knowledge, or upload the skill folder. Network-requiring skills need domains allowed in `claude.ai/settings/capabilities` (these skills are offline; no domains needed).

## Companion material (not installed by the CLI)

`patterns/`, `presets/`, `snippets/`, `docs/` are reference material, not skills. Two options:

1. **Keep the repo cloned** in a known location; skills reference paths like `patterns/crud-admin/README.md` — agent reads them from the clone.
2. **Vendor them into your project**: copy into `docs/unfold-skills/` inside your Django project so the agent finds them with the codebase.

```bash
git clone https://github.com/Ali-Fani/django-unfold-skills.git ~/unfold-skills
# point your agent at it, e.g. in AGENTS.md:
# "Unfold reference material lives at ~/unfold-skills (patterns/, presets/, snippets/, docs/)."
```

## Updating

Skills are plain files — re-run the install command to update. Verify the installed version against `docs/version-notes.md` (`verified_against: django-unfold 0.104.1`).
