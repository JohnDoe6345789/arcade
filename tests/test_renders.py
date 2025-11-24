import math
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RENDERS_DIR = ROOT / "renders"


def _svg_paths():
    return sorted(RENDERS_DIR.glob("*.svg"))


def _png_paths():
    return sorted(RENDERS_DIR.glob("*.png"))


def test_renders_have_svg_and_png_pairs():
    svgs = {path.stem for path in _svg_paths()}
    pngs = {path.stem for path in _png_paths()}

    assert svgs, "renders/ should contain at least one SVG render"
    assert pngs, "renders/ should contain at least one PNG render"

    missing_png = svgs - pngs
    extra_png = pngs - svgs
    assert not missing_png and not extra_png, f"SVG/PNG pairs must match (missing PNG: {sorted(missing_png)}, extra PNG: {sorted(extra_png)})"


def test_svg_roots_expose_units_and_viewbox():
    for path in _svg_paths():
        root = ET.parse(path).getroot()

        width_attr = root.attrib.get("width")
        height_attr = root.attrib.get("height")
        view_box = root.attrib.get("viewBox")
        svg_id = root.attrib.get("id", "")

        assert width_attr and width_attr.endswith("mm"), f"{path.name} width must be in millimeters"
        assert height_attr and height_attr.endswith("mm"), f"{path.name} height must be in millimeters"
        assert view_box, f"{path.name} must define a viewBox"
        assert svg_id, f"{path.name} must define an id"

        width_mm = float(width_attr[:-2])
        height_mm = float(height_attr[:-2])
        assert width_mm > 0 and height_mm > 0, f"{path.name} width/height must be positive"

        view_box_parts = view_box.split()
        assert len(view_box_parts) == 4, f"{path.name} viewBox should include four numeric values"
        vb_x, vb_y, vb_width, vb_height = map(float, view_box_parts)
        assert math.isfinite(vb_x) and math.isfinite(vb_y), f"{path.name} viewBox origin must be numeric"
        assert vb_width > 0 and vb_height > 0, f"{path.name} viewBox dimensions must be positive"

        assert math.isclose(width_mm, vb_width, abs_tol=0.01), f"{path.name} width should mirror viewBox width"
        assert math.isclose(height_mm, vb_height, abs_tol=0.01), f"{path.name} height should mirror viewBox height"

        expected_id = f"{path.stem}_svg"
        assert svg_id == expected_id, f"{path.name} id should match filename ({expected_id})"
