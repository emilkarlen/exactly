from typing import Optional, List
from typing import Pattern

from exactly_lib.definitions.primitives import line_matcher
from exactly_lib.test_case_utils.condition.integer.integer_matcher import IntegerMatcher
from exactly_lib.test_case_utils.err_msg2 import trace_details
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.impls import combinator_matchers
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.type_system.trace import trace


class LineMatcherDelegatedToMatcherWTrace(LineMatcher):
    def __init__(self, delegated: MatcherWTraceAndNegation[LineMatcherLine]):
        self._delegated = delegated

    @property
    def name(self) -> str:
        return self._delegated.name

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
        self._result = result

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


class LineMatcherRegex(LineMatcher):
    """Matches lines who's contents matches a given regex."""

    def __init__(self, compiled_regular_expression: Pattern):
        self._compiled_regular_expression = compiled_regular_expression
        self._regex_detail_renderer = trace_details.DetailsRendererOfConstant(
            trace.StringDetail(self.option_description)
        )

    @property
    def name(self) -> str:
        return line_matcher.REGEX_MATCHER_NAME

    @property
    def option_description(self) -> str:
        return self.name + ' ' + self.regex_pattern_string

    @property
    def regex_pattern_string(self) -> str:
        return self._compiled_regular_expression.pattern

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        return self._new_tb() \
            .append_details(self._regex_detail_renderer) \
            .build_result(self.matches(line))

    def matches(self, line: LineMatcherLine) -> bool:
        return bool(self._compiled_regular_expression.search(line[1]))


class LineMatcherLineNumber(LineMatcher):
    """Matches lines who's line number satisfy a given condition."""

    def __init__(self, integer_matcher: IntegerMatcher):
        self._integer_matcher = integer_matcher
        self._detail_renderer_of_expected = trace_details.DetailsRendererOfConstant(
            trace.StringDetail(self.option_description)
        )

    @property
    def name(self) -> str:
        return line_matcher.LINE_NUMBER_MATCHER_NAME

    @property
    def option_description(self) -> str:
        return self._integer_matcher.option_description

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        is_match = self.matches(line)

        return self._new_tb() \
            .append_details(self._detail_renderer_of_expected) \
            .build_result(is_match)

    def matches(self, line: LineMatcherLine) -> bool:
        return self._integer_matcher.matches(line[0])


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
