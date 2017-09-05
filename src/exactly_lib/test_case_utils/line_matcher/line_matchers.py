from exactly_lib.type_system.logic.line_matcher import LineMatcher


class LineMatcherRegex(LineMatcher):
    """Matches lines that matches a given regex."""

    def __init__(self, compiled_regular_expression):
        self._compiled_regular_expression = compiled_regular_expression

    @property
    def regex_pattern_string(self) -> str:
        return self._compiled_regular_expression.pattern

    def matches(self, line: str) -> bool:
        return bool(self._compiled_regular_expression.search(line))


class LineMatcherStructureVisitor:
    """
    Visits all variants of :class:`FileMatcher`.

    The existence of this class means that the structure of :class:`FileMatcher`s
    is fixed. The reason for this is to, among other things, support optimizations
    of selectors.
    """

    def visit(self, line_matcher: LineMatcher):
        if isinstance(line_matcher, LineMatcherRegex):
            return self.visit_regex(line_matcher)
        else:
            raise TypeError('Unknown {}: {}'.format(LineMatcher,
                                                    str(line_matcher)))

    def visit_regex(self, matcher: LineMatcherRegex):
        raise NotImplementedError('abstract method')
