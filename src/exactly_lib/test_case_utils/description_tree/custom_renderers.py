from exactly_lib.definitions import expression
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.logic_types import ExpectationType


def negation(negated: NodeRenderer[None]) -> NodeRenderer[None]:
    return renderers.NodeRendererFromParts(
        expression.NOT_OPERATOR_NAME,
        None,
        (),
        (negated,),
    )


def positive_or_negative(expectation_type: ExpectationType,
                         original: StructureRenderer) -> StructureRenderer:
    return (
        original
        if expectation_type is ExpectationType.POSITIVE
        else
        negation(original)
    )
