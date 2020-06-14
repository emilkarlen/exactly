from abc import ABC
from typing import Optional, Sequence, List

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case_utils.files_condition import syntax
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_building import FileMatcherArg
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.test_resources.arguments_building import Singleton, \
    FromArgumentElementsBase
from exactly_lib_test.test_resources.strings import WithToString


class FileCondition:
    def __init__(self,
                 name: WithToString,
                 condition: Optional[FileMatcherArg] = None,
                 ):
        self.name = name
        self.condition = condition

    @property
    def as_argument_elements(self) -> ArgumentElements:
        fn = ArgumentElements([self.name])
        return (
            fn
            if self.condition is None
            else
            fn.followed_by(self.condition.as_argument_elements, [syntax.FILE_MATCHER_SEPARATOR])
        )


BEGIN_BRACE_RENDERER = Singleton(syntax.BEGIN_BRACE)

END_BRACE_RENDERER = Singleton(syntax.END_BRACE)


class FilesConditionArg(FromArgumentElementsBase, ABC):
    @staticmethod
    def empty() -> 'FilesConditionArg':
        return FilesCondition(())

    @property
    def elements(self) -> List[WithToString]:
        raise ValueError('unsupported')


class FilesCondition(FilesConditionArg):
    def __init__(self, files: Sequence[FileCondition]):
        self.files = files

    @property
    def as_argument_elements(self) -> ArgumentElements:
        ret_val = ArgumentElements([syntax.BEGIN_BRACE])
        for fc in self.files:
            ret_val = ret_val.followed_by_lines(fc.as_argument_elements.all_lines)

        return ret_val.last_line_followed_by(ArgumentElements([syntax.END_BRACE]))


class SymbolReferenceNameSyntax(FilesConditionArg):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    @property
    def as_argument_elements(self) -> ArgumentElements:
        return ArgumentElements([self.symbol_name])


class SymbolReferenceReferenceSyntax(FilesConditionArg):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    @property
    def as_argument_elements(self) -> ArgumentElements:
        return ArgumentElements([symbol_reference_syntax_for_name(self.symbol_name)])


class Parentheses(FilesConditionArg):
    def __init__(self, files_condition: FilesConditionArg):
        self.files_condition = files_condition

    @property
    def as_argument_elements(self) -> ArgumentElements:
        return (
            ArgumentElements(['('])
                .append_to_first_and_following_lines(self.files_condition.as_argument_elements)
                .last_line_followed_by(ArgumentElements([')']))
        )


class InvalidSyntax(FilesConditionArg):
    @property
    def as_argument_elements(self) -> ArgumentElements:
        return ArgumentElements([syntax.END_BRACE])


class Missing(FilesConditionArg):
    @property
    def as_argument_elements(self) -> ArgumentElements:
        return ArgumentElements([])
