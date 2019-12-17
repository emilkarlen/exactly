from typing import Generic, Callable

from exactly_lib.type_system.logic.matcher_base_class import MatcherAdv, MODEL, ApplicationEnvironment, \
    MatcherWTraceAndNegation


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
