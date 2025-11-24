# Feedback Loop Playbook

Use this loop to keep the project reviewed, documented, and shipped without drift.

## Step 1) Code review the project (exit when clean)
- Review the current branch/PR and scan the whole project (modules/toc, code, scripts, tests) for metadata, geometry, or logic regressions. Read the actual code and JSON content (not just diffs) to understand intent, catch context loss, and spot silent regressions. Anchor on best practices: understand intent, check correctness and edge cases, keep comments/ids clear, prefer small focused diffs, leave actionable concise feedback, and watch code coverage/critical paths when new logic lands.
- Check for a repo-local virtualenv (`venv/` or `.venv/`) and activate it before running tests; if absent, create one (`python3 -m venv venv`) and install pytest. If cadquery/trimesh are missing for the cadquerywrapper tests, run `bash scripts/install_cadquerywrapper_deps.sh` (rootless; uses `.venv` by default).
- Run validation from that environment (`TMPDIR=/tmp venv/bin/python -m pytest` on WSL/Linux or `.\\venv\\Scripts\\python -m pytest` on Windows) and capture any failures.
- Log the outcome in `CODE_REVIEW_JOURNAL.md` with verdict, tests, and follow-ups.
- If the review raises no issues and tests are green, exit the loop until new changes arrive.

## Step 2) Run the PR workflow
- When fixes or additions are needed, follow `PLAYBOOK_PR_WORKFLOW.md` to branch, push via the hook, update the PR, and merge via the hook when ready.
- Keep test results and the review feedback reflected in the PR description and journal entry.

## Step 3) Repeat
- After updates land (and merges complete), confirm tests are current if new changes were pulled, then return to Step 1 and re-review until Step 1 exits cleanly.
