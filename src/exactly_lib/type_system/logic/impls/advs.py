from typing import Generic, Callable, TypeVar

from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue
from exactly_lib.type_system.logic.matcher_base_class import MatcherAdv, MODEL, MatcherWTrace

T = TypeVar('T')


class ConstantAdv(Generic[T], ApplicationEnvironmentDependentValue[T]):
    def __init__(self, constant: T):
        self._constant = constant

    def primitive(self, environment: ApplicationEnvironment) -> T:
        return self._constant


class ConstantMatcherAdv(Generic[MODEL], MatcherAdv[MODEL]):
    def __init__(self, constant: MatcherWTrace[MODEL]):
        self._constant = constant

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        return self._constant


class MatcherAdvFromFunction(Generic[MODEL], MatcherAdv[MODEL]):
    def __init__(self, constructor: Callable[[ApplicationEnvironment], MatcherWTrace[MODEL]]):
        self._constructor = constructor

    def primitive(self, environment: ApplicationEnvironment) -> MatcherWTrace[MODEL]:
        return self._constructor(environment)


class AdvFromFunction(Generic[T], ApplicationEnvironmentDependentValue[T]):
    def __init__(self, constructor: Callable[[ApplicationEnvironment], T]):
        self._constructor = constructor

    def primitive(self, environment: ApplicationEnvironment) -> T:
        return self._constructor(environment)
