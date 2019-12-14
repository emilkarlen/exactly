from typing import Sequence

from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv
from exactly_lib.symbol.logic.program import stdin_data_sdv
from exactly_lib.symbol.logic.program.arguments_sdv import ArgumentsSdv
from exactly_lib.symbol.logic.program.stdin_data_sdv import StdinDataSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.symbol.utils import DirDepValueResolver
from exactly_lib.test_case_utils.program.command import arguments_sdvs
from exactly_lib.type_system.logic.program.program import ProgramDdv
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util.symbol_table import SymbolTable


class ProgramSdv(LogicTypeSdv, DirDepValueResolver[ProgramDdv]):
    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.PROGRAM

    @property
    def value_type(self) -> ValueType:
        return ValueType.PROGRAM

    @property
    def references(self) -> Sequence[SymbolReference]:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> ProgramDdv:
        raise NotImplementedError('abstract method')

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
