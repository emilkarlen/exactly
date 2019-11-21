from typing import Generic, Optional

from exactly_lib.definitions.primitives import boolean
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, T, MatchingResult, Failure
from exactly_lib.util.description_tree import renderers, tree


class MatcherWithConstantResult(Generic[T], MatcherWTraceAndNegation[T]):
    NAME = 'constant'

    def __init__(self, result: bool):
        self._result = result
        self._matching_result = MatchingResult(
            self._result,
            renderers.Constant(
                tree.Node(self.NAME, self._result,
                          (tree.StringDetail(boolean.BOOLEANS[result]),),
                          ())
            ),
        )

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def option_description(self) -> str:
        return self.name

    @property
    def negation(self) -> 'MatcherWithConstantResult[T]':
        return MatcherWithConstantResult(not self._result)

    def matches_w_trace(self, model: T) -> MatchingResult:
        return self._matching_result

    def matches_w_failure(self, model: T) -> Optional[Failure[T]]:
        raise NotImplementedError('deprecated')

    def matches_emr(self, model: T) -> Optional[ErrorMessageResolver]:
        raise NotImplementedError('deprecated')
