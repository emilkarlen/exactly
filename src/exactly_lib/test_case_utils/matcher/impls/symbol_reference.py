from typing import Sequence

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.matcher import MatcherSdv, MODEL
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class MatcherReferenceSdv(MatcherSdv[MODEL]):
    """
    A :class:`MatcherSdv` that is a reference to a symbol
    """
    _TYPE_LOOKUP = {
        ValueType.LINE_MATCHER: lookups.lookup_line_matcher,
        ValueType.FILE_MATCHER: lookups.lookup_file_matcher,
        ValueType.FILES_MATCHER: lookups.lookup_files_matcher,
        ValueType.STRING_MATCHER: lookups.lookup_string_matcher,
    }

    def __init__(self,
                 name_of_referenced_sdv: str,
                 value_type: ValueType):
        self._name_of_referenced_sdv = name_of_referenced_sdv
        self._value_type = value_type
        self._references = [SymbolReference(name_of_referenced_sdv,
                                            ValueTypeRestriction(value_type))]

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        lookup_fun = self._TYPE_LOOKUP[self._value_type]
        sdv = lookup_fun(symbols, self._name_of_referenced_sdv)
        return sdv.resolve(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_sdv) + '\''
