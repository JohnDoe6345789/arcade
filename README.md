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

## Install render/validation tools
WSL/Ubuntu helper to install the CLI utilities used for validating and re-rendering SVG/PNG outputs:

```bash
bash scripts/install_render_tools.sh
```

Installs apt packages (pngcheck, ImageMagick, xmllint, Inkscape), npm tools (svgo, svglint when npm is present), and `cairosvg` via pip (prefers `.venv/bin/python` if available). Set `SKIP_APT_UPDATE=1` to skip `apt-get update`, or `PY_BIN` to point at a different Python interpreter.

Fakeroot/no-sudo install (keeps apt caches under `.cache/fakeroot-apt` and extracts into your chosen prefix):

```bash
FAKEROOT="$PWD/.local/fakeroot" INSTALL_INKSCAPE=0 bash scripts/install_render_tools.sh
export PATH="$PWD/.local/fakeroot/usr/bin:$PWD/.local/fakeroot/usr/local/bin:$PATH"
export LD_LIBRARY_PATH="$PWD/.local/fakeroot/usr/lib/x86_64-linux-gnu:$PWD/.local/fakeroot/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
```

Set `INSTALL_INKSCAPE=1` if you want Inkscape included in the fakeroot bundle (larger download). Use `NPM_PREFIX` to override where local npm packages land when `FAKEROOT` is set.

Validate the generated renders (SVG/PNG) with the lint helpers and pytest checks:

```bash
bash scripts/validate_renders.sh          # runs xmllint/pngcheck + pytest
VALIDATE_PARITY=1 bash scripts/validate_renders.sh  # also re-renders PNGs and compares against committed PNGs
```

## Install cadquerywrapper deps without sudo
Set up the cadquerywrapper runtime (cadquery + trimesh) rootlessly:

```bash
# create/activate a local venv (recommended). If .venv fails on your platform, retry with "python3 -m venv venv && source venv/bin/activate".
python3 -m venv .venv && source .venv/bin/activate

bash scripts/install_cadquerywrapper_deps.sh                # installs into .venv (creates if missing)
USE_VENV=0 USE_USER=1 bash scripts/install_cadquerywrapper_deps.sh  # reuse system python with pip --user
```

## Dockerized tooling
Image with all render/validation dependencies (Python, cairosvg, pytest, ImageMagick, Inkscape, pngcheck, svgo/svglint via Node 20):

```bash
docker build -t arcade-tools .
docker run --rm -it -v \"$PWD\":/workspace -w /workspace arcade-tools bash -lc \"python render_modules.py --out renders && bash scripts/validate_renders.sh\"
```

Use the container as a clean, reproducible environment for rendering or running the test suite without installing host dependencies.

## License
See [LICENSE](LICENSE) for terms.
