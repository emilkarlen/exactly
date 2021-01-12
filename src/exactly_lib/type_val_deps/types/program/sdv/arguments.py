from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference, ObjectWithSymbolReferences
from exactly_lib.type_val_deps.dep_variants.sdv.sdv_validation import DdvValidatorResolver
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv
from exactly_lib.type_val_deps.types.program.ddv.argument import ArgumentsDdv
from exactly_lib.util.symbol_table import SymbolTable


class ArgumentsSdv(ObjectWithSymbolReferences):
    def __init__(self,
                 arguments: ListSdv,
                 validators: Sequence[DdvValidatorResolver] = ()):
        self._arguments = arguments
        self._validators = validators

    @staticmethod
    def empty() -> 'ArgumentsSdv':
        return ArgumentsSdv(list_sdvs.empty(), ())

    @staticmethod
    def new_without_validation(arguments: ListSdv) -> 'ArgumentsSdv':
        return ArgumentsSdv(arguments, ())

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
