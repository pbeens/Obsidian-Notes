#!/usr/bin/env bash
set -euo pipefail

required_files=(
  README.md
  AGENTS.md
  tasks.md
  .gitignore
  LICENSE
  source/instructions.md
  source/references/README.md
  skill/obsidian-notes/SKILL.md
  skill/obsidian-notes/agents/openai.yaml
  skill/obsidian-notes/references/README.md
  scripts/build.py
)

for file in "${required_files[@]}"; do
  test -f "$file" || { echo "Missing required file: $file" >&2; exit 1; }
done

content_files=(README.md AGENTS.md tasks.md LICENSE source skill)
if rg -n --hidden '(OPENAI_API_KEY|sk-[A-Za-z0-9]{20,}|password\s*[:=]|Bearer\s+[A-Za-z0-9._-]{20,})' "${content_files[@]}"; then
  echo "Potential secret found; review the matching files before publication." >&2
  exit 1
fi

echo "Repository structure and sensitive-content checks passed."
