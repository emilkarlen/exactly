from typing import Sequence

from exactly_lib.symbol.logic.program import stdin_data_sdv
from exactly_lib.symbol.logic.program.arguments_sdv import ArgumentsSdv
from exactly_lib.symbol.logic.program.stdin_data_sdv import StdinDataSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references, \
    ObjectWithSymbolReferences
from exactly_lib.test_case_utils.program.command import arguments_sdvs
from exactly_lib.test_case_utils.string_transformer.impl.sequence import StringTransformerSequenceSdv
from exactly_lib.type_system.logic.program.stdin_data import StdinDataDdv
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv
from exactly_lib.util.symbol_table import SymbolTable


class ProgramElementsSdvAccumulator(ObjectWithSymbolReferences):
    """
    Helper class for handling elements that can be accumulated by a ProgramSdv
    """

    def __init__(self,
                 stdin: StdinDataSdv,
                 arguments: ArgumentsSdv,
                 transformations: Sequence[StringTransformerSdv],
                 ):
        self.stdin = stdin
        self.arguments = arguments
        self.transformations = transformations

    def new_accumulated(self,
                        additional_stdin: StdinDataSdv,
                        additional_arguments: ArgumentsSdv,
                        additional_transformations: Sequence[StringTransformerSdv],
                        ) -> 'ProgramElementsSdvAccumulator':
        """Creates a new accumulated instance."""
        return ProgramElementsSdvAccumulator(self.stdin.new_accumulated(additional_stdin),
                                             self.arguments.new_accumulated(additional_arguments),
                                             tuple(self.transformations) + tuple(additional_transformations))

    @property
    def references(self) -> Sequence[SymbolReference]:
        objects_with_refs = [self.stdin, self.arguments] + list(self.transformations)
        return references_from_objects_with_symbol_references(objects_with_refs)

    def resolve_stdin_data(self, symbols: SymbolTable) -> StdinDataDdv:
        return self.stdin.resolve_value(symbols)

    def resolve_transformations(self, symbols: SymbolTable) -> StringTransformerDdv:
        return StringTransformerSequenceSdv(self.transformations).resolve(symbols)


def empty() -> ProgramElementsSdvAccumulator:
    return ProgramElementsSdvAccumulator(stdin_data_sdv.no_stdin(), arguments_sdvs.empty(), ())


def new_with_arguments(arguments: ArgumentsSdv) -> ProgramElementsSdvAccumulator:
    return ProgramElementsSdvAccumulator(stdin_data_sdv.no_stdin(), arguments, ())
