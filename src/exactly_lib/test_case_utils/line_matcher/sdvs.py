from typing import Sequence, Callable

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.line_matcher import LineMatcherSdv
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.line_matcher import line_matcher_ddvs as ddvs
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class LineMatcherSdvConstant(LineMatcherSdv):
    def __init__(self, value: LineMatcher):
        self._value = ddvs.LineMatcherValueFromPrimitiveDdv(value)

    def resolve(self, symbols: SymbolTable) -> LineMatcherDdv:
        return self._value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._value) + '\''


class LineMatcherSdvFromParts(LineMatcherSdv):
    def __init__(self,
                 references: Sequence[SymbolReference],
                 make_value: Callable[[SymbolTable], LineMatcherDdv]):
        self._make_value = make_value
        self._references = references

    def resolve(self, symbols: SymbolTable) -> LineMatcherDdv:
        return self._make_value(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self))


class LineMatcherReferenceSdv(LineMatcherSdv):
    """
    A :class:`LineMatcherResolver` that is a reference to a symbol
    """

    def __init__(self, name_of_referenced_sdv: str):
        self._name_of_referenced_sdv = name_of_referenced_sdv
        self._references = [SymbolReference(name_of_referenced_sdv,
                                            ValueTypeRestriction(ValueType.LINE_MATCHER))]

    def resolve(self, symbols: SymbolTable) -> LineMatcherDdv:
        sdv = lookups.lookup_line_matcher(symbols, self._name_of_referenced_sdv)
        return sdv.resolve(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self)) + '\'' + str(self._name_of_referenced_sdv) + '\''
