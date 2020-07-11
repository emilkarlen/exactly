from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exactly_lib.test_case_file_structure import ddv_validation
from exactly_lib.test_case_file_structure.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import WithNameAndTreeStructureDescription
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, \
    LogicWithNodeDescriptionDdv
from exactly_lib.type_system.logic.matching_result import MatchingResult

MODEL = TypeVar('MODEL')


class MatcherWTrace(Generic[MODEL], WithNameAndTreeStructureDescription, ABC):
    @abstractmethod
    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        pass


class MatcherAdv(Generic[MODEL],
                 ApplicationEnvironmentDependentValue[MatcherWTrace[MODEL]],
                 ABC):
    """Application Environment Dependent Matcher"""

    @abstractmethod
    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        pass


class MatcherDdv(Generic[MODEL],
                 LogicWithNodeDescriptionDdv[MatcherWTrace[MODEL]],
                 ABC):
    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.constant_success_validator()

    @abstractmethod
    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        pass
