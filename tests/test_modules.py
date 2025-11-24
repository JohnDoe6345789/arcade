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


def _monitor_dimensions(diagonal_inches: float) -> tuple[float, float]:
    diagonal_mm = diagonal_inches * 25.4
    aspect_width = 16
    aspect_height = 9
    scale = diagonal_mm / math.sqrt(aspect_width**2 + aspect_height**2)
    return aspect_width * scale, aspect_height * scale


def test_monitor_bezel_viewing_window_supports_22_and_24_inch_screens():
    bezel = load_module("monitor_bezel_panel")
    viewing_window = next(
        child for child in bezel["children"] if child.get("attrib", {}).get("id") == "bezel_viewing_window"
    )["attrib"]

    window_width = float(viewing_window["width"])
    window_height = float(viewing_window["height"])
    window_diagonal = math.hypot(window_width, window_height)

    for diagonal in (22, 24):
        screen_width, screen_height = _monitor_dimensions(diagonal)
        screen_diagonal = math.hypot(screen_width, screen_height)

        assert screen_width < window_width, f"{diagonal}\" monitor width should fit within bezel window"
        assert screen_height < window_height, f"{diagonal}\" monitor height should fit within bezel window"
        assert screen_diagonal < window_diagonal, f"{diagonal}\" monitor diagonal should fit within bezel window"


def test_vesa_mount_plate_supports_75_and_100_mm_patterns():
    vesa = load_module("vesa_mount_plate")
    hole_group = [
        child
        for child in vesa["children"]
        if child["tag"].endswith("circle") and child.get("attrib", {}).get("class") == "panel"
    ]

    centers = {(float(hole["attrib"]["cx"]), float(hole["attrib"]["cy"])) for hole in hole_group}

    hundred_pattern = {(100.0, 100.0), (200.0, 100.0), (100.0, 200.0), (200.0, 200.0)}
    seventy_five_pattern = {
        (112.5, 112.5),
        (187.5, 112.5),
        (112.5, 187.5),
        (187.5, 187.5),
    }

    assert hundred_pattern.issubset(centers), "VESA 100x100 mm bolt pattern should be present"
    assert seventy_five_pattern.issubset(centers), "VESA 75x75 mm bolt pattern should be present"


def _iter_objects(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _iter_objects(child)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_objects(item)


def _expressiveness_score(identifier: str) -> float:
    """Score identifiers so descriptive names outrank auto-generated labels.

    The scoring intentionally docks short, generic SVG-derived ids such as
    "circle2" while rewarding longer, tokenized names like
    "case_back_panel_usb_port". The algorithm is deliberately simple: size and
    word-like tokens add points, while common SVG prefixes paired with numeric
    suffixes lose points.
    """

    name = identifier.strip()
    score = len(name) / 3

    tokens = [token for token in re.split(r"[_\s-]+", name) if token]
    if len(tokens) > 1:
        score += 0.5 * (len(tokens) - 1)
    if "_" in name or "-" in name:
        score += 1
    if len(name) >= 15:
        score += 0.5

    if re.fullmatch(r"(?i)(rect|circle|path|line|g)\d+", name):
        score -= 3
    elif re.match(r"(?i)^(rect|circle|path|line|g)[\d_]*$", name):
        score -= 1
    if re.search(r"\d+$", name) and len(tokens) <= 1:
        score -= 0.5

    return score


def test_identifier_scoring_rewards_expressive_names():
    lazy = _expressiveness_score("circle2")
    lazy_bulk = _expressiveness_score("circle25")
    descriptive = _expressiveness_score("case_back_panel_usb_port")

    assert descriptive > lazy, "Descriptive identifiers should outrank lazy SVG defaults"
    assert lazy_bulk < 0.5, "SVG auto-generated ids should be heavily penalized"
    assert lazy < 1.5, "Lazy names should receive a meaningful penalty"
    assert descriptive >= lazy + 4, "Richly tokenized names should earn a meaningful boost"


def test_identifiers_are_expressive_strings():
    """All nodes with ids should expose non-empty, descriptive-friendly identifiers."""

    scores = []
    lazy_ids = []
    lazy_pattern = re.compile(r"^(rect|circle|path|line|g)\d+$", re.IGNORECASE)
    for module_path in MODULES_DIR.glob("*.json"):
        data = json.loads(module_path.read_text())

        for obj in _iter_objects(data):
            if "id" not in obj:
                continue

            ident = obj["id"]
            assert isinstance(ident, str), f"id must be a string in {module_path.name}: {ident!r}"

            normalized = ident.strip()
            assert normalized, f"id must not be empty or whitespace in {module_path.name}"
            assert any(ch.isalpha() for ch in normalized), f"id should be expressive and contain letters: {ident!r} in {module_path.name}"

            if lazy_pattern.match(normalized):
                lazy_ids.append((module_path.name, normalized))

            score = _expressiveness_score(normalized)
            scores.append(score)

    assert scores, "No ids were discovered to score"

    assert not lazy_ids, f"Replace auto-generated ids: {lazy_ids}"

    average_score = sum(scores) / len(scores)
    weak_identifiers = [score for score in scores if score < 0.5]

    assert average_score >= 1.5, "Identifiers should trend toward descriptive, longer names"
    assert len(weak_identifiers) <= max(10, len(scores) * 0.05), "Only a handful of ids should look like SVG defaults"

