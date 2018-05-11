from typing import Sequence

from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.program.arguments_resolver import ArgumentsResolver
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.symbol.program.program_resolver import ProgramResolver
from exactly_lib.symbol.program.stdin_data_resolver import StdinDataResolver
from exactly_lib.symbol.resolver_structure import StringTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.program.resolvers import accumulator
from exactly_lib.test_case_utils.program.resolvers.accumulator import ProgramElementsAccumulator
from exactly_lib.type_system.logic.program.program_value import ProgramValue
from exactly_lib.util.symbol_table import SymbolTable


class ProgramResolverForCommand(ProgramResolver):
    def __init__(self,
                 command: CommandResolver,
                 accumulated_elements: ProgramElementsAccumulator):
        self._command = command
        self._accumulated_elements = accumulated_elements

    def new_accumulated(self,
                        additional_stdin: StdinDataResolver,
                        additional_arguments: ArgumentsResolver,
                        additional_transformations: Sequence[StringTransformerResolver],
                        additional_validation: Sequence[PreOrPostSdsValidator],
                        ):
        return ProgramResolverForCommand(
            self._command,
            self._accumulated_elements.new_accumulated(additional_stdin,
                                                       additional_arguments,
                                                       additional_transformations,
                                                       additional_validation))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([self._command,
                                                               self._accumulated_elements])

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.all_of(self._validators)

    def resolve(self, symbols: SymbolTable) -> ProgramValue:
        acc = self._accumulated_elements
        accumulated_command = self._command.new_with_additional_arguments(acc.arguments)
        return ProgramValue(accumulated_command.resolve(symbols),
                            acc.resolve_stdin_data(symbols),
                            acc.resolve_transformations(symbols))

    @property
    def _validators(self) -> Sequence[PreOrPostSdsValidator]:
        return tuple(self._command.validators) + tuple(self._accumulated_elements.validators)


def plain(command: CommandResolver) -> ProgramResolverForCommand:
    return ProgramResolverForCommand(command,
                                     accumulator.empty())
