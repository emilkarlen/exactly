from abc import ABC, abstractmethod
from typing import List, Optional, Sequence

from exactly_lib.definitions import logic
from exactly_lib.definitions.primitives import file_matcher
from exactly_lib.definitions.primitives import file_or_dir_contents
from exactly_lib.definitions.test_case import file_check_properties
from exactly_lib.impls import file_properties
from exactly_lib.impls.types.file_matcher.impl.names import defs
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib_test.impls.types.string_matcher.test_resources import arguments_building2 as sm_args
from exactly_lib_test.test_resources import argument_renderer
from exactly_lib_test.test_resources import matcher_argument
from exactly_lib_test.test_resources.argument_renderer import OptionArgument, ArgumentElementsRenderer
from exactly_lib_test.test_resources.arguments.arguments_building import ArgumentElements
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


class SymbolReferenceWReferenceSyntax(FileMatcherArg):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    @property
    def elements(self) -> List:
        return [symbol_reference_syntax_for_name(self.symbol_name)]


class Type(FileMatcherArg):
    def __init__(self, file_type: file_properties.FileType):
        self.file_type = file_type

    @property
    def elements(self) -> List:
        return [
            file_matcher.TYPE_MATCHER_NAME,
            file_properties.TYPE_INFO[self.file_type].type_argument,
        ]


class BinaryOperator(FileMatcherArg):
    def __init__(self,
                 operator: str,
                 operands: Sequence[FileMatcherArg]):
        self.operator = operator
        self.operands = operands

    @property
    def elements(self) -> List:
        return argument_renderer.elements_for_binary_operator_arg(self.operator, self.operands)


def conjunction(operands: Sequence[FileMatcherArg]) -> BinaryOperator:
    return BinaryOperator(logic.AND_OPERATOR_NAME, operands)


def disjunction(operands: Sequence[FileMatcherArg]) -> BinaryOperator:
    return BinaryOperator(logic.OR_OPERATOR_NAME, operands)


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

    @staticmethod
    def of(regex: str,
           ignore_case: bool = False,
           ) -> 'NameRegexVariant':
        return NameRegexVariant(
            matcher_argument.NameRegexComponent(regex, ignore_case)
        )

    @property
    def elements(self) -> List:
        regex_option_str = defs.REG_EX_OPERATOR.name
        return [regex_option_str] + self.regex.elements


class Name(FileMatcherArg):
    def __init__(self, name_matcher: NameVariant):
        self.name_matcher = name_matcher

    @property
    def elements(self) -> List:
        return [file_matcher.NAME_MATCHER_NAME] + self.name_matcher.elements


class Stem(FileMatcherArg):
    def __init__(self, name_matcher: NameVariant):
        self.name_matcher = name_matcher

    @property
    def elements(self) -> List:
        return [file_matcher.STEM_MATCHER_NAME] + self.name_matcher.elements


class Suffix(FileMatcherArg):
    def __init__(self, name_matcher: NameVariant):
        self.name_matcher = name_matcher

    @property
    def elements(self) -> List:
        return [file_matcher.SUFFIX_MATCHER_NAME] + self.name_matcher.elements


class Suffixes(FileMatcherArg):
    def __init__(self, name_matcher: NameVariant):
        self.name_matcher = name_matcher

    @property
    def elements(self) -> List:
        return [file_matcher.SUFFIXES_MATCHER_NAME] + self.name_matcher.elements


class Path(FileMatcherArg):
    def __init__(self, name_matcher: NameVariant):
        self.name_matcher = name_matcher

    @property
    def elements(self) -> List:
        return [file_matcher.WHOLE_PATH_MATCHER_NAME] + self.name_matcher.elements


class FileContents(FileMatcherArg):
    def __init__(self, string_matcher: sm_args.StringMatcherArg):
        self.string_matcher = string_matcher

    @property
    def elements(self) -> List:
        return [
            file_check_properties.REGULAR_FILE_CONTENTS,
            self.string_matcher,
        ]


class DirContents(FileMatcherArg):
    def __init__(self, files_matcher: MatcherArgument):
        self.files_matcher = files_matcher

    @property
    def elements(self) -> List:
        return [
            file_check_properties.DIR_CONTENTS,
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
            file_check_properties.DIR_CONTENTS,
            self.invalid_argument,
        ]


class DirContentsRecursive(FileMatcherArg):
    def __init__(self,
                 files_matcher: MatcherArgument,
                 min_depth: Optional[WithToString] = None,
                 max_depth: Optional[WithToString] = None,
                 ):
        self.files_matcher = files_matcher
        self.recursive_args = DirContentsRecursiveArgs(
            files_matcher,
            min_depth,
            max_depth,
        )

    @property
    def elements(self) -> List:
        return [
            file_check_properties.DIR_CONTENTS,
            self.recursive_args,
        ]


class DirContentsGeneric(FileMatcherArg):
    def __init__(self,
                 arguments: ArgumentElementsRenderer,
                 ):
        self.arguments = arguments

    @property
    def elements(self) -> List:
        return ([file_check_properties.DIR_CONTENTS]
                + self.arguments.elements
                )


class DirContentsRecursiveInvalidOptionArgs(FileMatcherArg):
    def __init__(self,
                 invalid_option_name: str,
                 ):
        self.invalid_option_name = invalid_option_name

    @property
    def elements(self) -> List:
        return [
            file_check_properties.DIR_CONTENTS,
            OptionArgument(file_or_dir_contents.RECURSIVE_OPTION.name),
            OptionArgument(a.OptionName(self.invalid_option_name)),
            SymbolReference('valid_files_matcher_arg'),
        ]


class DirContentsRecursiveArgs(FileMatcherArg):
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


class PathArgumentPositionArgument(ABC):
    @abstractmethod
    def arguments(self) -> List[str]:
        pass


class PathArgumentPositionDefault(PathArgumentPositionArgument):
    def arguments(self) -> List[str]:
        return []


class PathArgumentPositionLast(PathArgumentPositionArgument):
    def arguments(self) -> List[str]:
        return [
            option_syntax.option_syntax(file_matcher.PROGRAM_ARG_OPTION__LAST.name)
        ]


class PathArgumentPositionMarker(PathArgumentPositionArgument):
    def __init__(self, marker: str):
        self.marker = marker

    def arguments(self) -> List[str]:
        return [
            option_syntax.option_syntax(file_matcher.PROGRAM_ARG_OPTION__MARKER.name),
            self.marker
        ]


class RunProgram(FileMatcherArg):
    def __init__(self,
                 program: ArgumentElements,
                 path_arg_position: PathArgumentPositionArgument = PathArgumentPositionDefault(),
                 ):
        self.program = program
        self.path_arg_position = path_arg_position

    @property
    def as_argument_elements(self) -> ArgumentElements:
        run_primitive = ArgumentElements(
            [file_matcher.PROGRAM_MATCHER_NAME] + self.path_arg_position.arguments()
        )
        return run_primitive.append_to_first_and_following_lines(self.program)

    def __str__(self):
        return self.as_argument_elements.as_arguments.as_single_string

    @property
    def elements(self) -> List[WithToString]:
        return self.as_argument_elements.as_elements


class Not(FileMatcherArg):
    def __init__(self, matcher: FileMatcherArg):
        self.matcher = matcher

    @property
    def elements(self) -> List:
        return [
            logic.NOT_OPERATOR_NAME,
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
        super().__init__(logic.AND_OPERATOR_NAME, matchers)


class Or(_BinaryOperatorBase):
    def __init__(self, matchers: List[FileMatcherArg]):
        super().__init__(logic.OR_OPERATOR_NAME, matchers)


class WithOptionalNegation:
    def __init__(self, matcher: FileMatcherArg):
        self.matcher = matcher

    def get(self, expectation_type: ExpectationType) -> FileMatcherArg:
        if expectation_type is ExpectationType.POSITIVE:
            return self.matcher
        else:
            return Not(self.matcher)
