from typing import Sequence

from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.program.command_resolver import CommandResolver
from exactly_lib.symbol.program.stdin_data_resolver import StdinDataResolver
from exactly_lib.symbol.resolver_with_validation import DirDepValueResolverWithValidation
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case import pre_or_post_validation
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.program.command_and_stdin_value import CommandAndStdinValue
from exactly_lib.util.symbol_table import SymbolTable


class CommandAndStdinResolver(DirDepValueResolverWithValidation[CommandAndStdinValue]):
    """
    A command together with stdin contents.

    NOTE: The stdin contents component is not impl yet - but is
    mentioned in the name of the class to make the future purpose clear.
    """

    def __init__(self,
                 command: CommandResolver,
                 stdin: StdinDataResolver):
        self._command = command
        self._stdin = stdin

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references([self._command,
                                                               self._stdin])

    @property
    def command_resolver(self) -> CommandResolver:
        return self._command

    @property
    def stdin(self) -> StdinDataResolver:
        return self._stdin

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return pre_or_post_validation.all_of(self.validators)

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return tuple(self._command.validators) + tuple(self._stdin.validators)

    def resolve(self, symbols: SymbolTable) -> CommandAndStdinValue:
        return CommandAndStdinValue(self._command.resolve_value(symbols),
                                    self._stdin.resolve_value(symbols))
