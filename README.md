# Arcade cabinet SVG modules

This repository captures a bartop arcade cabinet sized for an off-the-shelf 22–24\" monitor (stand removed). The interior makes room for a full ATX motherboard and full ATX power supply, but the footprint also supports a Raspberry Pi swap for a lighter build. Each top-level node from the source drawing has been exported to a standalone JSON module so it is easy to browse, script against, or recombine.

## Repository layout
- `modules/` – JSON snapshots of individual SVG nodes (panels, isometric views, annotations, and hardware cut-outs such as the PSU and VESA plates).
- `toc.json` – a table of contents that lists every module with its role, category, and accessible label for quick lookup.
- `renders/` – auto-generated SVG and PNG exports of each module for quick visual inspection (built by `render_modules.py`).

## JSON module structure
Every module follows the same shape:
- `tag` and `id` identify the original SVG element.
- `attrib` preserves the element attributes (for example transforms, classes, and descriptive notes).
- `children` contains nested elements, allowing you to traverse the original drawing hierarchy.

For a quick peek at a module, you can use `jq`:
```bash
jq '{tag, id, attrib: .attrib | {class, transform}}' modules/assembly_instructions.json
```

## Typical use cases
- Inspect cabinet parts like `motherboard_tray.json`, `control_panel.json`, or `vesa_mount_plate.json` before manufacturing.
- Render or validate the geometry by walking the module tree and emitting standard SVG.
- Filter modules by role or category using the metadata in `toc.json` (for example, all `diagram` entries for isometric views).

## Render modules to SVG and PNG
Use the included helper to emit a folder of design files that you can hand to CAM tools or a print shop. PNGs are emitted alongside the SVGs when `cairosvg` is available.

```bash
source .venv/bin/activate            # or any Python environment with cairosvg installed
python -m pip install cairosvg       # one-time dependency for PNG exports
python render_modules.py --out renders
```

Flags:
- `--no-png` skips rasterizing to PNG if you only want SVGs.
- `--module <id>` limits rendering to specific module ids (repeatable).
- `--style-module <id>` injects a different `modules/<id>.json` style block if you add one.

## License
See [LICENSE](LICENSE) for terms.
