from abc import ABC, abstractmethod
from typing import Iterable

from exactly_lib.test_case.validation.ddv_validation import DdvValidator, \
    constant_success_validator
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import WithNameAndTreeStructureDescription, \
    WithTreeStructureDescription
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue

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


class StringTransformerDdv(DirDependentValue[ApplicationEnvironmentDependentValue[StringTransformer]],
                           WithTreeStructureDescription,
                           ABC):
    def validator(self) -> DdvValidator:
        return constant_success_validator()

    @abstractmethod
    def value_of_any_dependency(self, tcds: Tcds) -> StringTransformerAdv:
        pass
