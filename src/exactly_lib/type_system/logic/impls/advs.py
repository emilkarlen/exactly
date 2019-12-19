from typing import Generic, Callable, TypeVar

from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue
from exactly_lib.type_system.logic.matcher_base_class import MatcherAdv, MODEL, ApplicationEnvironment, \
    MatcherWTraceAndNegation

T = TypeVar('T')


class ConstantAdv(Generic[T], ApplicationEnvironmentDependentValue[T]):
    def __init__(self, constant: T):
        self._constant = constant

    def applier(self, environment: ApplicationEnvironment) -> T:
        return self._constant


class ConstantMatcherAdv(Generic[MODEL], MatcherAdv[MODEL]):
    def __init__(self, constant: MatcherWTraceAndNegation[MODEL]):
        self._constant = constant

    def applier(self, environment: ApplicationEnvironment) -> MatcherWTraceAndNegation[MODEL]:
        return self._constant


class MatcherAdvFromFunction(Generic[MODEL], MatcherAdv[MODEL]):
    def __init__(self, constructor: Callable[[ApplicationEnvironment], MatcherWTraceAndNegation[MODEL]]):
        self._constructor = constructor

    def applier(self, environment: ApplicationEnvironment) -> MatcherWTraceAndNegation[MODEL]:
        return self._constructor(environment)
