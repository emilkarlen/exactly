from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Sequence, Callable

from exactly_lib.symbol.object_with_typed_symbol_references import ObjectWithTypedSymbolReferences
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import ddv_validation
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment
from exactly_lib.util.description_tree import details
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.symbol_table import SymbolTable

PRIMITIVE = TypeVar('PRIMITIVE')


class Adv(Generic[PRIMITIVE], ABC):
    @abstractmethod
    def primitive(self, environment: ApplicationEnvironment) -> PRIMITIVE:
        pass


class Ddv(Generic[PRIMITIVE], ABC):
    @property
    def describer(self) -> DetailsRenderer:
        return details.empty()

    @property
    def validator(self) -> DdvValidator:
        return ddv_validation.constant_success_validator()

    @abstractmethod
    def value_of_any_dependency(self, tcds: Tcds) -> Adv[PRIMITIVE]:
        pass


class Sdv(Generic[PRIMITIVE], ObjectWithTypedSymbolReferences, ABC):
    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    @abstractmethod
    def resolve(self, symbols: SymbolTable) -> Ddv[PRIMITIVE]:
        pass


class ConstantAdv(Generic[PRIMITIVE], Adv[PRIMITIVE]):
    def __init__(self, primitive: PRIMITIVE):
        self._primitive = primitive

    def primitive(self, environment: ApplicationEnvironment) -> PRIMITIVE:
        return self._primitive


class ConstantDdv(Generic[PRIMITIVE], Ddv[PRIMITIVE]):
    def __init__(self, adv: Adv[PRIMITIVE]):
        self._adv = adv

    def value_of_any_dependency(self, tcds: Tcds) -> Adv[PRIMITIVE]:
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
