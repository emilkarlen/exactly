from typing import Sequence

from exactly_lib.symbol.data import list_sdvs
from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator


class ArgumentsSdv(ObjectWithTypedSymbolReferences):
    def __init__(self,
                 arguments: ListSdv,
                 validators: Sequence[PreOrPostSdsValidator] = ()):
        self._arguments = arguments
        self._validators = validators

    def new_accumulated(self, arguments_sdv: 'ArgumentsSdv') -> 'ArgumentsSdv':
        args = list_sdvs.concat([self._arguments, arguments_sdv.arguments_list])
        validators = tuple(self._validators) + tuple(arguments_sdv.validators)

        return ArgumentsSdv(args, validators)

    @property
    def arguments_list(self) -> ListSdv:
        return self._arguments

    @property
    def validators(self) -> Sequence[PreOrPostSdsValidator]:
        return self._validators

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._arguments.references


def new_without_validation(arguments: ListSdv) -> ArgumentsSdv:
    return ArgumentsSdv(arguments, ())
