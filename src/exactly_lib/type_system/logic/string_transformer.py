from abc import ABC, abstractmethod

from exactly_lib.appl_env.app_env_dep_val import ApplicationEnvironmentDependentValue
from exactly_lib.type_system.description.tree_structured import WithNameAndTreeStructureDescription
from exactly_lib.type_system.logic.logic_base_class import LogicWithNodeDescriptionDdv
from exactly_lib.type_system.logic.string_model import StringModel


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

    @abstractmethod
    def transform(self, model: StringModel) -> StringModel:
        pass

    def __str__(self):
        return type(self).__name__


StringTransformerAdv = ApplicationEnvironmentDependentValue[StringTransformer]


class StringTransformerDdv(LogicWithNodeDescriptionDdv[StringTransformer], ABC):
    pass
