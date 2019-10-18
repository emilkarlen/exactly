from abc import ABC
from typing import Sequence

from exactly_lib.type_system.description.structure_building import StructureBuilder
from exactly_lib.type_system.description.tree_structured import WithNameAndTreeStructureDescription, StructureRenderer
from exactly_lib.util.description_tree import renderers, tree
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail


class WithCachedNameAndTreeStructureDescriptionBase(WithNameAndTreeStructureDescription, ABC):
    def __init__(self):
        self._structure_renderer = renderers.CachedSingleInvokation(
            renderers.FromFunction(self._structure)
        )

    def structure(self) -> StructureRenderer:
        return self._structure_renderer

    def _structure(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            self.name,
            None,
            (),
            (),
        )

    def _new_structure_builder(self) -> StructureBuilder:
        return StructureBuilder(self.name)

    @staticmethod
    def _details_renderer_of(tree_structured: WithNameAndTreeStructureDescription) -> DetailsRenderer:
        return _DetailsRendererFromTreeStructured(tree_structured)


class _DetailsRendererFromTreeStructured(DetailsRenderer):
    def __init__(self, tree_structured: WithNameAndTreeStructureDescription):
        self._tree_structured = tree_structured

    def render(self) -> Sequence[Detail]:
        return [tree.TreeDetail(self._tree_structured.structure().render())]
