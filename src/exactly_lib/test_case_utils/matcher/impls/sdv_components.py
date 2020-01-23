from typing import Sequence, Callable, Generic

from exactly_lib.symbol.logic.matcher import MatcherSdv, MODEL
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.impls.advs import ConstantMatcherAdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, MatcherWTraceAndNegation, MatcherAdv
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


class MatcherDdvFromPartsWConstantAdv(Generic[MODEL], MatcherDdv[MODEL]):
    def __init__(self,
                 make_matcher: Callable[[Tcds], MatcherWTraceAndNegation[MODEL]],
                 structure: StructureRenderer,
                 ):
        self._make_matcher = make_matcher
        self._structure = structure

    def structure(self) -> StructureRenderer:
        return self._structure

    def value_of_any_dependency(self, tcds: Tcds) -> MatcherAdv[MODEL]:
        return ConstantMatcherAdv(self._make_matcher(tcds))


def matcher_sdv_from_constant_primitive(primitive: MatcherWTraceAndNegation[MODEL]) -> MatcherSdv[MODEL]:
    return MatcherSdvFromConstantDdv(
        ddv_components.MatcherDdvFromConstantPrimitive(primitive)
    )
