from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence, Callable

from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolDependentValue
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.impls.advs import ConstantAdv
from exactly_lib.type_system.logic.logic_base_class import LogicDdv, \
    ApplicationEnvironmentDependentValue
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable

PRIMITIVE = TypeVar('PRIMITIVE')


class Ddv(Generic[PRIMITIVE], LogicDdv[PRIMITIVE], ABC):
    @property
    def describer(self) -> DetailsRenderer:
        return details.empty()


class Sdv(Generic[PRIMITIVE], SymbolDependentValue, ABC):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> Ddv[PRIMITIVE]:
        pass


class ConstantDdv(Generic[PRIMITIVE], Ddv[PRIMITIVE]):
    def __init__(self, adv: ApplicationEnvironmentDependentValue[PRIMITIVE]):
        self._adv = adv

    def value_of_any_dependency(self, tcds: Tcds) -> ApplicationEnvironmentDependentValue[PRIMITIVE]:
        return self._adv


class ConstantSdv(Generic[PRIMITIVE], Sdv[PRIMITIVE]):
    def __init__(self, ddv: Ddv[PRIMITIVE]):
        self._ddv = ddv

    def resolve(self, symbols: SymbolTable) -> Ddv[PRIMITIVE]:
        return self._ddv


class SdvFromParts(Generic[PRIMITIVE], Sdv[PRIMITIVE]):
    def __init__(self,
                 make_ddv: Callable[[SymbolTable], Ddv[PRIMITIVE]],
                 symbol_references: Sequence[SymbolReference] = (),
                 ):
        self._make_ddv = make_ddv
        self._symbol_references = symbol_references

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._symbol_references

    def resolve(self, symbols: SymbolTable) -> Ddv[PRIMITIVE]:
        return self._make_ddv(symbols)


def sdv_of_constant_primitive(primitive: PRIMITIVE) -> Sdv[PRIMITIVE]:
    return ConstantSdv(
        ConstantDdv(
            ConstantAdv(primitive)
        )
    )
