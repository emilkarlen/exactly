from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references
from exactly_lib.type_val_deps.types.program.ddv.program import ProgramDdv
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.util.symbol_table import SymbolTable


class ProgramSdvForCommand(ProgramSdv):
    def __init__(self,
                 command: CommandSdv,
                 accumulated_elements: AccumulatedComponents,
                 ):
        self._command = command
        self._accumulated_components = accumulated_elements

    def new_accumulated(self, additional: AccumulatedComponents) -> 'ProgramSdvForCommand':
        return ProgramSdvForCommand(self._command,
                                    self._accumulated_components.new_accumulated(additional))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([self._command,
                                                               self._accumulated_components])

    def resolve(self, symbols: SymbolTable) -> ProgramDdv:
        acc = self._accumulated_components
        accumulated_command = self._command.new_with_additional_arguments(acc.arguments)
        return ProgramDdv(accumulated_command.resolve(symbols),
                          acc.resolve_stdin(symbols),
                          acc.resolve_transformations(symbols))


def plain(command: CommandSdv) -> ProgramSdvForCommand:
    return ProgramSdvForCommand(command,
                                AccumulatedComponents.empty())
