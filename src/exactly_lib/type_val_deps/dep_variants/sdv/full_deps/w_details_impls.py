from typing import TypeVar, Generic, Sequence, Callable

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.dep_variants.adv import advs
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps import w_details_impls as ddv_w_details_impls
from exactly_lib.type_val_deps.dep_variants.ddv.full_deps.ddv import FullDepsWithDetailsDescriptionDdv
from exactly_lib.type_val_deps.dep_variants.sdv.full_deps.sdv import FullDepsWithDetailsDescriptionSdv
from exactly_lib.util.symbol_table import SymbolTable

PRIMITIVE = TypeVar('PRIMITIVE')


class ConstantSdv(Generic[PRIMITIVE], FullDepsWithDetailsDescriptionSdv[PRIMITIVE]):
    def __init__(self, ddv: FullDepsWithDetailsDescriptionDdv[PRIMITIVE]):
        self._ddv = ddv

    def resolve(self, symbols: SymbolTable) -> FullDepsWithDetailsDescriptionDdv[PRIMITIVE]:
        return self._ddv


class SdvFromParts(Generic[PRIMITIVE], FullDepsWithDetailsDescriptionSdv[PRIMITIVE]):
    def __init__(self,
                 make_ddv: Callable[[SymbolTable], FullDepsWithDetailsDescriptionDdv[PRIMITIVE]],
                 symbol_references: Sequence[SymbolReference] = (),
                 ):
        self._make_ddv = make_ddv
        self._symbol_references = symbol_references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._symbol_references

    def resolve(self, symbols: SymbolTable) -> FullDepsWithDetailsDescriptionDdv[PRIMITIVE]:
        return self._make_ddv(symbols)


def sdv_of_constant_primitive(primitive: PRIMITIVE) -> FullDepsWithDetailsDescriptionSdv[PRIMITIVE]:
    return ConstantSdv(
        ddv_w_details_impls.ConstantDdv(advs.ConstantAdv(primitive))
    )
