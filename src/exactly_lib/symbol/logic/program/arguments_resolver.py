from typing import Sequence

from exactly_lib.symbol.data import list_resolvers
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator


class ArgumentsResolver(ObjectWithTypedSymbolReferences):
    def __init__(self,
                 arguments: ListResolver,
                 validators: Sequence[PreOrPostSdsValidator] = ()):
        self._arguments = arguments
        self._validators = validators

    def new_accumulated(self, arguments_resolver):
        args = list_resolvers.concat([self._arguments, arguments_resolver.arguments_list])
        validators = tuple(self._validators) + tuple(arguments_resolver.validators)

        return ArgumentsResolver(args, validators)

    @property
    def arguments_list(self) -> ListResolver:
        return self._arguments

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return self._validators

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._arguments.references


def new_without_validation(arguments: ListResolver) -> ArgumentsResolver:
    return ArgumentsResolver(arguments, ())
