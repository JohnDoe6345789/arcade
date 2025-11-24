"""Shared helper for printing third-party import hints."""

from __future__ import annotations

import sys


DEFAULT_WORKAROUND = (
    "Create a local venv (.venv preferred; try venv if that fails): "
    "python3 -m venv .venv && source .venv/bin/activate; then run "
    "'bash scripts/install_cadquerywrapper_deps.sh' or set USE_VENV=0 USE_USER=1 "
    "to install into the user site."
)


def print_import_advice(
    package: str, workaround: str | None = None, context: str | None = None
) -> None:
    """Print a friendly hint when a third-party dependency is missing."""
    parts = [f"[hint] Missing dependency '{package}'."]
    if context:
        parts.append(context)
    parts.append(f"Workaround: {workaround or DEFAULT_WORKAROUND}")
    print(" ".join(parts), file=sys.stderr)


__all__ = ["print_import_advice"]
