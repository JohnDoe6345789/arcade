#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: pushpr-lin.sh [remote] [--auto-merge] [--merge-method=<merge|squash|rebase>]
  remote          Remote to push to (default: origin)
  --auto-merge    Enable gh auto-merge with branch deletion for the PR
  --merge-method  Preferred merge method when setting auto-merge (default: repo/GitHub default)

You can also set:
  PUSHPR_AUTO_MERGE=1              # same as --auto-merge
  PUSHPR_MERGE_METHOD=<method>     # same as --merge-method
EOF
}

remote="origin"
auto_merge="${PUSHPR_AUTO_MERGE:-0}"
merge_method="${PUSHPR_MERGE_METHOD:-}"

while (($#)); do
  case "$1" in
    --auto-merge) auto_merge=1 ;;
    --merge-method=*) merge_method="${1#*=}" ;;
    -h|--help) usage; exit 0 ;;
    *) remote="$1" ;;
  esac
  shift
done
branch="$(git rev-parse --abbrev-ref HEAD)"

[[ "${branch}" == custom/* ]] || exit 0

git push "${remote}" "${branch}"

if command -v gh >/dev/null 2>&1; then
  pr_number="$(gh pr list --head "${branch}" --state open --json number --jq '.[0].number' 2>/dev/null || true)"
  if [[ -z "${pr_number}" ]]; then
    # gh pr create currently lacks --json support on some versions; fall back to parsing the URL.
    create_output="$(gh pr create --head "${branch}" --base main --title "Auto PR for ${branch}" --fill 2>/dev/null || true)"
    pr_number="$(printf '%s\n' "${create_output}" | grep -oE '/pull/[0-9]+' | tail -n1 | grep -oE '[0-9]+')"
  fi

  if [[ -n "${pr_number}" ]]; then
    diff_summary="$(gh pr diff "${pr_number}" --name-only 2>/dev/null || true)"
    if [[ -n "${diff_summary}" ]]; then
      comment_body="$(printf 'Automated diff summary from push hook:\n```\n%s\n```\n' "${diff_summary}")"
      gh pr comment "${pr_number}" --body "${comment_body}" 2>/dev/null || true
    fi
  fi

  if [[ -n "${pr_number}" && "${auto_merge}" -eq 1 ]]; then
    merge_flag=""
    case "${merge_method}" in
      merge|squash|rebase) merge_flag="--${merge_method}" ;;
    esac
    gh pr merge "${pr_number}" --auto --delete-branch ${merge_flag} 2>/dev/null || true
  fi
fi
