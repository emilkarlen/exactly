from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Sequence

from exactly_lib.tcfs import ddv_validation
from exactly_lib.tcfs.ddv_validation import DdvValidator
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_system.description.tree_structured import WithNameAndTreeStructureDescription
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue, \
    LogicWithNodeDescriptionDdv
from exactly_lib.type_system.logic.matching_result import MatchingResult

MODEL = TypeVar('MODEL')
T = TypeVar('T')


class MatcherWTrace(Generic[MODEL], WithNameAndTreeStructureDescription, ABC):
    @abstractmethod
    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        pass

    def accept(self, visitor: 'MatcherStdTypeVisitor[MODEL, T]') -> T:
        return visitor.visit_non_standard(self)


class MatcherStdTypeVisitor(Generic[MODEL, T], ABC):
    @abstractmethod
    def visit_constant(self, value: bool) -> T:
        pass

    @abstractmethod
    def visit_negation(self, operand: MatcherWTrace[MODEL]) -> T:
        pass

    @abstractmethod
    def visit_conjunction(self, operands: Sequence[MatcherWTrace[MODEL]]) -> T:
        pass

    @abstractmethod
    def visit_disjunction(self, operands: Sequence[MatcherWTrace[MODEL]]) -> T:
        pass

    @abstractmethod
    def visit_non_standard(self, matcher: MatcherWTrace[MODEL]) -> T:
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
    def value_of_any_dependency(self, tcds: TestCaseDs) -> MatcherAdv[MODEL]:
        pass
