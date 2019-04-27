from exactly_lib.test_case_utils.file_matcher.file_matchers import FileMatcherNot, FileMatcherAnd, FileMatcherOr, FileMatcherConstant
from exactly_lib.test_case_utils.file_matcher.impl.name_regex import FileMatcherBaseNameRegExPattern
from exactly_lib.test_case_utils.file_matcher.impl.name_glob_pattern import FileMatcherNameGlobPattern
from exactly_lib.test_case_utils.file_matcher.impl.file_type import FileMatcherType
from exactly_lib.type_system.logic.file_matcher import FileMatcher


class FileMatcherStructureVisitor:
    """
    Visits all variants of :class:`FileMatcher`.

    The existence of this class means that the structure of :class:`FileMatcher`s
    is fixed. The reason for this is to, among other things, support optimizations
    of selectors.

    REFACT 2019-04-26: This class should be removed - there should be
    no need for a fixed hierarchy of FileMatcher.s.
    """

    def visit(self, matcher: FileMatcher):
        if isinstance(matcher, FileMatcherNameGlobPattern):
            return self.visit_name_glob_pattern(matcher)
        if isinstance(matcher, FileMatcherBaseNameRegExPattern):
            return self.visit_name_reg_ex_pattern(matcher)
        if isinstance(matcher, FileMatcherType):
            return self.visit_type(matcher)
        if isinstance(matcher, FileMatcherNot):
            return self.visit_not(matcher)
        if isinstance(matcher, FileMatcherAnd):
            return self.visit_and(matcher)
        if isinstance(matcher, FileMatcherOr):
            return self.visit_or(matcher)
        if isinstance(matcher, FileMatcherConstant):
            return self.visit_constant(matcher)
        else:
            raise TypeError('Unknown {}: {}'.format(FileMatcher,
                                                    str(matcher)))

    def visit_constant(self, matcher: FileMatcherConstant):
        raise NotImplementedError('abstract method')

    def visit_name_glob_pattern(self, matcher: FileMatcherNameGlobPattern):
        raise NotImplementedError('abstract method')

    def visit_name_reg_ex_pattern(self, matcher: FileMatcherBaseNameRegExPattern):
        raise NotImplementedError('abstract method')

    def visit_type(self, matcher: FileMatcherType):
        raise NotImplementedError('abstract method')

    def visit_not(self, matcher: FileMatcherNot):
        raise NotImplementedError('abstract method')

    def visit_and(self, matcher: FileMatcherAnd):
        raise NotImplementedError('abstract method')

    def visit_or(self, matcher: FileMatcherOr):
        raise NotImplementedError('abstract method')
