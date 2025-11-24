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
# 2.  Creates a 3D box that will have a hole placed in it later.
result = cq.Workplane("front").box(2, 3, 0.5)

# 3.  Find the top-most face with the >Z max selector.
# 3a. Establish a new workplane to build geometry on.
# 3b.  Create a hole down into the box.
result = result.faces(">Z").workplane().hole(0.5)

# Displays the result of this script
show_object(result)

# Validate and export with CadQueryWrapper
wrapper = CadQueryWrapper(
    "cadquerywrapper/rules/bambu_printability_rules.json",
    result,
)
wrapper.export_stl("Ex012_Creating_Workplanes_on_Faces.stl")
