from typing import Sequence, Optional

from exactly_lib.definitions.primitives import string_source
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer, WithNodeDescription
from exactly_lib.util.description_tree import renderers


def sequence_of_unknown_num_operands(parts: Sequence[WithNodeDescription]) -> Optional[StructureRenderer]:
    num_operands = len(parts)

    if num_operands == 0:
        return None
    elif num_operands == 1:
        return parts[0].structure()
    else:
        return sequence_of_at_least_2_operands(parts)


def sequence_of_at_least_2_operands(parts: Sequence[WithNodeDescription]) -> StructureRenderer:
    return renderers.NodeRendererFromParts(
        string_source.CONCAT_NAME,
        None,
        (),
        [part.structure() for part in parts],
    )
