from typing import Sequence

from exactly_lib.symbol import lookups
from exactly_lib.symbol.program.arguments_resolver import ArgumentsResolver
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.symbol.program.stdin_data_resolver import StdinDataResolver
from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.program.resolvers.accumulator import ProgramElementsAccumulator
from exactly_lib.type_system.logic.program.program_value import ProgramValue
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class ProgramResolverForSymbolReference(ProgramResolver):
    def __init__(self,
                 symbol_name: str,
                 accumulated_elements: ProgramElementsAccumulator):
        self._symbol_name = symbol_name
        self._accumulated_elements = accumulated_elements

        self._symbol_reference = SymbolReference(symbol_name,
                                                 ValueTypeRestriction(ValueType.PROGRAM))

    def new_accumulated(self,
                        additional_stdin: StdinDataResolver,
                        additional_arguments: ArgumentsResolver,
                        additional_transformations: Sequence[LinesTransformerResolver],
                        additional_validation: Sequence[PreOrPostSdsValidator],
                        ):
        return ProgramResolverForSymbolReference(
            self._symbol_name,
            self._accumulated_elements.new_accumulated(additional_stdin,
                                                       additional_arguments,
                                                       additional_transformations,
                                                       additional_validation))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return [self._symbol_reference] + list(self._accumulated_elements.references)

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._accumulated_elements.validator

    def resolve_value(self, symbols: SymbolTable) -> ProgramValue:
        program_of_symbol = lookups.lookup_program(symbols, self._symbol_name)
        acc = self._accumulated_elements
        accumulated_program = program_of_symbol.new_accumulated(acc.stdin,
                                                                acc.arguments,
                                                                acc.transformations,
                                                                acc.validators)
        program_value = accumulated_program.resolve(symbols)
        assert isinstance(program_value, ProgramValue)  # Type info for IDE
        return ProgramValue(program_value.command,
                            program_value.stdin,
                            program_value.transformation)
