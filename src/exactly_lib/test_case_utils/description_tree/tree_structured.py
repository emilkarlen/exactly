from abc import ABC
from typing import Sequence

from exactly_lib.type_system.description.structure_building import StructureBuilder
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription
from exactly_lib.util.description_tree import renderers, tree
from exactly_lib.util.description_tree.renderer import NodeRenderer, DetailsRenderer
from exactly_lib.util.description_tree.tree import Node, Detail


class WithCachedTreeStructureDescriptionBase(WithTreeStructureDescription, ABC):
    def __init__(self):
        self._structure_renderer = renderers.CachedSingleInvokation(
            renderers.FromFunction(self._structure)
        )

    def structure(self) -> Node[None]:
        return self._structure_renderer.render()

    def _structure(self) -> NodeRenderer[None]:
        return renderers.Constant(
            tree.Node(self.name,
                      None,
                      (),
                      ()),
        )

    def _new_structure_builder(self) -> StructureBuilder:
        return StructureBuilder(self.name)

    @staticmethod
    def _node_renderer_of(tree_structured: WithTreeStructureDescription) -> NodeRenderer[None]:
        return _NodeRendererFromTreeStructured(tree_structured)

    @staticmethod
    def _details_renderer_of(tree_structured: WithTreeStructureDescription) -> DetailsRenderer:
        return _DetailsRendererFromTreeStructured(tree_structured)


class _DetailsRendererFromTreeStructured(DetailsRenderer):
    def __init__(self, tree_structured: WithTreeStructureDescription):
        self._tree_structured = tree_structured

    def render(self) -> Sequence[Detail]:
        return [tree.TreeDetail(self._tree_structured.structure())]


class _NodeRendererFromTreeStructured(NodeRenderer[None]):
    def __init__(self, tree_structured: WithTreeStructureDescription):
        self._tree_structured = tree_structured

    def render(self) -> Node[None]:
        return self._tree_structured.structure()
