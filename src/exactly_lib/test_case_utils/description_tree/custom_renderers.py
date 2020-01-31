from exactly_lib.definitions import logic
from exactly_lib.type_system.description.tree_structured import StructureRenderer, WithTreeStructureDescription
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.logic_types import ExpectationType


def negation(negated: NodeRenderer[None]) -> NodeRenderer[None]:
    return renderers.NodeRendererFromParts(
        logic.NOT_OPERATOR_NAME,
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


class WithTreeStructure(NodeRenderer[None]):
    def __init__(self, tree_structured: WithTreeStructureDescription):
        self._tree_structured = tree_structured

    def render(self) -> Node[None]:
        return self._tree_structured.structure().render()
