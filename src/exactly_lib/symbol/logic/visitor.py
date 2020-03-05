from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.logic.file_matcher import FileMatcherStv
from exactly_lib.symbol.logic.files_matcher import FilesMatcherStv
from exactly_lib.symbol.logic.line_matcher import LineMatcherStv
from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeStv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.string_matcher import StringMatcherStv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv

T = TypeVar('T')


class LogicTypeStvPseudoVisitor(Generic[T], ABC):
    def visit(self, value: LogicTypeStv) -> T:
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, FileMatcherStv):
            return self.visit_file_matcher(value)
        if isinstance(value, FilesMatcherStv):
            return self.visit_files_matcher(value)
        if isinstance(value, LineMatcherStv):
            return self.visit_line_matcher(value)
        if isinstance(value, StringMatcherStv):
            return self.visit_string_matcher(value)
        if isinstance(value, StringTransformerSdv):
            return self.visit_string_transformer(value)
        if isinstance(value, ProgramSdv):
            return self.visit_program(value)
        raise TypeError('Unknown {}: {}'.format(DataTypeSdv, str(value)))

    @abstractmethod
    def visit_file_matcher(self, value: FileMatcherStv) -> T:
        pass

    @abstractmethod
    def visit_files_matcher(self, value: FilesMatcherStv) -> T:
        pass

    @abstractmethod
    def visit_line_matcher(self, value: LineMatcherStv) -> T:
        pass

    @abstractmethod
    def visit_string_matcher(self, value: StringMatcherStv) -> T:
        pass

    @abstractmethod
    def visit_string_transformer(self, value: StringTransformerSdv) -> T:
        pass

    @abstractmethod
    def visit_program(self, value: ProgramSdv) -> T:
        pass
