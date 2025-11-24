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
- All pushes to branches matching `custom/*` must go through the local hook wrapper to auto-open a PR against `main`.
- Install `.git/hooks/push-pr.ps1` with executable bit and the following content:
  ```powershell
  #!/usr/bin/env pwsh
  $remote = if ($args.Length -ge 1) { $args[0] } else { "origin" }
  $branch = git rev-parse --abbrev-ref HEAD
  if ($branch -notlike "custom/*") { exit 0 }

  git push $remote $branch
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

  $existing = gh pr list --head $branch --state open --json number 2>$null | ConvertFrom-Json
  if ($existing.Count -gt 0) { exit 0 }

  gh pr create --head $branch --base main --title "Auto PR for $branch" --fill
  ```
- The script is checked in at `.github/hooks/push-pr.ps1`; copy it into `.git/hooks/push-pr.ps1` locally.
- Add the alias: `git config alias.pushpr '!powershell -ExecutionPolicy Bypass -File .git/hooks/push-pr.ps1'` (swap `powershell` for `pwsh` if you prefer Core).
- Use `git pushpr` instead of `git push` for `custom/*`; bypassing this flow is not allowed.
- Keep `gh` authenticated; the hook will no-op on non-`custom/*` branches so standard pushes still work elsewhere.

## Commit & Pull Request Guidelines
- Commits: concise imperative subject (`Add bezel window check`), reference the affected module(s), and group related JSON changes together.
- Pull requests: summarize scope, list touched module ids, note any new geometric assumptions, and include `pytest` results.
- Attach before/after snippets or measurements when altering dimensions; link any discussion issues that motivated the change.
