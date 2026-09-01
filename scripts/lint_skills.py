import os
import re
import sys

MAX_DESC = 1024

root = "skills"
errors = []
count = 0

for d in sorted(os.listdir(root)):
    skill_md = os.path.join(root, d, "SKILL.md")
    if not os.path.isfile(skill_md):
        continue
    count += 1
    text = open(skill_md, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append(f"{skill_md}: no frontmatter")
        continue
    fm = m.group(1)
    nm = re.search(r"^name:\s*(\S+)\s*$", fm, re.M)
    if not nm:
        errors.append(f"{skill_md}: missing name")
    else:
        name = nm.group(1)
        if name != d:
            errors.append(f"{skill_md}: name '{name}' != dir '{d}'")
        if not re.fullmatch(r"[a-z0-9-]+", name):
            errors.append(f"{skill_md}: name not lowercase-hyphenated: {name}")
    dm = re.search(r"^description:\s*(.+)$", fm, re.M)
    if not dm:
        errors.append(f"{skill_md}: missing description")
    else:
        desc = dm.group(1).strip()
        if len(desc) > MAX_DESC:
            errors.append(f"{skill_md}: description {len(desc)} > {MAX_DESC} chars")
        if not re.search(r"[Uu]se when", desc):
            errors.append(f"{skill_md}: description missing 'Use when' trigger")
    for line in fm.splitlines():
        if line.strip() and not line.startswith((" ", "\t")):
            key = line.split(":", 1)[0].strip()
            if key not in ("name", "description"):
                errors.append(f"{skill_md}: non-standard frontmatter key '{key}'")

print(f"checked {count} skills")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print("ALL VALID")
