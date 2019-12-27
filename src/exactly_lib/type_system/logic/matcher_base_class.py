from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import WithNameAndTreeStructureDescription
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment, ApplicationEnvironmentDependentValue, \
    LogicTypeDdv
from exactly_lib.util.description_tree.renderer import NodeRenderer

MODEL = TypeVar('MODEL')

TraceRenderer = NodeRenderer[bool]


class MatchingResult:
    """The result of applying a matcher."""

    def __init__(self,
                 value: bool,
                 trace: TraceRenderer):
        self._value = value
        self._trace = trace

    @property
    def value(self) -> bool:
        return self._value

    @property
    def trace(self) -> TraceRenderer:
        return self._trace


class MatcherWTrace(Generic[MODEL], WithNameAndTreeStructureDescription, ABC):
    @abstractmethod
    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        pass


class MatcherWTraceAndNegation(Generic[MODEL], MatcherWTrace[MODEL], ABC):
    @property
    @abstractmethod
    def negation(self) -> 'MatcherWTraceAndNegation[MODEL]':
        pass


class MatcherAdv(Generic[MODEL],
                 ApplicationEnvironmentDependentValue[MatcherWTraceAndNegation[MODEL]],
                 ABC):
    """Application Environment Dependent Matcher"""

    @abstractmethod
    def applier(self, environment: ApplicationEnvironment) -> MatcherWTraceAndNegation[MODEL]:
        pass


class MatcherDdv(Generic[MODEL],
                 LogicTypeDdv[MatcherWTraceAndNegation[MODEL]],
                 ABC):
    @abstractmethod
    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        pass

    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.constant_success_validator()
