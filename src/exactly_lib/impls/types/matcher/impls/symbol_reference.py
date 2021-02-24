from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.dep_variants.ddv.matcher import MatcherDdv
from exactly_lib.type_val_deps.sym_ref import symbol_lookup
from exactly_lib.type_val_deps.sym_ref.restrictions import ValueTypeRestriction
from exactly_lib.type_val_deps.types.matcher import MatcherSdv, MODEL
from exactly_lib.util.symbol_table import SymbolTable


class MatcherReferenceSdv(MatcherSdv[MODEL]):
    """
    A :class:`MatcherSdv` that is a reference to a symbol
    """
    _TYPE_LOOKUP = {
        ValueType.INTEGER_MATCHER: symbol_lookup.lookup_integer_matcher,
        ValueType.LINE_MATCHER: symbol_lookup.lookup_line_matcher,
        ValueType.FILE_MATCHER: symbol_lookup.lookup_file_matcher,
        ValueType.FILES_MATCHER: symbol_lookup.lookup_files_matcher,
        ValueType.STRING_MATCHER: symbol_lookup.lookup_string_matcher,
    }

    def __init__(self,
                 name_of_referenced_sdv: str,
                 value_type: ValueType):
        self._name_of_referenced_sdv = name_of_referenced_sdv
        self._value_type = value_type
        self._references = [SymbolReference(name_of_referenced_sdv,
                                            ValueTypeRestriction.of_single(value_type))]

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        lookup_fun = self._TYPE_LOOKUP[self._value_type]
        sdv = lookup_fun(symbols, self._name_of_referenced_sdv)
        return sdv.resolve(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_sdv) + '\''
