from typing import Sequence

from exactly_lib.definitions import expression
from exactly_lib.test_case_utils.condition.integer.integer_matcher import IntegerMatcher
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherLine
from exactly_lib.type_system.trace import trace
from exactly_lib.type_system.trace import trace_rendering
from exactly_lib.type_system.trace.trace_rendering import MatchingResult


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

    def __init__(self, compiled_regular_expression):
        self._compiled_regular_expression = compiled_regular_expression
        self._regex_detail_renderer = trace_rendering.DetailRendererOfConstant(
            trace.StringDetail(self.option_description)
        )

    @property
    def name(self) -> str:
        return 'matches (TODO use const)'

    @property
    def option_description(self) -> str:
        return self.name + ' ' + self.regex_pattern_string

    @property
    def regex_pattern_string(self) -> str:
        return self._compiled_regular_expression.pattern

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        return self._new_tb() \
            .append_detail(self._regex_detail_renderer) \
            .build(self.matches(line))

    def matches(self, line: LineMatcherLine) -> bool:
        return bool(self._compiled_regular_expression.search(line[1]))


class LineMatcherLineNumber(LineMatcher):
    """Matches lines who's line number satisfy a given condition."""

    def __init__(self, integer_matcher: IntegerMatcher):
        self._integer_matcher = integer_matcher
        self._detail_renderer_of_expected = trace_rendering.DetailRendererOfConstant(
            trace.StringDetail(self.option_description)
        )

    @property
    def name(self) -> str:
        return 'line-num (TODO use const)'

    @property
    def option_description(self) -> str:
        return self._integer_matcher.option_description

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        is_match = self.matches(line)

        return self._new_tb() \
            .append_detail(self._detail_renderer_of_expected) \
            .build_result(is_match)

    def matches(self, line: LineMatcherLine) -> bool:
        return self._integer_matcher.matches(line[0])


class LineMatcherNot(LineMatcher):
    """Matcher that negates a given matcher."""

    def __init__(self, matcher: LineMatcher):
        self._matcher = matcher

    @property
    def name(self) -> str:
        return expression.NOT_OPERATOR_NAME

    @property
    def option_description(self) -> str:
        return expression.NOT_OPERATOR_NAME + ' ' + self._matcher.option_description

    @property
    def negated_matcher(self) -> LineMatcher:
        return self._matcher

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        result = self._matcher.matches3(line)

        return self._new_tb() \
            .append_child(result.trace) \
            .build_result(not result.value)

    def matches(self, line: LineMatcherLine) -> bool:
        return not self._matcher.matches(line)


class LineMatcherAnd(LineMatcher):
    """Matcher that and:s a list of matchers."""

    def __init__(self, matchers: Sequence[LineMatcher]):
        self._matchers = tuple(matchers)

    @property
    def name(self) -> str:
        return expression.AND_OPERATOR_NAME

    @property
    def option_description(self) -> str:
        op = ' ' + expression.AND_OPERATOR_NAME + ' '
        return '({})'.format(op.join(map(lambda fm: fm.option_description, self.matchers)))

    @property
    def matchers(self) -> Sequence[LineMatcher]:
        return list(self._matchers)

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        tb = self._new_tb()

        for sub_matcher in self._matchers:
            result = sub_matcher.matches_w_trace(line)
            tb.append_child(result.trace)
            if not result.value:
                return tb.build_result(False)

        return tb.build_result(True)

    def matches(self, line: LineMatcherLine) -> bool:
        return all((matcher.matches(line)
                    for matcher in self._matchers))


class LineMatcherOr(LineMatcher):
    """Matcher that or:s a list of matchers."""

    def __init__(self, matchers: Sequence[LineMatcher]):
        self._matchers = tuple(matchers)

    @property
    def name(self) -> str:
        return expression.OR_OPERATOR_NAME

    @property
    def option_description(self) -> str:
        op = ' ' + expression.OR_OPERATOR_NAME + ' '
        return '({})'.format(op.join(map(lambda fm: fm.option_description, self.matchers)))

    @property
    def matchers(self) -> Sequence[LineMatcher]:
        return list(self._matchers)

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        tb = self._new_tb()

        for sub_matcher in self._matchers:
            result = sub_matcher.matches_w_trace(line)
            tb.append_child(result.trace)
            if result.value:
                return tb.build_result(True)

        return tb.build_result(False)

    def matches(self, line: LineMatcherLine) -> bool:
        return any((matcher.matches(line)
                    for matcher in self._matchers))


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
