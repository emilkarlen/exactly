from typing import Sequence, Callable, Generic

from exactly_lib.symbol.logic.matcher import MatcherSdv, MODEL
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTrace
from exactly_lib.util.symbol_table import SymbolTable
from . import ddv_components


class MatcherSdvFromParts(Generic[MODEL], MatcherSdv[MODEL]):
    def __init__(self,
                 references: Sequence[SymbolReference],
                 make_ddv: Callable[[SymbolTable], MatcherDdv[MODEL]]):
        self._make_ddv = make_ddv
        self._references = references

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        return self._make_ddv(symbols)

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def __str__(self):
        return str(type(self))


class MatcherSdvFromConstantDdv(Generic[MODEL], MatcherSdv[MODEL]):
    def __init__(self, ddv: MatcherDdv[MODEL]):
        self._ddv = ddv

    def resolve(self, symbols: SymbolTable) -> MatcherDdv[MODEL]:
        return self._ddv

    @property
    def references(self) -> Sequence[SymbolReference]:
        return []

    def __str__(self):
        return str(type(self)) + '\'' + str(self._ddv) + '\''


def matcher_sdv_from_constant_primitive(primitive: MatcherWTrace[MODEL]) -> MatcherSdv[MODEL]:
    return MatcherSdvFromConstantDdv(
        ddv_components.MatcherDdvFromConstantPrimitive(primitive)
    )
