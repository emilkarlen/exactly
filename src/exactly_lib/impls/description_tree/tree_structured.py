from abc import ABC, abstractmethod

from exactly_lib.impls.description_tree.custom_details import WithTreeStructure
from exactly_lib.type_val_prims.description.structure_building import StructureBuilder
from exactly_lib.type_val_prims.description.tree_structured import WithNameAndNodeDescription, \
    StructureRenderer, \
    WithNodeDescription
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer


class WithCachedNameAndNodeStructureDescriptionBase(WithNameAndNodeDescription, ABC):
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
    def _details_renderer_of(tree_structured: WithNameAndNodeDescription) -> DetailsRenderer:
        return WithTreeStructure(tree_structured)


class WithCachedNodeDescriptionBase(WithNodeDescription, ABC):
    def __init__(self):
        self._structure_renderer = renderers.CachedSingleInvokation(
            renderers.FromFunction(self._structure)
        )

    def structure(self) -> StructureRenderer:
        return self._structure_renderer

    @abstractmethod
    def _structure(self) -> StructureRenderer:
        pass
