from typing import Sequence

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.matcher import MatcherSdv, T
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class MatcherReferenceSdv(MatcherSdv[T]):
    """
    A :class:`MatcherSdv` that is a reference to a symbol
    """

    def __init__(self,
                 name_of_referenced_sdv: str,
                 reference_restriction: ValueType):
        self._name_of_referenced_sdv = name_of_referenced_sdv
        self._references = [SymbolReference(name_of_referenced_sdv,
                                            ValueTypeRestriction(reference_restriction))]

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[T]:
        sdv = lookups.lookup_line_matcher(symbols, self._name_of_referenced_sdv)
        return sdv.resolve(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_sdv) + '\''
