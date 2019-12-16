from typing import Generic

from exactly_lib.type_system.logic.matcher_base_class import MatcherAdv, MODEL, ApplicationEnvironment, \
    MatcherWTraceAndNegation


class ConstantAdv(Generic[MODEL], MatcherAdv[MODEL]):
    def __init__(self, constant: MatcherWTraceAndNegation[MODEL]):
        self._constant = constant

    def applier(self, environment: ApplicationEnvironment) -> MatcherWTraceAndNegation[MODEL]:
        return self._constant
