#!/usr/bin/env bash
set -euo pipefail

remote="${1:-origin}"
branch="$(git rev-parse --abbrev-ref HEAD)"

[[ "${branch}" == custom/* ]] || exit 0

git push "${remote}" "${branch}"

if command -v gh >/dev/null 2>&1; then
  existing="$(gh pr list --head "${branch}" --state open --json number --jq 'length' 2>/dev/null || echo 0)"
  if [[ "${existing}" -eq 0 ]]; then
    gh pr create --head "${branch}" --base main --title "Auto PR for ${branch}" --fill || true
  fi
fi
