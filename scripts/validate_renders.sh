#!/usr/bin/env bash
set -euo pipefail

# Validate rendered SVG, PNG, and JPEG outputs for the arcade cabinet.
# Runs xmllint + optional svglint/svgo on SVGs, pngcheck on PNGs,
# and can regenerate PNGs for parity checking when VALIDATE_PARITY=1.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PY_BIN="${PY_BIN:-}"
if [[ -z "$PY_BIN" && -x ".venv/bin/python" ]]; then
  PY_BIN=".venv/bin/python"
elif [[ -z "$PY_BIN" ]]; then
  PY_BIN="python3"
fi

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

maybe_cmd() {
  command -v "$1" >/dev/null 2>&1
}

shopt -s nullglob
SVGS=(renders/*.svg)
PNGS=(renders/*.png)
JPGS=(renders/*.jpg)

if (( ${#SVGS[@]} == 0 )); then
  echo "No SVG files found in renders/; generate them first." >&2
  exit 1
fi
if (( ${#PNGS[@]} == 0 )); then
  echo "No PNG files found in renders/; generate them first." >&2
  exit 1
fi
if (( ${#JPGS[@]} == 0 )); then
  echo "No JPEG files found in renders/; generate them first." >&2
  exit 1
fi

echo "Checking SVG/PNG/JPEG pairs..."
missing_pairs=0
for svg in "${SVGS[@]}"; do
  base="${svg%.svg}"
  if [[ ! -f "${base}.png" ]]; then
    echo "Missing PNG for ${svg}" >&2
    missing_pairs=1
  fi
  if [[ ! -f "${base}.jpg" ]]; then
    echo "Missing JPEG for ${svg}" >&2
    missing_pairs=1
  fi
done
for jpg in "${JPGS[@]}"; do
  base="${jpg%.jpg}"
  if [[ ! -f "${base}.svg" ]]; then
    echo "Missing SVG for ${jpg}" >&2
    missing_pairs=1
  fi
done
if (( missing_pairs )); then
  exit 1
fi

require_cmd xmllint
require_cmd pngcheck

echo "Linting SVG syntax with xmllint..."
for svg in "${SVGS[@]}"; do
  xmllint --noout "$svg"
done

if maybe_cmd svglint; then
  echo "Running svglint across SVGs..."
  svglint "${SVGS[@]}"
else
  echo "svglint not found; skipping SVG structure lint."
fi

if maybe_cmd svgo; then
  if svgo --help 2>&1 | grep -q -- '--dry-run'; then
    echo "Running svgo dry-run lint..."
    svgo --dry-run "${SVGS[@]}" >/dev/null
  else
    echo "svgo found but --dry-run is unsupported; skipping svgo lint to avoid overwriting sources."
  fi
else
  echo "svgo not found; skipping svgo lint."
fi

echo "Checking PNG integrity with pngcheck..."
for png in "${PNGS[@]}"; do
  pngcheck -q "$png"
done

if maybe_cmd identify; then
  echo "Sample PNG dimensions (first five):"
  identify -format '%f: %wx%h\n' "${PNGS[@]}" | head -n 5
  echo "Sample JPEG dimensions (first five):"
  identify -format '%f: %wx%h\n' "${JPGS[@]}" | head -n 5
else
  echo "identify not found; skipping dimension summary."
fi

if [[ ${VALIDATE_PARITY:-0} == 1 ]]; then
  if maybe_cmd cairosvg && maybe_cmd compare; then
    echo "VALIDATE_PARITY=1 set; regenerating PNGs and comparing..."
    TMP_DIR="$(mktemp -d)"
    trap 'rm -rf "$TMP_DIR"' EXIT
    parity_failed=0
    for svg in "${SVGS[@]}"; do
      base="$(basename "$svg" .svg)"
      tmp_png="${TMP_DIR}/${base}.png"
      cairosvg "$svg" -o "$tmp_png"
      delta="$(compare -metric AE "$tmp_png" "renders/${base}.png" null: 2>&1 >/dev/null || true)"
      if [[ "$delta" != "0" ]]; then
        echo "PNG parity mismatch for ${base}.png (diff pixels: ${delta})" >&2
        parity_failed=1
      fi
    done
    if (( parity_failed )); then
      exit 1
    fi
  else
    echo "VALIDATE_PARITY=1 set but cairosvg/compare not found; skipping parity check."
  fi
fi

if command -v "$PY_BIN" >/dev/null 2>&1; then
  echo "Running pytest renders metadata checks..."
  "$PY_BIN" -m pytest --capture=no tests/test_renders.py
else
  echo "Python not found at ${PY_BIN}; skipping pytest run." >&2
  exit 1
fi

echo "Render validation completed successfully."
