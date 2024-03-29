from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.util.description_tree.renderer import DetailsRenderer

T = TypeVar('T')


class DescriptionVisitor(Generic[T]):
    @abstractmethod
    def visit_node(self, description: 'NodeDescription') -> T:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def visit_details(self, description: 'DetailsDescription') -> T:
        raise NotImplementedError('abstract method')


class LogicValueDescription(ABC):
    """Gives a description of a value, useful for error message and structure reporting."""

    def accept(self, visitor: DescriptionVisitor[T]) -> T:
        pass


class NodeDescription(LogicValueDescription, ABC):
    """Gives a description of a value, useful for error message and structure reporting."""

    @abstractmethod
    def structure(self) -> StructureRenderer:
        raise NotImplementedError('abstract method')

    def accept(self, visitor: DescriptionVisitor[T]) -> T:
        return visitor.visit_node(self)


class DetailsDescription(LogicValueDescription, ABC):
    """Gives a description of a value, useful for error message and structure reporting."""

    @abstractmethod
    def details(self) -> DetailsRenderer:
        raise NotImplementedError('abstract method')

    def accept(self, visitor: DescriptionVisitor[T]) -> T:
        return visitor.visit_details(self)
