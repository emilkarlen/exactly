from abc import abstractmethod, ABC
from typing import TypeVar, Generic

from exactly_lib.test_case_file_structure import ddv_validation
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription, StructureRenderer
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.description import LogicValueDescription, NodeDescription

VALUE_TYPE = TypeVar('VALUE_TYPE')


class ApplicationEnvironmentDependentValue(Generic[VALUE_TYPE], ABC):
    """A value that may depend on :class:`ApplicationEnvironment`"""

    @abstractmethod
    def primitive(self, environment: ApplicationEnvironment) -> VALUE_TYPE:
        pass


class LogicDdv(Generic[VALUE_TYPE],
               DirDependentValue[ApplicationEnvironmentDependentValue[VALUE_TYPE]],
               ABC):
    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.constant_success_validator()

    @abstractmethod
    def description(self) -> LogicValueDescription:
        pass

    @abstractmethod
    def value_of_any_dependency(self, tcds: Tcds) -> ApplicationEnvironmentDependentValue[VALUE_TYPE]:
        pass


class LogicWithNodeDescriptionDdv(Generic[VALUE_TYPE],
                                  LogicDdv[VALUE_TYPE],
                                  WithTreeStructureDescription,
                                  ABC):
    """A :class:`LogicDdv` that can report its structure in terms of a node tree"""

    def description(self) -> NodeDescription:
        return _DescriptionOfTreeStructure(self)


class _DescriptionOfTreeStructure(NodeDescription):
    def __init__(self, tree_structured: WithTreeStructureDescription):
        self._tree_structured = tree_structured

    def structure(self) -> StructureRenderer:
        return self._tree_structured.structure()
