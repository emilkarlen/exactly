from typing import Sequence

from exactly_lib.symbol.data import list_resolvers
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.object_with_symbol_references import references_from_objects_with_symbol_references
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.string_or_file import StringOrFileRefResolver
from exactly_lib.test_case_utils.util_values import StringOrFileRefValue
from exactly_lib.util.symbol_table import SymbolTable


class StdinResolver(ObjectWithTypedSymbolReferences):
    def __init__(self,
                 fragments: Sequence[StringOrFileRefResolver],
                 validators: Sequence[PreOrPostSdsValidator] = ()):
        self._validators = validators
        self._fragments = fragments

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return self._validators

    @property
    def references(self) -> Sequence[SymbolReference]:
        return references_from_objects_with_symbol_references(self._fragments)

    def resolve_value(self, symbols: SymbolTable) -> Sequence[StringOrFileRefValue]:
        return [f.resolve_value(symbols) for f in self._fragments]



def no_stdin() -> StdinResolver:
    return StdinResolver((), ())


class ArgumentsResolver(ObjectWithTypedSymbolReferences):
    def __init__(self,
                 arguments: ListResolver,
                 validators: Sequence[PreOrPostSdsValidator] = ()):
        self._arguments = arguments
        self._validators = validators

    @property
    def arguments_list(self) -> ListResolver:
        return self._arguments

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return self._validators

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._arguments.references

    def new_with_appended(self,
                          arguments: ListResolver,
                          validators: Sequence[PreOrPostSdsValidator] = ()):
        args = list_resolvers.concat([self.arguments_list, arguments])
        validators = tuple(self._validators) + tuple(validators)

        return ArgumentsResolver(args, validators)


def no_arguments() -> ArgumentsResolver:
    return ArgumentsResolver(list_resolvers.empty(), ())
