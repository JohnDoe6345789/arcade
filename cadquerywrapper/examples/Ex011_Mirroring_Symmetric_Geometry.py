try:
    import cadquery as cq
except ModuleNotFoundError as exc:
    from cadquerywrapper.import_advice import print_import_advice

    print_import_advice(
        "cadquery",
        "bash scripts/install_cadquerywrapper_deps.sh (or python -m pip install cadquery)",
        "CadQuery is required to run this example.",
    )
    raise
from cadquerywrapper import CadQueryWrapper

# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  A horizontal line is drawn on the workplane with the hLine function.
# 2a. 1.0 is the distance, not coordinate. hLineTo allows using xCoordinate
#     not distance.
r = cq.Workplane("front").hLine(1.0)

# 3.  Draw a series of vertical and horizontal lines with the vLine and hLine
#     functions.
r = r.vLine(0.5).hLine(-0.25).vLine(-0.25).hLineTo(0.0)

# 4.  Mirror the geometry about the Y axis and extrude it into a 3D object.
result = r.mirrorY().extrude(0.25)

# Displays the result of this script
show_object(result)

# Validate and export with CadQueryWrapper
wrapper = CadQueryWrapper(
    "cadquerywrapper/rules/bambu_printability_rules.json",
    result,
)
wrapper.export_stl("Ex011_Mirroring_Symmetric_Geometry.stl")
