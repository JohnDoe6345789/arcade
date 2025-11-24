import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULES_DIR = ROOT / "modules"
TOC_PATH = ROOT / "toc.json"


def load_module(module_id: str) -> dict:
    module_path = MODULES_DIR / f"{module_id}.json"
    return json.loads(module_path.read_text())


def test_toc_entries_have_matching_modules():
    toc = json.loads(TOC_PATH.read_text())
    assert toc, "toc.json should list at least one module"

    for entry in toc:
        module_path = MODULES_DIR / f"{entry['id']}.json"
        assert module_path.exists(), f"Module JSON missing for id={entry['id']}"

        module_data = load_module(entry["id"])
        assert module_data["id"] == entry["id"], "Module id must echo TOC id"
        assert module_data["tag"] == entry["tag"], "Module tag should align with TOC tag"
        assert isinstance(module_data.get("children", []), list), "children must be present as a list"


def test_modules_provide_enriched_attributes():
    for module_path in MODULES_DIR.glob("*.json"):
        data = json.loads(module_path.read_text())
        assert "attrib" in data, f"{module_path.name} should expose SVG attributes"
        attrib = data["attrib"]
        assert "id" in attrib, f"{module_path.name} attrib should include id"
        assert "descriptionVerbose" in attrib, f"{module_path.name} attrib should document the element"
        assert "notes" in attrib, f"{module_path.name} attrib should carry preservation note"


def parse_translation(transform: str):
    match = re.search(r"translate\(([^,]+),([^\)]+)\)", transform)
    assert match, f"Unexpected transform format: {transform}"
    return float(match.group(1)), float(match.group(2))


def test_psu_tray_mount_pattern_matches_atx_psu_spec():
    psu_module = load_module("psu_tray")
    hole_group = next(
        child for child in psu_module["children"] if child.get("attrib", {}).get("id") == "psu_holes"
    )

    translate_x, translate_y = parse_translation(hole_group["attrib"]["transform"])
    assert math.isclose(translate_x, 40.0, abs_tol=0.01)
    assert math.isclose(translate_y, 40.0, abs_tol=0.01)

    holes = [
        (float(child["attrib"]["cx"]) + translate_x, float(child["attrib"]["cy"]) + translate_y)
        for child in hole_group["children"]
        if child["tag"].endswith("circle")
    ]

    assert len(holes) == 4, "ATX PSU mount should expose four mounting holes"

    xs, ys = zip(*holes)
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    assert math.isclose(width, 81.5, abs_tol=0.01), "ATX PSU holes should be 81.5 mm apart horizontally"
    assert math.isclose(height, 71.5, abs_tol=0.01), "ATX PSU holes should be 71.5 mm apart vertically"


def test_motherboard_tray_atx_hole_layout():
    motherboard = load_module("motherboard_tray")
    atx_group = next(
        child for child in motherboard["children"] if child.get("attrib", {}).get("id") == "atx_holes"
    )

    hole_positions = {
        (round(float(child["attrib"]["cx"]), 3), round(float(child["attrib"]["cy"]), 3))
        for child in atx_group["children"]
        if child["tag"].endswith("circle")
    }

    expected_positions = {
        (9.525, 9.525),
        (45.72, 9.525),
        (175.26, 9.525),
        (294.64, 9.525),
        (9.525, 120.65),
        (175.26, 120.65),
        (294.64, 120.65),
        (9.525, 190.5),
        (294.64, 190.5),
        (9.525, 231.775),
        (175.26, 231.775),
        (294.64, 231.775),
    }

    assert hole_positions == expected_positions, "ATX mount pattern should match spec coordinates"

    xs = [x for x, _ in hole_positions]
    ys = [y for _, y in hole_positions]
    assert math.isclose(max(xs) - min(xs), 285.115, abs_tol=0.01), "ATX width should be 11.225 in (285.115 mm)"
    assert math.isclose(max(ys) - min(ys), 222.25, abs_tol=0.01), "ATX height should be 8.75 in (222.25 mm)"

