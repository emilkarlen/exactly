from abc import ABC, abstractmethod

from exactly_lib.type_val_prims.description.structure_building import StructureBuilder
from exactly_lib.type_val_prims.description.tree_structured import WithNameAndNodeDescription, \
    StructureRenderer, \
    WithNodeDescription
from exactly_lib.util.description_tree import renderers


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


class WithCachedNodeDescriptionBase(WithNodeDescription, ABC):
    def __init__(self):
        self._structure_renderer = renderers.CachedSingleInvokation(
            renderers.FromFunction(self._structure)
        )

    def structure(self) -> StructureRenderer:
        return self._structure_renderer

    @abstractmethod
    def _structure(self) -> StructureRenderer:
        raise NotImplementedError('abstract method')
