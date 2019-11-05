from typing import Optional, Match, Sequence
from typing import Pattern

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.test_case_utils.description_tree import custom_details, bool_trace_rendering
from exactly_lib.test_case_utils.line_matcher import trace_rendering
from exactly_lib.test_case_utils.line_matcher.impl import delegated
from exactly_lib.test_case_utils.line_matcher.impl.impl_base_classes import LineMatcherImplBase
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.description_tree import details, renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail


def negation(matcher: LineMatcher) -> LineMatcher:
    return delegated.LineMatcherDelegatedToMatcher(combinator_matchers.Negation(matcher))


def conjunction(matchers: Sequence[LineMatcher]) -> LineMatcher:
    return delegated.LineMatcherDelegatedToMatcher(combinator_matchers.Conjunction(matchers))


def disjunction(matchers: Sequence[LineMatcher]) -> LineMatcher:
    return delegated.LineMatcherDelegatedToMatcher(combinator_matchers.Disjunction(matchers))


class LineMatcherConstant(LineMatcherImplBase):
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

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        return self._new_tb() \
            .build_result(self.matches(line))

    def matches(self, line: LineMatcherLine) -> bool:
        return self._result


class LineMatcherRegex(LineMatcherImplBase):
    """Matches lines who's contents matches a given regex."""

    NAME = ' '.join((
        line_matcher.REGEX_MATCHER_NAME,
        syntax_elements.REGEX_SYNTAX_ELEMENT.singular_name,
    ))

    @staticmethod
    def new_structure_tree(regex: DetailsRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            LineMatcherRegex.NAME,
            None,
            (custom_details.regex_with_config_renderer(False, regex),),
            (),
        )

    def __init__(self, compiled_regular_expression: Pattern[str]):
        super().__init__()
        self._expected = custom_details.regex_with_config_renderer(
            False,
            custom_details.PatternRenderer(compiled_regular_expression))

        self._compiled_regular_expression = compiled_regular_expression

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def option_description(self) -> str:
        return self.name + ' ' + self.regex_pattern_string

    @property
    def regex_pattern_string(self) -> str:
        return self._compiled_regular_expression.pattern

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        tb = self._tb_for_line(line)

        match = self.matches(line)
        if match is not None:
            tb.append_details(
                custom_details.match(custom_details.PatternMatchRenderer(match))
            )

        return tb.build_result(match is not None)

    def matches(self, line: LineMatcherLine) -> Optional[Match]:
        return self._compiled_regular_expression.search(line[1])

    def _new_tb_with_expected(self) -> TraceBuilder:
        return self._new_tb().append_details(self._expected_detail_renderer)

    def _structure(self) -> StructureRenderer:
        return renderers.header_and_detail(
            self.name,
            self._expected,
        )

    def _tb_for_line(self, line: LineMatcherLine) -> TraceBuilder:
        return TraceBuilder(self.name).append_details(
            _ExpectedAndActualRenderer(self._expected, line)
        )


class _ExpectedAndActualRenderer(DetailsRenderer):
    def __init__(self,
                 expected: DetailsRenderer,
                 actual: LineMatcherLine,
                 ):
        self._expected = expected
        self._actual = actual

    def render(self) -> Sequence[Detail]:
        expected_renderer = custom_details.expected(self._expected)

        actual_renderer = custom_details.actual(
            trace_rendering.LineMatcherLineRenderer(self._actual)
        )
        ret_val = list(expected_renderer.render())

        ret_val += actual_renderer.render()

        return ret_val
