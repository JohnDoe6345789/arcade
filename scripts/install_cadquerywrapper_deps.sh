#!/usr/bin/env bash
set -euo pipefail

# Rootless installer for cadquerywrapper runtime (cadquery + trimesh).
# Defaults to using .venv; override USE_VENV=0 to reuse an existing interpreter.
# Optional flags:
#   INSTALL_DEV=1  install dev requirements (includes pytest)
#   VENV_PATH=/path/to/venv  choose a different venv path (when USE_VENV=1)
#   PY_BIN=python3.11        interpreter to use when USE_VENV=0
#   USE_USER=1               install with --user when USE_VENV=0

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REQ_FILE="$ROOT_DIR/cadquerywrapper/requirements.txt"
REQ_DEV_FILE="$ROOT_DIR/cadquerywrapper/requirements-dev.txt"

USE_VENV=${USE_VENV:-1}
INSTALL_DEV=${INSTALL_DEV:-0}
USE_USER=${USE_USER:-0}
VENV_PATH="${VENV_PATH:-$ROOT_DIR/.venv}"

log() { printf '==> %s\n' "$*"; }

if (( USE_VENV )); then
  if [[ ! -x "$VENV_PATH/bin/python" ]]; then
    log "Creating virtual environment at $VENV_PATH"
    python3 -m venv "$VENV_PATH"
  fi
  PY_BIN="$VENV_PATH/bin/python"
else
  PY_BIN="${PY_BIN:-python3}"
fi

if ! command -v "$PY_BIN" >/dev/null 2>&1; then
  echo "Python not found at $PY_BIN; set PY_BIN to a valid interpreter."
  exit 1
fi

PIP_FLAGS=()
if (( ! USE_VENV )) && (( USE_USER )); then
  PIP_FLAGS+=(--user)
fi

REQ_TO_INSTALL="$REQ_FILE"
if (( INSTALL_DEV )); then
  REQ_TO_INSTALL="$REQ_DEV_FILE"
fi

log "Upgrading pip with $PY_BIN"
"$PY_BIN" -m pip install --upgrade pip

log "Installing cadquerywrapper requirements from $(basename "$REQ_TO_INSTALL")"
"$PY_BIN" -m pip install "${PIP_FLAGS[@]}" -r "$REQ_TO_INSTALL"

if (( USE_VENV )); then
  cat <<EOF

Dependencies installed into $VENV_PATH
Activate with: source $VENV_PATH/bin/activate
Run tests: TMPDIR=/tmp $VENV_PATH/bin/python -m pytest
EOF
else
  if (( USE_USER )); then
    log "Installed with --user; ensure your PATH and PYTHONPATH include the user base"
  else
    log "Installed with $PY_BIN (no venv); ensure this interpreter is used when running tests"
  fi
fi
