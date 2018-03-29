from typing import Sequence

from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.external_program.command.command_resolver import CommandResolver
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator


class CommandAndStdinResolver(ObjectWithTypedSymbolReferences):
    """
    A command together with stdin contents.

    NOTE: The stdin contents component is not impl yet - but is
    mentioned in the name of the class to make the future purpose clear.
    """

    def __init__(self, command_resolver: CommandResolver):
        self._command_resolver = command_resolver

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._command_resolver.references

    @property
    def command_resolver(self) -> CommandResolver:
        return self._command_resolver

    @property
    def validator(self) -> PreOrPostSdsValidator:
        return self._command_resolver.validator
