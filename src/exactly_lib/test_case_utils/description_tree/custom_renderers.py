from exactly_lib.definitions import expression
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer


def negation(negated: NodeRenderer[None]) -> NodeRenderer[None]:
    return renderers.NodeRendererFromParts(
        expression.NOT_OPERATOR_NAME,
        None,
        (),
        (negated,),
    )
