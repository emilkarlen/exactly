from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node, NODE_DATA


class ConstantNodeRendererTestImpl(NodeRenderer[NODE_DATA]):
    def __init__(self, constant: Node[NODE_DATA]):
        self._constant = constant

    def render(self) -> Node[NODE_DATA]:
        return self._constant
