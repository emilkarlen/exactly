from abc import ABC, abstractmethod

from exactly_lib.util.description_tree import tree
from exactly_lib.util.description_tree.tree import Node


class WithTreeStructureDescription(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def structure(self) -> Node[None]:
        """
        The structure of the object, that can be used in traced.

        The returned tree is constant.

        Implementations may be heavy.

        """
        return tree.Node(
            self.name,
            None,
            (),
            (),
        )
