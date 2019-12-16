from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import WithNameAndTreeStructureDescription
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment, ApplicationEnvironmentDependentValue, \
    LogicTypeDdv
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.with_option_description import WithOptionDescription

MODEL = TypeVar('MODEL')


class Failure(Generic[MODEL]):
    def __init__(self,
                 expectation_type: ExpectationType,
                 expected: str,
                 actual: MODEL):
        self.expectation_type = expectation_type
        self.expected = expected
        self.actual = actual


class Matcher(Generic[MODEL], WithOptionDescription, ABC):
    """Matches a model."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    def matches(self, model: MODEL) -> bool:
        return self.matches_emr(model) is None

    def matches_emr(self, model: MODEL) -> Optional[ErrorMessageResolver]:
        raise NotImplementedError('abstract method')


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


class MatcherWTrace(Generic[MODEL], Matcher[MODEL], WithNameAndTreeStructureDescription, ABC):
    @abstractmethod
    def matches_w_trace(self, model: MODEL) -> MatchingResult:
        pass

    def matches(self, model: MODEL) -> bool:
        return self.matches_w_trace(model).value


class MatcherWTraceAndNegation(Generic[MODEL], MatcherWTrace[MODEL], ABC):
    @property
    @abstractmethod
    def negation(self) -> 'MatcherWTraceAndNegation[MODEL]':
        pass

    def matches_w_failure(self, model: MODEL) -> Optional[Failure[MODEL]]:
        """
        :raises HardErrorException
        """
        raise NotImplementedError('deprecated')


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
    def value_of_any_dependency(self, tcds: Tcds) -> MatcherWTraceAndNegation[MODEL]:
        pass

    @abstractmethod
    def adv_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        """Method that will replace value_of_any_dependency"""
        pass

    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.constant_success_validator()
