from typing import Sequence

from exactly_lib.impls.types.program.command import arguments_sdvs
from exactly_lib.impls.types.program.sdvs import accumulator
from exactly_lib.impls.types.program.sdvs.accumulator import ProgramElementsSdvAccumulator
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.sym_ref import symbol_lookup
from exactly_lib.type_val_deps.sym_ref.restrictions import ValueTypeRestriction
from exactly_lib.type_val_deps.types.program.ddv.program import ProgramDdv
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib.type_val_deps.types.program.sdv.stdin import StdinDataSdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.util.symbol_table import SymbolTable


class ProgramSdvForSymbolReference(ProgramSdv):
    def __init__(self,
                 symbol_name: str,
                 accumulated_elements: ProgramElementsSdvAccumulator):
        self._symbol_name = symbol_name
        self._accumulated_elements = accumulated_elements

        self._symbol_reference = SymbolReference(symbol_name,
                                                 ValueTypeRestriction(ValueType.PROGRAM))

    def new_accumulated(self,
                        additional_stdin: StdinDataSdv,
                        additional_arguments: ArgumentsSdv,
                        additional_transformations: Sequence[StringTransformerSdv],
                        ) -> ProgramSdv:
        return ProgramSdvForSymbolReference(
            self._symbol_name,
            self._accumulated_elements.new_accumulated(additional_stdin,
                                                       additional_arguments,
                                                       additional_transformations))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return [self._symbol_reference] + list(self._accumulated_elements.references)

    def resolve(self, symbols: SymbolTable) -> ProgramDdv:
        program_of_symbol = symbol_lookup.lookup_program(symbols, self._symbol_name)
        acc = self._accumulated_elements
        accumulated_program = program_of_symbol.new_accumulated(acc.stdin, acc.arguments, acc.transformations)

        return accumulated_program.resolve(symbols)


def plain(symbol_name: str,
          arguments: ArgumentsSdv = arguments_sdvs.empty()) -> ProgramSdvForSymbolReference:
    return ProgramSdvForSymbolReference(symbol_name,
                                        accumulator.new_with_arguments(arguments))
