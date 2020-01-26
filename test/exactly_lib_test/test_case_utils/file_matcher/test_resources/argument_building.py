from abc import ABC
from typing import List, Optional

from exactly_lib.definitions import expression
from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.test_case_utils.string_matcher.test_resources import arguments_building2 as sm_args
from exactly_lib_test.test_resources import matcher_argument
from exactly_lib_test.test_resources.arguments_building import OptionArgument
from exactly_lib_test.test_resources.matcher_argument import MatcherArgument
from exactly_lib_test.test_resources.strings import WithToString


class FileMatcherArg(MatcherArgument, ABC):
    pass


class Custom(FileMatcherArg):
    """Argument for building invalid syntax"""

    def __init__(self, matcher: str):
        self.matcher = matcher

    @property
    def elements(self) -> List:
        return [self.matcher]


class SymbolReference(FileMatcherArg):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    @property
    def elements(self) -> List:
        return [self.symbol_name]


class Type(FileMatcherArg):
    def __init__(self, file_type: file_properties.FileType):
        self.file_type = file_type

    @property
    def elements(self) -> List:
        return [
            file_matcher.TYPE_MATCHER_NAME,
            file_properties.TYPE_INFO[self.file_type].type_argument,
        ]


class NameVariant(matcher_argument.MatcherArgComponent, ABC):
    pass


class NameGlobPatternVariant(NameVariant):
    def __init__(self, pattern: str):
        self.pattern = pattern

    @property
    def elements(self) -> List:
        return [matcher_argument.quote_if_unquoted_with_space(self.pattern)]


class NameRegexVariant(NameVariant):
    def __init__(self, regex: matcher_argument.NameRegexComponent):
        self.regex = regex

    @property
    def elements(self) -> List:
        regex_option_str = option_syntax.option_syntax(parse_file_matcher.REG_EX_OPTION)
        return [regex_option_str] + self.regex.elements


class Name(FileMatcherArg):
    def __init__(self, name_matcher: NameVariant):
        self.name_matcher = name_matcher

    @property
    def elements(self) -> List:
        return [file_matcher.NAME_MATCHER_NAME] + self.name_matcher.elements


class FileContents(FileMatcherArg):
    def __init__(self, string_matcher: sm_args.StringMatcherArg):
        self.string_matcher = string_matcher

    @property
    def elements(self) -> List:
        return [
            parse_file_matcher.REGULAR_FILE_CONTENTS,
            self.string_matcher,
        ]


class DirContents(FileMatcherArg):
    def __init__(self, files_matcher: MatcherArgument):
        self.files_matcher = files_matcher

    @property
    def elements(self) -> List:
        return [
            parse_file_matcher.DIR_CONTENTS,
            self.files_matcher,
        ]


class InvalidDirContents(FileMatcherArg):
    def __init__(self,
                 invalid_argument: WithToString,
                 ):
        self.invalid_argument = invalid_argument

    @property
    def elements(self) -> List:
        return [
            parse_file_matcher.DIR_CONTENTS,
            self.invalid_argument,
        ]


class InvalidDirContentsRecursive(FileMatcherArg):
    def __init__(self,
                 invalid_argument: WithToString,
                 ):
        self.invalid_argument = invalid_argument

    @property
    def elements(self) -> List:
        return [
            parse_file_matcher.DIR_CONTENTS,
            OptionArgument(file_or_dir_contents.RECURSIVE_OPTION.name),
            self.invalid_argument,
        ]


class DirContentsRecursive(FileMatcherArg):
    def __init__(self,
                 files_matcher: MatcherArgument,
                 min_depth: Optional[WithToString] = None,
                 max_depth: Optional[WithToString] = None,
                 ):
        self.files_matcher = files_matcher
        self.min_depth = min_depth
        self.max_depth = max_depth

    @property
    def elements(self) -> List:
        ret_val = [
            parse_file_matcher.DIR_CONTENTS,
            OptionArgument(file_or_dir_contents.RECURSIVE_OPTION.name),
        ]

        if self.min_depth is not None:
            ret_val += [
                OptionArgument(file_or_dir_contents.MIN_DEPTH_OPTION.name),
                str(self.min_depth),
            ]

        if self.max_depth is not None:
            ret_val += [
                OptionArgument(file_or_dir_contents.MAX_DEPTH_OPTION.name),
                str(self.max_depth),
            ]

        ret_val.append(self.files_matcher)

        return ret_val


class Not(FileMatcherArg):
    def __init__(self, matcher: FileMatcherArg):
        self.matcher = matcher

    @property
    def elements(self) -> List:
        return [
            expression.NOT_OPERATOR_NAME,
            self.matcher,
        ]


class _BinaryOperatorBase(FileMatcherArg):
    def __init__(self,
                 operator_name: str,
                 matchers: List[FileMatcherArg]):
        self.matchers = matchers
        self.operator_name = operator_name
        matcher_argument.value_error_if_empty(operator_name, matchers)

    @property
    def elements(self) -> List:
        return matcher_argument.concat_and_intersperse_non_empty_list(self.operator_name,
                                                                      self.matchers)


class And(_BinaryOperatorBase):
    def __init__(self, matchers: List[FileMatcherArg]):
        super().__init__(expression.AND_OPERATOR_NAME, matchers)


class Or(_BinaryOperatorBase):
    def __init__(self, matchers: List[FileMatcherArg]):
        super().__init__(expression.OR_OPERATOR_NAME, matchers)


class WithOptionalNegation:
    def __init__(self, matcher: FileMatcherArg):
        self.matcher = matcher

    def get(self, expectation_type: ExpectationType) -> FileMatcherArg:
        if expectation_type is ExpectationType.POSITIVE:
            return self.matcher
        else:
            return Not(self.matcher)
