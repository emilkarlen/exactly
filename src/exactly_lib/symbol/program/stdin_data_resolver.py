from typing import Sequence

from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.program.string_or_file import StringOrFileRefResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.logic.program.stdin_data_values import StdinDataValue
from exactly_lib.util.symbol_table import SymbolTable


class StdinDataResolver(ObjectWithTypedSymbolReferences):
    def __init__(self,
                 fragments: Sequence[StringOrFileRefResolver],
                 validators: Sequence[PreOrPostSdsValidator] = ()):
        self._validators = validators
        self._fragments = fragments

    def new_accumulated(self, stdin_data_resolver):
        assert isinstance(stdin_data_resolver, StdinDataResolver)

        fragments = tuple(self._fragments) + tuple(stdin_data_resolver._fragments)
        validators = tuple(self._validators) + tuple(stdin_data_resolver.validators)

        return StdinDataResolver(fragments, validators)

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return self._validators

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references(self._fragments)

    def resolve_value(self, symbols: SymbolTable) -> StdinDataValue:
        return StdinDataValue([f.resolve_value(symbols) for f in self._fragments])


def no_stdin() -> StdinDataResolver:
    return StdinDataResolver((), ())
