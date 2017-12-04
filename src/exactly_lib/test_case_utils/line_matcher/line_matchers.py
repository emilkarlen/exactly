from exactly_lib.help_texts import expression
from exactly_lib.test_case_utils.condition.integer.integer_matcher import IntegerMatcher
from exactly_lib.type_system.logic.line_matcher import LineMatcher


class LineMatcherConstant(LineMatcher):
    """Matcher with constant result."""

    def __init__(self, result: bool):
        self._result = result

    @property
    def option_description(self) -> str:
        return 'any file' if self._result else 'no file'

    @property
    def result_constant(self) -> bool:
        return self._result

    def matches(self, line: str) -> bool:
        return self._result


class LineMatcherRegex(LineMatcher):
    """Matches lines who's contents matches a given regex."""

    def __init__(self, compiled_regular_expression):
        self._compiled_regular_expression = compiled_regular_expression

    @property
    def option_description(self) -> str:
        return 'name matches regex ' + self.regex_pattern_string

    @property
    def regex_pattern_string(self) -> str:
        return self._compiled_regular_expression.pattern

    def matches(self, line: tuple) -> bool:
        return bool(self._compiled_regular_expression.search(line[1]))


class LineMatcherLineNumber(LineMatcher):
    """Matches lines who's line number satisfy a given condition."""

    def __init__(self, integer_matcher: IntegerMatcher):
        self._integer_matcher = integer_matcher

    @property
    def option_description(self) -> str:
        return self._integer_matcher.option_description

    def matches(self, line: tuple) -> bool:
        return self._integer_matcher.matches(line[0])


class LineMatcherNot(LineMatcher):
    """Matcher that negates a given matcher."""

    def __init__(self, matcher: LineMatcher):
        self._matcher = matcher

    @property
    def option_description(self) -> str:
        return expression.NOT_OPERATOR_NAME + ' ' + self._matcher.option_description

    @property
    def negated_matcher(self) -> LineMatcher:
        return self._matcher

    def matches(self, line: tuple) -> bool:
        return not self._matcher.matches(line)


class LineMatcherAnd(LineMatcher):
    """Matcher that and:s a list of matchers."""

    def __init__(self, matchers: list):
        self._matchers = tuple(matchers)

    @property
    def option_description(self) -> str:
        op = ' ' + expression.AND_OPERATOR_NAME + ' '
        return '({})'.format(op.join(map(lambda fm: fm.option_description, self.matchers)))

    @property
    def matchers(self) -> list:
        return list(self._matchers)

    def matches(self, line: str) -> bool:
        return all([matcher.matches(line)
                    for matcher in self._matchers])


class LineMatcherOr(LineMatcher):
    """Matcher that or:s a list of matchers."""

    def __init__(self, matchers: list):
        self._matchers = tuple(matchers)

    @property
    def option_description(self) -> str:
        op = ' ' + expression.OR_OPERATOR_NAME + ' '
        return '({})'.format(op.join(map(lambda fm: fm.option_description, self.matchers)))

    @property
    def matchers(self) -> list:
        return list(self._matchers)

    def matches(self, line: str) -> bool:
        return any([matcher.matches(line)
                    for matcher in self._matchers])


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
