from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.sym_ref import symbol_lookup
from exactly_lib.type_val_deps.sym_ref.restrictions import ValueTypeRestriction
from exactly_lib.type_val_deps.types.program.ddv.program import ProgramDdv
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.util.symbol_table import SymbolTable


class ProgramSdvForSymbolReference(ProgramSdv):
    def __init__(self,
                 symbol_name: str,
                 accumulated_elements: AccumulatedComponents):
        self._symbol_name = symbol_name
        self._accumulated_components = accumulated_elements

        self._symbol_reference = SymbolReference(symbol_name,
                                                 ValueTypeRestriction.of_single(ValueType.PROGRAM))

    def new_accumulated(self, additional: AccumulatedComponents) -> 'ProgramSdvForSymbolReference':
        return ProgramSdvForSymbolReference(self._symbol_name,
                                            self._accumulated_components.new_accumulated(additional))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return [self._symbol_reference] + list(self._accumulated_components.references)

    def resolve(self, symbols: SymbolTable) -> ProgramDdv:
        program_of_symbol = symbol_lookup.lookup_program(symbols, self._symbol_name)
        accumulated_program = program_of_symbol.new_accumulated(self._accumulated_components)

        return accumulated_program.resolve(symbols)


def plain(symbol_name: str,
          arguments: ArgumentsSdv = ArgumentsSdv.empty()) -> ProgramSdvForSymbolReference:
    return ProgramSdvForSymbolReference(symbol_name,
                                        AccumulatedComponents.of_arguments(arguments))
