from abc import ABC
from typing import Iterable

from exactly_lib.type_system.description.tree_structured import WithNameAndTreeStructureDescription
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, \
    LogicWithNodeDescriptionDdv

StringTransformerModel = Iterable[str]


class StringTransformer(WithNameAndTreeStructureDescription, ABC):
    """
    Transforms a sequence of lines, where each line is a string.
    """

    @property
    def is_identity_transformer(self) -> bool:
        """
        Tells if this transformer is the identity transformer
        """
        return False

    def transform(self, lines: StringTransformerModel) -> StringTransformerModel:
        raise NotImplementedError('abstract method')

    def __str__(self):
        return type(self).__name__


StringTransformerAdv = ApplicationEnvironmentDependentValue[StringTransformer]


class StringTransformerDdv(LogicWithNodeDescriptionDdv[StringTransformer], ABC):
    pass
