#!/usr/bin/env python3
"""Render JSON-based SVG modules into standalone SVG (and optional PNG) files."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

DEFAULT_STYLE = """.panel { fill: none; stroke: #111; stroke-width: 1; }
.label { font-family: Arial, sans-serif; font-size: 16px; }
.dim { font-family: Arial, sans-serif; font-size: 14px; font-style: italic; }
.title { font-family: Arial, sans-serif; font-size: 22px; font-weight: bold; }
"""


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--modules",
        type=Path,
        default=repo_root / "modules",
        help="Directory containing JSON modules exported from the SVG drawing.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=repo_root / "renders",
        help="Directory to write rendered SVG (and PNG) files into.",
    )
    parser.add_argument(
        "--style-module",
        default="style1",
        help="Module id that holds shared <style> rules to embed in each render.",
    )
    parser.add_argument(
        "--png",
        dest="emit_png",
        default=True,
        action=argparse.BooleanOptionalAction,
        help="Also emit PNGs alongside SVGs (requires cairosvg). Enabled by default.",
    )
    parser.add_argument(
        "--module",
        dest="module_filter",
        action="append",
        help="Limit rendering to specific module ids (repeatable).",
    )
    return parser.parse_args()


def strip_namespace(tag: str) -> str:
    return tag.split("}", 1)[1] if tag.startswith("{") else tag


def normalize_tag(tag: str) -> str:
    return tag if tag.startswith("{") else f"{{{SVG_NS}}}{tag}"


def load_style_text(modules_dir: Path, style_id: str) -> str:
    style_path = modules_dir / f"{style_id}.json"
    if not style_path.exists():
        return DEFAULT_STYLE

    data = json.loads(style_path.read_text(encoding="utf-8"))
    return data.get("text") or DEFAULT_STYLE


def collect_attributes(node: dict) -> dict:
    attributes = {k: str(v) for k, v in (node.get("attrib") or {}).items()}
    for meta_key in ("descriptionVerbose", "notes", "category", "role", "shapeType", "aria-label", "ariaLabel", "tabindex"):
        if meta_key in node and meta_key not in attributes:
            attributes[meta_key] = str(node[meta_key])
    return attributes


def build_element(node: dict) -> ET.Element:
    element = ET.Element(normalize_tag(node.get("tag", "g")), collect_attributes(node))

    if "text" in node and node["text"] is not None:
        element.text = str(node["text"])

    for child in node.get("children", []):
        element.append(build_element(child))

    return element


TRANSLATE_RE = re.compile(
    r"translate\(\s*(?P<x>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)\s*(?:[, ]\s*(?P<y>[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?))?\s*\)"
)
POINT_RE = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def parse_translation(transform: str | None) -> tuple[float, float]:
    if not transform:
        return 0.0, 0.0

    match = TRANSLATE_RE.search(transform)
    if not match:
        return 0.0, 0.0

    x = float(match.group("x"))
    y_group = match.group("y")
    y = float(y_group) if y_group not in (None, "") else 0.0
    return x, y


def _points_from_attribute(points: str | None) -> Iterable[tuple[float, float]]:
    if not points:
        return []

    coords = [float(value) for value in POINT_RE.findall(points)]
    return list(zip(coords[::2], coords[1::2]))


def _text_bounds(text: str, x: float, y: float) -> tuple[float, float, float, float]:
    width = max(8.0, len(text) * 8.0)
    height = 16.0
    return x, y - height, x + width, y + height


def combine_bounds(bounds: Iterable[tuple[float, float, float, float]]) -> tuple[float, float, float, float] | None:
    bounds = list(bounds)
    if not bounds:
        return None
    min_x = min(b[0] for b in bounds)
    min_y = min(b[1] for b in bounds)
    max_x = max(b[2] for b in bounds)
    max_y = max(b[3] for b in bounds)
    return min_x, min_y, max_x, max_y


def element_bounds(node: dict, offset: tuple[float, float] = (0.0, 0.0)) -> tuple[float, float, float, float] | None:
    attrib = node.get("attrib") or {}
    translate_x, translate_y = parse_translation(attrib.get("transform"))
    ox, oy = offset[0] + translate_x, offset[1] + translate_y
    tag_name = strip_namespace(node.get("tag", ""))

    candidates: list[tuple[float, float, float, float]] = []

    if tag_name == "rect":
        x = float(attrib.get("x", 0))
        y = float(attrib.get("y", 0))
        w = float(attrib.get("width", 0))
        h = float(attrib.get("height", 0))
        candidates.append((ox + x, oy + y, ox + x + w, oy + y + h))
    elif tag_name == "circle":
        cx = float(attrib.get("cx", 0))
        cy = float(attrib.get("cy", 0))
        r = float(attrib.get("r", 0))
        candidates.append((ox + cx - r, oy + cy - r, ox + cx + r, oy + cy + r))
    elif tag_name == "line":
        x1 = float(attrib.get("x1", 0))
        y1 = float(attrib.get("y1", 0))
        x2 = float(attrib.get("x2", 0))
        y2 = float(attrib.get("y2", 0))
        candidates.append((ox + min(x1, x2), oy + min(y1, y2), ox + max(x1, x2), oy + max(y1, y2)))
    elif tag_name in {"polygon", "polyline"}:
        points = list(_points_from_attribute(attrib.get("points")))
        if points:
            xs, ys = zip(*points)
            candidates.append((ox + min(xs), oy + min(ys), ox + max(xs), oy + max(ys)))
    elif tag_name == "text":
        text = node.get("text", "")
        x = float(attrib.get("x", 0))
        y = float(attrib.get("y", 0))
        candidates.append(_text_bounds(str(text), ox + x, oy + y))

    for child in node.get("children", []):
        child_bounds = element_bounds(child, (ox, oy))
        if child_bounds:
            candidates.append(child_bounds)

    return combine_bounds(candidates)


def render_module(module_data: dict, output_dir: Path, style_text: str, emit_png: bool = True) -> tuple[Path, Path | None]:
    module_id = module_data.get("id", "module")
    output_dir.mkdir(parents=True, exist_ok=True)

    bounds = element_bounds(module_data) or (0.0, 0.0, 100.0, 100.0)
    min_x, min_y, max_x, max_y = bounds
    padding = 10.0
    width = max(1.0, (max_x - min_x) + 2 * padding)
    height = max(1.0, (max_y - min_y) + 2 * padding)
    view_box = f"{min_x - padding} {min_y - padding} {width} {height}"

    svg_attributes = {
        "version": "1.1",
        "viewBox": view_box,
        "width": f"{width}mm",
        "height": f"{height}mm",
        "id": f"{module_id}_svg",
    }

    svg_root = ET.Element(normalize_tag("svg"), svg_attributes)

    if style_text:
        style_el = ET.SubElement(svg_root, normalize_tag("style"))
        style_el.text = style_text

    svg_root.append(build_element(module_data))

    tree = ET.ElementTree(svg_root)
    ET.indent(tree, space="  ")

    svg_path = output_dir / f"{module_id}.svg"
    tree.write(svg_path, encoding="utf-8", xml_declaration=True)

    png_path: Path | None = None
    if emit_png:
        try:
            import cairosvg  # type: ignore

            png_path = output_dir / f"{module_id}.png"
            cairosvg.svg2png(url=str(svg_path), write_to=str(png_path))
        except ImportError:
            from cadquerywrapper.import_advice import print_import_advice

            print_import_advice(
                "cairosvg",
                "python -m pip install cairosvg (or pip install --user cairosvg); rerun with --no-png to skip raster output.",
                f"PNG rendering for {module_id} is optional.",
            )
        except Exception as exc:  # pragma: no cover - conversion errors depend on runtime env
            print(f"[warn] Failed to render PNG for {module_id}: {exc}")
            png_path = None

    return svg_path, png_path


def iter_modules(modules_dir: Path, module_filter: list[str] | None) -> Iterable[Path]:
    for path in sorted(modules_dir.glob("*.json")):
        if module_filter and path.stem not in module_filter:
            continue
        yield path


def main() -> None:
    args = parse_args()
    style_text = load_style_text(args.modules, args.style_module)

    svg_count = 0
    png_count = 0
    for module_path in iter_modules(args.modules, args.module_filter):
        data = json.loads(module_path.read_text(encoding="utf-8"))
        svg_path, maybe_png = render_module(data, args.out, style_text, emit_png=args.emit_png)
        svg_count += 1
        png_count += 1 if maybe_png else 0
        print(f"[ok] Rendered {module_path.stem} -> {svg_path.name}" + (f", {maybe_png.name}" if maybe_png else ""))

    print(f"Finished rendering {svg_count} module(s); PNGs generated for {png_count}.")


if __name__ == "__main__":
    main()
