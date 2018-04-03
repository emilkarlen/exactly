from typing import Sequence

from exactly_lib.symbol.data import list_resolvers
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.lines_transformer import LinesTransformerSequenceResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.program import component_resolvers
from exactly_lib.symbol.program.component_resolvers import StdinDataResolver
from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.symbol.resolver_with_validation import ObjectWithSymbolReferencesAndValidation
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.logic.lines_transformer import LinesTransformerValue
from exactly_lib.type_system.logic.program.stdin_data_values import StdinDataValue
from exactly_lib.util.symbol_table import SymbolTable


class ProgramElementsAccumulator(ObjectWithSymbolReferencesAndValidation):
    """
    Helper class for handling elements that can be accumulated by a ProgramResolver
    """

    def __init__(self,
                 stdin: StdinDataResolver,
                 arguments: ListResolver,
                 transformations: Sequence[LinesTransformerResolver],
                 validators: Sequence[PreOrPostSdsValidator]):
        self.stdin = stdin
        self.arguments = arguments
        self.transformations = transformations
        self.validators = validators

    def new_accumulated(self,
                        additional_arguments: ListResolver,
                        additional_transformations: Sequence[LinesTransformerResolver],
                        additional_validation: Sequence[PreOrPostSdsValidator],
                        ):
        """Creates a new accumulated instance."""
        return ProgramElementsAccumulator(self.stdin,
                                          list_resolvers.concat([self.arguments, additional_arguments]),
                                          tuple(self.transformations) + tuple(additional_transformations),
                                          tuple(self.validators) + tuple(additional_validation))

    @property
    def references(self) -> Sequence[SymbolReference]:
        objects_with_refs = [self.stdin, self.arguments] + list(self.transformations)
        return references_from_objects_with_symbol_references(objects_with_refs)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.all_of(self.validators)

    def resolve_stdin_data(self, symbols: SymbolTable) -> StdinDataValue:
        return self.stdin.resolve_value(symbols)

    def resolve_transformations(self, symbols: SymbolTable) -> LinesTransformerValue:
        return LinesTransformerSequenceResolver(self.transformations).resolve(symbols)


def empty() -> ProgramElementsAccumulator:
    return ProgramElementsAccumulator(component_resolvers.no_stdin(),
                                      list_resolvers.empty(),
                                      (),
                                      ())


def new_with_validators(validators: Sequence[PreOrPostSdsValidator]) -> ProgramElementsAccumulator:
    return ProgramElementsAccumulator(component_resolvers.no_stdin(),
                                      list_resolvers.empty(),
                                      (),
                                      validators)


def new_with_arguments_and_validators(arguments: ListResolver,
                                      validators: Sequence[PreOrPostSdsValidator]) -> ProgramElementsAccumulator:
    return ProgramElementsAccumulator(component_resolvers.no_stdin(),
                                      arguments,
                                      (),
                                      validators)
