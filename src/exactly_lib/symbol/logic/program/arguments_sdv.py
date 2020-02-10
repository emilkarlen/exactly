from typing import Sequence

from exactly_lib.symbol.data import list_sdvs
from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, ObjectWithSymbolReferences
from exactly_lib.symbol.sdv_validation import DdvValidatorResolver
from exactly_lib.type_system.logic.program.argument import ArgumentsDdv
from exactly_lib.util.symbol_table import SymbolTable


class ArgumentsSdv(ObjectWithSymbolReferences):
    def __init__(self,
                 arguments: ListSdv,
                 validators: Sequence[DdvValidatorResolver] = ()):
        self._arguments = arguments
        self._validators = validators

    def new_accumulated(self, arguments_sdv: 'ArgumentsSdv') -> 'ArgumentsSdv':
        args = list_sdvs.concat([self._arguments, arguments_sdv.arguments_list])
        validators = tuple(self._validators) + tuple(arguments_sdv._validators)

        return ArgumentsSdv(args, validators)

    @property
    def arguments_list(self) -> ListSdv:
        return self._arguments

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._arguments.references

    def resolve(self, symbols: SymbolTable) -> ArgumentsDdv:
        return ArgumentsDdv(
            self._arguments.resolve(symbols),
            [vr(symbols)
             for vr in self._validators]
        )


def new_without_validation(arguments: ListSdv) -> ArgumentsSdv:
    return ArgumentsSdv(arguments, ())
