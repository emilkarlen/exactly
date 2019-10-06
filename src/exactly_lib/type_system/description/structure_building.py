from typing import List, Sequence

from exactly_lib.util.description_tree.renderer import NodeRenderer, DetailsRenderer, NODE_DATA
from exactly_lib.util.description_tree.renderers import NodeRendererFromParts
from exactly_lib.util.description_tree.tree import Node


class StructureBuilder:
    def __init__(self, header: str):
        self._header = header
        self._details = []
        self._children = []

    @property
    def details(self) -> List[DetailsRenderer]:
        return self._details

    def append_details(self, detail: DetailsRenderer) -> 'StructureBuilder':
        self._details.append(detail)
        return self

    @property
    def children(self) -> List[NodeRenderer[None]]:
        return self._children

    def append_child(self, child: NodeRenderer[None]) -> 'StructureBuilder':
        self._children.append(child)
        return self

    def append_children(self, children: Sequence[NodeRenderer[None]]) -> 'StructureBuilder':
        self._children += children
        return self

    def build(self) -> NodeRenderer[None]:
        return NodeRendererFromParts(
            self._header,
            None,
            self._details,
            self._children,
        )

    def as_render(self) -> NodeRenderer[None]:
        return _NodeRendererFromBuilder(self)


class _NodeRendererFromBuilder(NodeRenderer[None]):
    def __init__(self,
                 builder: StructureBuilder,
                 ):
        self._builder = builder

    def render(self) -> Node[NODE_DATA]:
        return self._builder.build().render()
