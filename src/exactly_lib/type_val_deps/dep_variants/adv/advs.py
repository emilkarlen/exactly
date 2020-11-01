from typing import Generic, Callable, TypeVar

from exactly_lib.type_val_deps.dep_variants.adv.app_env_dep_val import ApplicationEnvironment, \
    ApplicationEnvironmentDependentValue
from exactly_lib.type_val_deps.dep_variants.adv.matcher import MatcherAdv
from exactly_lib.type_val_prims.matcher.matcher_base_class import MODEL, MatcherWTrace

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
