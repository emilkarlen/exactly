from typing import Sequence

from exactly_lib.symbol.logic.program.arguments_sdv import ArgumentsSdv
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.program.stdin_data_sdv import StdinDataSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references
from exactly_lib.test_case_utils.program.sdvs import accumulator
from exactly_lib.test_case_utils.program.sdvs.accumulator import ProgramElementsSdvAccumulator
from exactly_lib.type_system.logic.program.program import ProgramDdv
from exactly_lib.util.symbol_table import SymbolTable


class ProgramSdvForCommand(ProgramSdv):
    def __init__(self,
                 command: CommandSdv,
                 accumulated_elements: ProgramElementsSdvAccumulator):
        self._command = command
        self._accumulated_elements = accumulated_elements

    def new_accumulated(self,
                        additional_stdin: StdinDataSdv,
                        additional_arguments: ArgumentsSdv,
                        additional_transformations: Sequence[StringTransformerSdv],
                        ) -> 'ProgramSdvForCommand':
        return ProgramSdvForCommand(
            self._command,
            self._accumulated_elements.new_accumulated(additional_stdin,
                                                       additional_arguments,
                                                       additional_transformations))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([self._command,
                                                               self._accumulated_elements])

    def resolve(self, symbols: SymbolTable) -> ProgramDdv:
        acc = self._accumulated_elements
        has_transformations = len(acc.transformations) > 0
        accumulated_command = self._command.new_with_additional_arguments(acc.arguments)
        return ProgramDdv(accumulated_command.resolve(symbols),
                          acc.resolve_stdin_data(symbols),
                          acc.resolve_transformations(symbols),
                          has_transformations)


def plain(command: CommandSdv) -> ProgramSdvForCommand:
    return ProgramSdvForCommand(command,
                                accumulator.empty())
