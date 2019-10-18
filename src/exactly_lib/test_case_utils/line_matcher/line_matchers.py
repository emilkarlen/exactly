from abc import ABC
from typing import Optional, List, Match, Sequence
from typing import Pattern

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.test_case_utils.condition.integer.integer_matcher import IntegerMatcher
from exactly_lib.test_case_utils.description_tree import custom_details, bool_trace_rendering
from exactly_lib.test_case_utils.line_matcher import trace_rendering
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.description_tree import details, renderers
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.description_tree.tree import Detail


class LineMatcherDelegatedToMatcherWTrace(LineMatcher):
    def __init__(self, delegated: MatcherWTraceAndNegation[LineMatcherLine]):
        super().__init__()
        self._delegated = delegated

    @property
    def name(self) -> str:
        return self._delegated.name

    def _structure(self) -> StructureRenderer:
        return self._delegated.structure()

    @property
    def option_description(self) -> str:
        return self._delegated.option_description

    def matches(self, model: LineMatcherLine) -> bool:
        return self._delegated.matches(model)

    def matches_emr(self, model: LineMatcherLine) -> Optional[ErrorMessageResolver]:
        return self._delegated.matches_emr(model)

    def matches_w_trace(self, model: LineMatcherLine) -> MatchingResult:
        return self._delegated.matches_w_trace(model)


class LineMatcherNot(LineMatcherDelegatedToMatcherWTrace):
    """Matcher that negates a given matcher."""

    def __init__(self, matcher: LineMatcher):
        self._matcher = matcher
        super().__init__(combinator_matchers.Negation(matcher))

    @property
    def negated_matcher(self) -> LineMatcher:
        return self._matcher


class LineMatcherAnd(LineMatcherDelegatedToMatcherWTrace):
    """Matcher that and:s a list of matchers."""

    def __init__(self, matchers: List[LineMatcher]):
        self._matchers = matchers
        super().__init__(combinator_matchers.Conjunction(matchers))

    @property
    def matchers(self) -> List[LineMatcher]:
        return self._matchers


class LineMatcherOr(LineMatcherDelegatedToMatcherWTrace):
    """Matcher that or:s a list of matchers."""

    def __init__(self, matchers: List[LineMatcher]):
        self._matchers = matchers
        super().__init__(combinator_matchers.Disjunction(matchers))

    @property
    def matchers(self) -> List[LineMatcher]:
        return self._matchers


class LineMatcherConstant(LineMatcher):
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


class _LineMatcherWExpectedAndActualBase(LineMatcher, ABC):
    def __init__(self, expected: DetailsRenderer):
        super().__init__()
        self._expected = expected

    def _structure(self) -> StructureRenderer:
        return renderers.header_and_detail(
            self.name,
            self._expected,
        )

    def _tb_for_line(self, line: LineMatcherLine) -> TraceBuilder:
        return TraceBuilder(self.name).append_details(
            _ExpectedAndActualRenderer(self._expected, line)
        )


class LineMatcherRegex(_LineMatcherWExpectedAndActualBase):
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
            (regex,),
            (),
        )

    def __init__(self, compiled_regular_expression: Pattern):
        super().__init__(custom_details.PatternRenderer(False, compiled_regular_expression))
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


class LineMatcherLineNumber(_LineMatcherWExpectedAndActualBase):
    """Matches lines who's line number satisfy a given condition."""

    NAME = ' '.join((line_matcher.LINE_NUMBER_MATCHER_NAME,
                     syntax_elements.INTEGER_COMPARISON_SYNTAX_ELEMENT.singular_name))

    @staticmethod
    def new_structure_tree(line_number_matcher: DetailsRenderer) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            LineMatcherLineNumber.NAME,
            None,
            (line_number_matcher,),
            (),
        )

    def __init__(self, integer_matcher: IntegerMatcher):
        super().__init__(details.String(integer_matcher.option_description))
        self._integer_matcher = integer_matcher

    @property
    def name(self) -> str:
        return self.NAME

    @property
    def option_description(self) -> str:
        return self._integer_matcher.option_description

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        tb = self._tb_for_line(line)

        is_match = self.matches(line)

        return tb.build_result(is_match)

    def matches(self, line: LineMatcherLine) -> bool:
        return self._integer_matcher.matches(line[0])


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


class LineMatcherStructureVisitor:
    """
    Visits all variants of :class:`LineMatcher`.

    The existence of this class means that the structure of :class:`LineMatcher`s
    is fixed. The reason for this is to, among other things, support optimizations
    of selectors.
    """

    def visit(self, line_matcher: LineMatcher):
        if isinstance(line_matcher, LineMatcherRegex):
            return self.visit_regex(line_matcher)
        if isinstance(line_matcher, LineMatcherLineNumber):
            return self.visit_line_number(line_matcher)
        if isinstance(line_matcher, LineMatcherConstant):
            return self.visit_constant(line_matcher)
        if isinstance(line_matcher, LineMatcherNot):
            return self.visit_not(line_matcher)
        if isinstance(line_matcher, LineMatcherAnd):
            return self.visit_and(line_matcher)
        if isinstance(line_matcher, LineMatcherOr):
            return self.visit_or(line_matcher)
        else:
            raise TypeError('Unknown {}: {}'.format(LineMatcher,
                                                    str(line_matcher)))

    def visit_constant(self, matcher: LineMatcherConstant):
        raise NotImplementedError('abstract method')

    def visit_regex(self, matcher: LineMatcherRegex):
        raise NotImplementedError('abstract method')

    def visit_line_number(self, matcher: LineMatcherLineNumber):
        raise NotImplementedError('abstract method')

    def visit_not(self, matcher: LineMatcherNot):
        raise NotImplementedError('abstract method')

    def visit_and(self, matcher: LineMatcherAnd):
        raise NotImplementedError('abstract method')

    def visit_or(self, matcher: LineMatcherOr):
        raise NotImplementedError('abstract method')
