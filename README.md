# Arcade cabinet SVG modules

This repository contains a disassembled SVG of a small arcade cabinet. Each top-level node from the source drawing has been exported to a standalone JSON module so it is easy to browse, script against, or recombine.

## Repository layout
- `modules/` – JSON snapshots of individual SVG nodes (panels, isometric views, annotations, and hardware cut-outs such as the PSU and VESA plates).
- `toc.json` – a table of contents that lists every module with its role, category, and accessible label for quick lookup.

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

## License
See [LICENSE](LICENSE) for terms.
