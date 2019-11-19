from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.logic.line_matcher import LineMatcherSdv
from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.string_matcher import StringMatcherSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv

T = TypeVar('T')


class LogicTypeSdvPseudoVisitor(Generic[T], ABC):
    def visit(self, value: LogicTypeSdv) -> T:
        """
        :return: Return value from _visit... method
        """
        if isinstance(value, FileMatcherSdv):
            return self.visit_file_matcher(value)
        if isinstance(value, FilesMatcherSdv):
            return self.visit_files_matcher(value)
        if isinstance(value, LineMatcherSdv):
            return self.visit_line_matcher(value)
        if isinstance(value, StringMatcherSdv):
            return self.visit_string_matcher(value)
        if isinstance(value, StringTransformerSdv):
            return self.visit_string_transformer(value)
        if isinstance(value, ProgramSdv):
            return self.visit_program(value)
        raise TypeError('Unknown {}: {}'.format(DataTypeSdv, str(value)))

    @abstractmethod
    def visit_file_matcher(self, value: FileMatcherSdv) -> T:
        pass

    @abstractmethod
    def visit_files_matcher(self, value: FilesMatcherSdv) -> T:
        pass

    @abstractmethod
    def visit_line_matcher(self, value: LineMatcherSdv) -> T:
        pass

    @abstractmethod
    def visit_string_matcher(self, value: StringMatcherSdv) -> T:
        pass

    @abstractmethod
    def visit_string_transformer(self, value: StringTransformerSdv) -> T:
        pass

    @abstractmethod
    def visit_program(self, value: ProgramSdv) -> T:
        pass
