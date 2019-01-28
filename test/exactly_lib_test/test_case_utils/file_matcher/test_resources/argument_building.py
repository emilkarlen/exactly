from typing import List

from exactly_lib.definitions import expression
from exactly_lib.test_case_utils import file_properties
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import arguments_building2 as sm_args
from . import argument_syntax


class FileMatcherArg:
    """Generate source using __str__"""
    pass


class Type(FileMatcherArg):
    def __init__(self, file_type: file_properties.FileType):
        self.file_type = file_type

    def __str__(self):
        return argument_syntax.type_matcher_of(self.file_type)


class NameGlobPattern(FileMatcherArg):
    def __init__(self, pattern: str):
        self.pattern = pattern

    def __str__(self):
        return argument_syntax.name_glob_pattern_matcher_of(self.pattern)


class Contents(FileMatcherArg):
    def __init__(self, string_matcher: sm_args.StringMatcherArg):
        self.string_matcher = string_matcher

    def __str__(self):
        return argument_syntax.contents_matcher_of(str(self.string_matcher))


class And(FileMatcherArg):
    def __init__(self, matchers: List[FileMatcherArg]):
        self.matchers = matchers

    def __str__(self):
        return argument_syntax.and_([str(matcher) for matcher in self.matchers])


class Not(FileMatcherArg):
    def __init__(self, matcher: FileMatcherArg):
        self.matcher = matcher

    def __str__(self):
        return expression.NOT_OPERATOR_NAME + ' ' + str(self.matcher)


class WithOptionalNegation:
    def __init__(self, matcher: FileMatcherArg):
        self.matcher = matcher

    def get(self, expectation_type: ExpectationType) -> FileMatcherArg:
        if expectation_type is ExpectationType.POSITIVE:
            return self.matcher
        else:
            return Not(self.matcher)
