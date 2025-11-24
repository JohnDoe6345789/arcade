# Repository Guidelines

## Project Structure & Module Organization
- Source assets live in `modules/` as standalone JSON exports of individual SVG nodes (panels, isometric diagrams, hardware cut-outs).
- The catalog lives in `toc.json`, linking each module id, role, category, and tag for quick lookup.
- Tests reside in `tests/`, currently `tests/test_modules.py`, and assume a Python environment with access to the JSON modules.

## Build, Test, and Development Commands
- Prepare a virtual environment: `python -m venv .venv && .\.venv\Scripts\activate`.
- Install test tooling (pytest is the only dependency): `python -m pip install pytest`.
- Run the suite: `python -m pytest` (validates TOC coverage, SVG attribute presence, hole layouts, and identifier quality).
- Quick module peek without loading everything: `jq '{tag, id, attrib: .attrib | {class, transform}}' modules/<module>.json`.

## Coding Style & Naming Conventions
- JSON files should remain human-readable: 2-space indentation, stable key ordering when practical, and lowercase snake_case identifiers.
- SVG-derived `id` values must be expressive (avoid defaults like `circle2`); prefer tokenized names such as `case_back_panel_usb_port`.
- Preserve `attrib` richness: include `id`, `descriptionVerbose`, `notes`, and any transforms or dimensions carried from the SVG.
- When adding modules, mirror the existing field names (`tag`, `id`, `attrib`, `children`) so tests and consumers remain stable.

## Testing Guidelines
- Tests rely on Pytest; keep new checks colocated in `tests/` with descriptive function names (e.g., `test_<area>_<behavior>()`).
- Maintain geometric assertions for mechanical parts (hole spacing, cut-out sizes) and descriptive-id scoring for accessibility.
- Ensure `toc.json` entries map one-to-one with files in `modules/` and that every node exposes non-empty ids containing letters.

## Git Hook for Custom Branch PRs
- GitHub auto-PR workflow is removed; rely on the local hook to open PRs for `custom/*` branches.
- All pushes to branches matching `custom/*` must go through the local hook wrapper to auto-open a PR against `main`.
- Install the platform hook: copy `.github/hooks/pushpr-lin.sh` (Linux) or `.github/hooks/pushpr-win.ps1` (Windows) into `.git/hooks/` and make it executable.
- Add the alias for your platform:
  - Linux: `git config alias.pushpr-lin '!bash .git/hooks/pushpr-lin.sh'`
  - Windows: `git config alias.pushpr-win '!powershell -ExecutionPolicy Bypass -File .git/hooks/pushpr-win.ps1'`
- Use `git pushpr-lin` or `git pushpr-win` instead of `git push` for `custom/*`; bypassing this flow is not allowed.
- Keep `gh` authenticated; the hook will no-op on non-`custom/*` branches so standard pushes still work elsewhere.
- Optional auto-merge and branch cleanup: run the hook with `--auto-merge` (plus optional `--merge-method=merge|squash|rebase`) or set `PUSHPR_AUTO_MERGE=1` and `PUSHPR_MERGE_METHOD` to have it call `gh pr merge --auto --delete-branch` after creating/updating the PR.
- The hooks rely on `gh pr list` and `gh pr merge --auto`; `gh pr create` currently lacks `--json` output, so if the hook does not open a PR automatically, run `gh pr create --fill --title \"Auto PR for <branch>\"` yourself and then re-run the hook with `--auto-merge` (or call `gh pr merge --auto --delete-branch` manually).
- After the hook (or manual fallback) opens the PR, review the diff immediately and merge if everything looks good so `custom/*` branches do not linger.

## Commit & Pull Request Guidelines
- Commits: concise imperative subject (`Add bezel window check`), reference the affected module(s), and group related JSON changes together.
- Pull requests: summarize scope, list touched module ids, note any new geometric assumptions, and include `pytest` results.
- Attach before/after snippets or measurements when altering dimensions; link any discussion issues that motivated the change.
