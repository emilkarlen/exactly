import itertools
from typing import Generic, Sequence

from exactly_lib.util.description_tree.renderer import NODE_DATA, NodeRenderer, DetailsRenderer
from exactly_lib.util.description_tree.tree import Node


class Constant(Generic[NODE_DATA], NodeRenderer[NODE_DATA]):
    def __init__(self,
                 constant: Node[NODE_DATA],
                 ):
        self._constant = constant

    def render(self) -> Node[NODE_DATA]:
        return self._constant


class NodeRendererFromParts(Generic[NODE_DATA], NodeRenderer[NODE_DATA]):
    def __init__(self,
                 header: str,
                 data: NODE_DATA,
                 details: Sequence[DetailsRenderer],
                 children: Sequence[NodeRenderer[NODE_DATA]],
                 ):
        self._header = header
        self._data = data
        self._details = details
        self._children = children

    def render(self) -> Node[NODE_DATA]:
        return Node(self._header,
                    self._data,
                    list(itertools.chain.from_iterable(d.render() for d in self._details)),
                    [c.render() for c in self._children],
                    )
