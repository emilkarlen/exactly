from typing import Sequence, Optional

from exactly_lib.definitions.primitives import string_transformer
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer, WithNodeDescription
from exactly_lib.util.description_tree import renderers


def sequence_of_unknown_num_operands(operands: Sequence[WithNodeDescription]) -> StructureRenderer:
    num_operands = len(operands)

    if num_operands == 0:
        return renderers.header_only(string_transformer.IDENTITY_TRANSFORMER_NAME)
    elif num_operands == 1:
        return operands[0].structure()
    else:
        return sequence_of_at_least_2_operands(operands)


def sequence_of_renderers__optional(operands: Sequence[StructureRenderer]) -> Optional[StructureRenderer]:
    num_operands = len(operands)

    if num_operands == 0:
        return None
    elif num_operands == 1:
        return operands[0]
    else:
        return sequence_of_at_least_2_operands__renderers(operands)


def sequence_of_at_least_2_operands(operands: Sequence[WithNodeDescription]) -> StructureRenderer:
    return renderers.NodeRendererFromParts(
        string_transformer.SEQUENCE_OPERATOR_NAME,
        None,
        (),
        [
            operand.structure()
            for operand in operands
        ],
    )


def sequence_of_at_least_2_operands__renderers(operands: Sequence[StructureRenderer]) -> StructureRenderer:
    return renderers.NodeRendererFromParts(
        string_transformer.SEQUENCE_OPERATOR_NAME,
        None,
        (),
        operands,
    )
