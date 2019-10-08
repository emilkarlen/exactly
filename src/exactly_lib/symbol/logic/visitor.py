from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.symbol.data.data_value_resolver import DataValueResolver
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.logic.files_matcher import FilesMatcherResolver
from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.symbol.logic.logic_value_resolver import LogicValueResolver
from exactly_lib.symbol.logic.program.program_resolver import ProgramResolver
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver

T = TypeVar('T')


class LogicValueResolverPseudoVisitor(Generic[T], ABC):
    def visit(self, value: LogicValueResolver) -> T:
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, FileMatcherResolver):
            return self.visit_file_matcher(value)
        if isinstance(value, FilesMatcherResolver):
            return self.visit_files_matcher(value)
        if isinstance(value, LineMatcherResolver):
            return self.visit_line_matcher(value)
        if isinstance(value, StringMatcherResolver):
            return self.visit_string_matcher(value)
        if isinstance(value, StringTransformerResolver):
            return self.visit_string_transformer(value)
        if isinstance(value, ProgramResolver):
            return self.visit_program(value)
        raise TypeError('Unknown {}: {}'.format(DataValueResolver, str(value)))

    @abstractmethod
    def visit_file_matcher(self, value: FileMatcherResolver) -> T:
        pass

    @abstractmethod
    def visit_files_matcher(self, value: FilesMatcherResolver) -> T:
        pass

    @abstractmethod
    def visit_line_matcher(self, value: LineMatcherResolver) -> T:
        pass

    @abstractmethod
    def visit_string_matcher(self, value: StringMatcherResolver) -> T:
        pass

    @abstractmethod
    def visit_string_transformer(self, value: StringTransformerResolver) -> T:
        pass

    @abstractmethod
    def visit_program(self, value: ProgramResolver) -> T:
        pass
