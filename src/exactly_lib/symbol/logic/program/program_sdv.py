from abc import ABC, abstractmethod
from typing import Sequence

from exactly_lib.symbol.logic.logic_type_sdv import LogicSdv
from exactly_lib.symbol.logic.program import stdin_data_sdv
from exactly_lib.symbol.logic.program.arguments_sdv import ArgumentsSdv
from exactly_lib.symbol.logic.program.stdin_data_sdv import StdinDataSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_utils.program.command import arguments_sdvs
from exactly_lib.type_system.logic.program.program import Program, ProgramDdv
from exactly_lib.util.symbol_table import SymbolTable


class ProgramSdv(LogicSdv[Program], ABC):
    def new_accumulated(self,
                        additional_stdin: StdinDataSdv,
                        additional_arguments: ArgumentsSdv,
                        additional_transformations: Sequence[StringTransformerSdv],
                        ) -> 'ProgramSdv':
        raise NotImplementedError('abstract method')

    def new_with_additional_arguments(self, additional_arguments: ArgumentsSdv) -> 'ProgramSdv':
        """
        Creates a new SDV with additional arguments appended at the end of
        current argument list.
        """
        return self.new_accumulated(stdin_data_sdv.no_stdin(), additional_arguments, ())

    def new_with_appended_transformations(self, transformations: Sequence[StringTransformerSdv]) -> 'ProgramSdv':
        """
        Creates a new SDV with additional transformation appended at the end of
        current transformations.
        """
        return self.new_accumulated(stdin_data_sdv.no_stdin(), arguments_sdvs.empty(), transformations)

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> ProgramDdv:
        pass
