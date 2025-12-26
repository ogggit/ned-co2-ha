#!/usr/bin/env bash
set -euo pipefail

# Gebruik: ./publish_to_github.sh GITHUB_REPO_URL
# Voorbeeld: ./publish_to_github.sh git@github.com:org/ned-co2-ha.git

if [ $# -ne 1 ]; then
  echo "Gebruik: $0 <GITHUB_REPO_URL>"
  exit 1
fi

REPO_URL="$1"

if ! command -v git >/dev/null 2>&1; then
  echo "git is niet gevonden in PATH. Installeer git en probeer opnieuw." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

git init

echo "__pycache__/
*.pyc
*.pyo
*.egg-info/
.pytest_cache/
.cache/
.idea/
.vscode/
.DS_Store
" > .gitignore

git add .

git commit -m "Initial commit: NED CO2 Home Assistant custom integration"

git branch -M main

git remote add origin "$REPO_URL"

git push -u origin main

echo "Gedaan. Repo gepusht naar $REPO_URL"
