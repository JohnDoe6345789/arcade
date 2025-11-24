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

# Create a plate with 4 rounded corners in the Z-axis.
# 1.  Establishes a workplane that an object can be built on.
# 1a. Uses the X and Y origins to define the workplane, meaning that the
#     positive Z direction is "up", and the negative Z direction is "down".
# 2.  Creates a plain box to base future geometry on with the box() function.
# 3.  Selects all edges that are parallel to the Z axis.
# 4.  Creates fillets on each of the selected edges with the specified radius.
result = cq.Workplane("XY").box(3, 3, 0.5).edges("|Z").fillet(0.125)

# Displays the result of this script
show_object(result)

# Validate and export with CadQueryWrapper
wrapper = CadQueryWrapper(
    "cadquerywrapper/rules/bambu_printability_rules.json",
    result,
)
wrapper.export_stl("Ex020_Rounding_Corners_with_Fillets.stl")
