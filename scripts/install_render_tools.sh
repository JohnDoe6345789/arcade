#!/usr/bin/env bash
set -euo pipefail

# Helper to install render/validation dependencies on Debian/Ubuntu (incl. WSL).
# Modes:
# 1) Default system install (uses sudo apt-get install).
# 2) Fakeroot install (set FAKEROOT=/path): downloads .deb files into .cache/fakeroot-apt
#    and extracts them under FAKEROOT with dpkg -x (no sudo). Apt lists/cache are kept
#    inside the repo so system state stays untouched.
# Installs:
# - apt packages: pngcheck, ImageMagick (identify/compare), xmllint, Inkscape (skip via INSTALL_INKSCAPE=0)
# - npm: svgo, svglint (global or --prefix with FAKEROOT)
# - Python: cairosvg (prefers .venv if present)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

APT_PACKAGES=(pngcheck imagemagick libxml2-utils)
if [[ ${INSTALL_INKSCAPE:-1} == 1 ]]; then
  APT_PACKAGES+=(inkscape)
fi
NPM_PACKAGES=(svgo svglint)
PY_PACKAGES=(cairosvg)

FAKEROOT="${FAKEROOT:-}"
USE_FAKEROOT=0
if [[ -n "$FAKEROOT" ]]; then
  USE_FAKEROOT=1
  mkdir -p "$FAKEROOT"
fi

FAKEROOT_APT="${FAKEROOT_APT:-$ROOT_DIR/.cache/fakeroot-apt}"
APT_STATE="$FAKEROOT_APT/state"
APT_CACHE="$FAKEROOT_APT/cache"
APT_LISTS="$APT_STATE/lists"

if (( USE_FAKEROOT )); then
  mkdir -p "$APT_STATE/partial" "$APT_LISTS/partial" "$APT_CACHE/archives/partial"
  touch "$APT_STATE/status"
  APT_GET_OPTS=(
    -o "Dir::State=$APT_STATE"
    -o "Dir::State::status=$APT_STATE/status"
    -o "Dir::State::lists=$APT_LISTS"
    -o "Dir::Cache=$APT_CACHE"
    -o "Dir::Cache::archives=$APT_CACHE/archives"
  )
  APT_CACHE_OPTS=(
    -o "Dir::State=$APT_STATE"
    -o "Dir::State::status=$APT_STATE/status"
    -o "Dir::State::lists=$APT_LISTS"
  )
else
  APT_GET_OPTS=()
  APT_CACHE_OPTS=()
fi

PY_BIN="${PY_BIN:-}"
if [[ -z "$PY_BIN" && -x ".venv/bin/python" ]]; then
  PY_BIN=".venv/bin/python"
elif [[ -z "$PY_BIN" ]]; then
  PY_BIN="python3"
fi

log() { printf '==> %s\n' "$*"; }

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This installer targets Debian/Ubuntu (including WSL). Install dependencies manually on other platforms."
  exit 1
fi

if [[ ${SKIP_APT_UPDATE:-0} != 1 ]]; then
  if (( USE_FAKEROOT )); then
    log "Updating apt lists in $FAKEROOT_APT (no sudo)"
    apt-get "${APT_GET_OPTS[@]}" update
  else
    log "Updating apt package lists"
    sudo apt-get update
  fi
fi

if (( USE_FAKEROOT )); then
  log "Downloading packages (and dependencies) into $FAKEROOT_APT"
  apt-get "${APT_GET_OPTS[@]}" install --download-only -y "${APT_PACKAGES[@]}"

  log "Extracting packages into $FAKEROOT"
  shopt -s nullglob
  for deb in "$APT_CACHE"/archives/*.deb; do
    dpkg -x "$deb" "$FAKEROOT"
  done
else
  log "Installing apt packages: ${APT_PACKAGES[*]}"
  sudo apt-get install -y "${APT_PACKAGES[@]}"
fi

if command -v npm >/dev/null 2>&1; then
  if (( USE_FAKEROOT )); then
    NPM_PREFIX="${NPM_PREFIX:-$FAKEROOT/usr/local}"
    mkdir -p "$NPM_PREFIX"
    log "Installing npm packages into $NPM_PREFIX: ${NPM_PACKAGES[*]}"
    npm install --prefix "$NPM_PREFIX" "${NPM_PACKAGES[@]}"
  else
    log "Installing global npm packages: ${NPM_PACKAGES[*]}"
    npm install -g "${NPM_PACKAGES[@]}"
  fi
else
  echo "npm not found; install Node.js to pick up svgo and svglint."
fi

if command -v "$PY_BIN" >/dev/null 2>&1; then
  log "Installing Python packages with ${PY_BIN}: ${PY_PACKAGES[*]}"
  "$PY_BIN" -m pip install --upgrade pip
  "$PY_BIN" -m pip install --upgrade "${PY_PACKAGES[@]}"
else
  echo "Python not found at ${PY_BIN}; install python3 or point PY_BIN to your interpreter."
fi

if (( USE_FAKEROOT )); then
  cat <<EOF

Fakeroot install completed in $FAKEROOT
Add these to your shell before running validation:
  export PATH="$FAKEROOT/usr/bin:$FAKEROOT/usr/local/bin:\$PATH"
  export LD_LIBRARY_PATH="$FAKEROOT/usr/lib/x86_64-linux-gnu:$FAKEROOT/lib/x86_64-linux-gnu:\$LD_LIBRARY_PATH"
EOF
fi
