from abc import ABC, abstractmethod

from exactly_lib.util.description_tree.renderer import DetailsRenderer


class WithDetailsDescription(ABC):
    @property
    @abstractmethod
    def describer(self) -> DetailsRenderer:
        """
        The structure of the object, that can be used in traced.

        The returned details are constant.
        """
        pass
