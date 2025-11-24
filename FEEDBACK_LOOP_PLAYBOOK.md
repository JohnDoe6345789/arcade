# Feedback Loop Playbook

Use this loop to keep the project reviewed, documented, and shipped without drift.

## Step 1) Code review the project (exit when clean)
- Review the current branch/PR and scan the whole project (modules/toc, code, scripts, tests) for metadata, geometry, or logic regressions. Read the actual code and JSON content (not just diffs) to understand intent, catch context loss, and spot silent regressions. Anchor on best practices: understand intent, check correctness and edge cases, keep comments/ids clear, prefer small focused diffs, leave actionable concise feedback, and watch code coverage/critical paths when new logic lands.
- Run validation (prefer `python3 -m pytest` from a clean venv; on WSL set `TMPDIR=/tmp` to avoid capture temp-file issues) and capture any failures.
- Check whether a repo-local `venv/` exists so you activate the right environment before running tests.
- Log the outcome in `CODE_REVIEW_JOURNAL.md` with verdict, tests, and follow-ups.
- If the review raises no issues and tests are green, exit the loop until new changes arrive.

## Step 2) Run the PR workflow
- When fixes or additions are needed, follow `PLAYBOOK_PR_WORKFLOW.md` to branch, push via the hook, update the PR, and merge via the hook when ready.
- Keep test results and the review feedback reflected in the PR description and journal entry.

## Step 3) Repeat
- After updates land (and merges complete), confirm tests are current if new changes were pulled, then return to Step 1 and re-review until Step 1 exits cleanly.
