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

## Commit & Pull Request Guidelines
- Commits: concise imperative subject (`Add bezel window check`), reference the affected module(s), and group related JSON changes together.
- Pull requests: summarize scope, list touched module ids, note any new geometric assumptions, and include `pytest` results.
- Attach before/after snippets or measurements when altering dimensions; link any discussion issues that motivated the change.
