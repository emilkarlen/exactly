from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.util.description_tree import renderers


def structure_renderer_for_arbitrary_object(x) -> StructureRenderer:
    return renderers.header_only(str(type(x)))
