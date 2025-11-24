# Branch and PR Playbook

Step-by-step flow to create branches, open PRs with the custom hook, handle reviews, and clean up.

## 1) Prepare
- Ensure `gh` is authenticated (`gh auth status`).
- Install the push hook: copy `.github/hooks/pushpr-lin.sh` or `.github/hooks/pushpr-win.ps1` into `.git/hooks/` and set the matching alias (`git config alias.pushpr-lin '!bash .git/hooks/pushpr-lin.sh'` or `git config alias.pushpr-win '!powershell -ExecutionPolicy Bypass -File .git/hooks/pushpr-win.ps1'`).
- Verify you are on `main` and up to date: `git switch main && git pull`.

## 2) Create a feature branch
- Name branches `custom/<topic>` (required for the hook): `git switch -c custom/<topic>`.
- Do the work; keep commits focused and messages imperative (e.g., `Add repo gitignore`).

## 3) Open/update the PR (hook-driven)
- From the feature branch, push via the hook (never raw `git push`): `git pushpr-lin` (Linux) or `git pushpr-win` (Windows).
- If the hook does not open a PR automatically, run `gh pr create --fill --title "Auto PR for <branch>"` then rerun the hook with `--auto-merge` or set `PUSHPR_AUTO_MERGE=1` and `PUSHPR_MERGE_METHOD=merge|squash|rebase`.
- After pushing, check the PR for the automated diff summary comment; if missing, rerun the hook or add a manual summary.

## 4) Respond to review
- Address feedback with additional commits on the same branch; repush via the hook to update the PR.
- Keep `CODE_REVIEW_JOURNAL.md` current (newest-first entries with date, branch, tests, verdict, follow-ups).
- If tests are required, run them locally and note results in the PR and journal.

## 5) Approve or request changes
- Reviewers record findings and verdict in the PR and journal entry.
- For approvals, ensure outstanding comments are resolved; for requested changes, iterate until all blockers clear.

## 6) Merge and clean up
- When ready, rerun the hook with auto-merge enabled (`git pushpr-lin --auto-merge` or `git pushpr-win --auto-merge`) or set env vars (`PUSHPR_AUTO_MERGE=1`, optional `PUSHPR_MERGE_METHOD`).
- Confirm `gh pr merge --auto --delete-branch` succeeded; if not, merge manually and delete the branch on GitHub.
- Locally: `git switch main && git pull && git branch -d custom/<topic>`.

## Quick checklist
- [ ] On `custom/<topic>` branch, up to date with `main`.
- [ ] Changes committed with clear messages.
- [ ] Tests run or explicitly noted.
- [ ] PR opened/updated via push hook; diff summary present.
- [ ] `CODE_REVIEW_JOURNAL.md` updated with verdict and follow-ups.
- [ ] Auto-merge (with delete) completed; local branch removed after pulling main.
