from abc import ABC, abstractmethod

from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer

StructureRenderer = NodeRenderer[None]


class WithTreeStructureDescription(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def structure(self) -> StructureRenderer:
        """
        The structure of the object, that can be used in traced.

        The returned tree is constant.
        """
        return renderers.NodeRendererFromParts(
            self.name,
            None,
            (),
            (),
        )
