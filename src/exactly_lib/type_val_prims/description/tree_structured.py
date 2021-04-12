from abc import ABC, abstractmethod

from exactly_lib.util.description_tree.renderer import NodeRenderer

StructureRenderer = NodeRenderer[None]


class WithNodeDescription(ABC):
    @abstractmethod
    def structure(self) -> StructureRenderer:
        """
        The structure of the object, that can be used in traced.

        The returned tree is constant.
        """
        raise NotImplementedError('abstract method')


class WithNameAndNodeDescription(WithNodeDescription, ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def structure(self) -> StructureRenderer:
        """
        The structure of the object, that can be used in traced.

        The returned tree is constant.
        """
        raise NotImplementedError('abstract method')
