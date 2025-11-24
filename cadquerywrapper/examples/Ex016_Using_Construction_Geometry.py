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

# Create a block with holes in each corner of a rectangle on that workplane.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the named plane orientation "front" to define the workplane, meaning
#     that the positive Z direction is "up", and the negative Z direction
#     is "down".
# 2.  Creates a plain box to base future geometry on with the box() function.
# 3.  Selects the top-most Z face of the box.
# 4.  Creates a new workplane to build new geometry on.
# 5.  Creates a for-construction rectangle that only exists to use for placing
#     other geometry.
# 6.  Selects the vertices of the for-construction rectangle.
# 7.  Places holes at the center of each selected vertex.
result = (
    cq.Workplane("front")
    .box(2, 2, 0.5)
    .faces(">Z")
    .workplane()
    .rect(1.5, 1.5, forConstruction=True)
    .vertices()
    .hole(0.125)
)

# Displays the result of this script
show_object(result)

# Validate and export with CadQueryWrapper
wrapper = CadQueryWrapper(
    "cadquerywrapper/rules/bambu_printability_rules.json",
    result,
)
wrapper.export_stl("Ex016_Using_Construction_Geometry.stl")
