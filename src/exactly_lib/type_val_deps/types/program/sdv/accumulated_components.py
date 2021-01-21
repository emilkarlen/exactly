from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference, references_from_objects_with_symbol_references, \
    ObjectWithSymbolReferences
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.string_source.ddv import StringSourceDdv
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.type_val_deps.types.string_transformer.ddv import StringTransformerDdv
from exactly_lib.type_val_deps.types.string_transformer.sdv import StringTransformerSdv
from exactly_lib.util.symbol_table import SymbolTable


class AccumulatedComponents(ObjectWithSymbolReferences):
    """Components of a :class:ProgramSdv that can be accumulated."""

    def __init__(self,
                 stdin: Sequence[StringSourceSdv],
                 arguments: ArgumentsSdv,
                 transformations: Sequence[StringTransformerSdv],
                 ):
        self.stdin = stdin
        self.arguments = arguments
        self.transformations = transformations

    @staticmethod
    def empty() -> 'AccumulatedComponents':
        return AccumulatedComponents((), ArgumentsSdv.empty(), ())

    @staticmethod
    def of_arguments(arguments: ArgumentsSdv) -> 'AccumulatedComponents':
        return AccumulatedComponents((), arguments, ())

    @staticmethod
    def of_stdin(stdin: Sequence[StringSourceSdv]) -> 'AccumulatedComponents':
        return AccumulatedComponents(stdin, ArgumentsSdv.empty(), ())

    @staticmethod
    def of_transformations(transformations: Sequence[StringTransformerSdv]) -> 'AccumulatedComponents':
        return AccumulatedComponents((), ArgumentsSdv.empty(), transformations)

    @staticmethod
    def of_transformation(transformation: StringTransformerSdv) -> 'AccumulatedComponents':
        return AccumulatedComponents.of_transformations((transformation,))

    def new_accumulated(self, additional: 'AccumulatedComponents') -> 'AccumulatedComponents':
        """Creates a new accumulated instance."""
        return AccumulatedComponents(tuple(self.stdin) + tuple(additional.stdin),
                                     self.arguments.new_accumulated(additional.arguments),
                                     tuple(self.transformations) + tuple(additional.transformations))

    @property
    def references(self) -> Sequence[SymbolReference]:
        objects_with_refs = list(self.stdin) + [self.arguments] + list(self.transformations)
        return references_from_objects_with_symbol_references(objects_with_refs)

    def resolve_stdin(self, symbols: SymbolTable) -> Sequence[StringSourceDdv]:
        return [ss.resolve(symbols) for ss in self.stdin]

    def resolve_transformations(self, symbols: SymbolTable) -> Sequence[StringTransformerDdv]:
        return [st.resolve(symbols) for st in self.transformations]
