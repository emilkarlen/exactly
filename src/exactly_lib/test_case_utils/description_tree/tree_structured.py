from abc import ABC, abstractmethod

from exactly_lib.test_case_utils.description_tree.custom_details import WithTreeStructure
from exactly_lib.type_system.description.structure_building import StructureBuilder
from exactly_lib.type_system.description.tree_structured import WithNameAndTreeStructureDescription, StructureRenderer, \
    WithTreeStructureDescription
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer


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
        return WithTreeStructure(tree_structured)


class WithCachedTreeStructureDescriptionBase(WithTreeStructureDescription, ABC):
    def __init__(self):
        self._structure_renderer = renderers.CachedSingleInvokation(
            renderers.FromFunction(self._structure)
        )

    def structure(self) -> StructureRenderer:
        return self._structure_renderer

    @abstractmethod
    def _structure(self) -> StructureRenderer:
        pass
