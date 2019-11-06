from typing import Sequence, Optional

from exactly_lib.test_case_utils.description_tree import bool_trace_rendering
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.line_matcher.impl import delegated
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.description_tree import details, renderers


def negation(matcher: LineMatcher) -> LineMatcher:
    return delegated.LineMatcherDelegatedToMatcher(combinator_matchers.Negation(matcher))


def conjunction(matchers: Sequence[LineMatcher]) -> LineMatcher:
    return delegated.LineMatcherDelegatedToMatcher(combinator_matchers.Conjunction(matchers))


def disjunction(matchers: Sequence[LineMatcher]) -> LineMatcher:
    return delegated.LineMatcherDelegatedToMatcher(combinator_matchers.Disjunction(matchers))


class LineMatcherConstant(WithCachedTreeStructureDescriptionBase,
                          LineMatcher,
                          ):
    """Matcher with constant result."""

    def __init__(self, result: bool):
        super().__init__()
        self._result = result

    def _structure(self) -> StructureRenderer:
        return renderers.header_and_detail(
            'constant',
            details.String(bool_trace_rendering.bool_string(self._result))
        )

    @property
    def name(self) -> str:
        return self.option_description

    @property
    def option_description(self) -> str:
        return 'any line' if self._result else 'no line'

    @property
    def result_constant(self) -> bool:
        return self._result

    @property
    def negation(self) -> LineMatcher:
        return LineMatcherConstant(not self._result)

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        return TraceBuilder(self.name) \
            .build_result(self.matches(line))

    def matches_emr(self, line: LineMatcherLine) -> Optional[ErrorMessageResolver]:
        raise NotImplementedError('deprecated')

    def matches(self, line: LineMatcherLine) -> bool:
        return self._result
