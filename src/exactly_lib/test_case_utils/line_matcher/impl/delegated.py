from typing import Optional

from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatchingResult


class LineMatcherDelegatedToMatcherWTrace(LineMatcher):
    def __init__(self, delegated: MatcherWTraceAndNegation[LineMatcherLine]):
        super().__init__()
        self._delegated = delegated

    @property
    def name(self) -> str:
        return self._delegated.name

    def structure(self) -> StructureRenderer:
        return self._delegated.structure()

    @property
    def option_description(self) -> str:
        return self._delegated.option_description

    @property
    def negation(self) -> LineMatcher:
        return LineMatcherDelegatedToMatcherWTrace(
            combinator_matchers.Negation(self)
        )

    def matches(self, model: LineMatcherLine) -> bool:
        return self._delegated.matches(model)

    def matches_emr(self, model: LineMatcherLine) -> Optional[ErrorMessageResolver]:
        return self._delegated.matches_emr(model)

    def matches_w_trace(self, model: LineMatcherLine) -> MatchingResult:
        return self._delegated.matches_w_trace(model)
