from typing import Generic, Sequence, TypeVar

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter, PropertyGetterDdv, \
    PropertyGetterSdv
from exactly_lib.test_case_utils.matcher.property_matcher import PROP_TYPE
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class PropertyGetterDdvConstant(Generic[PROP_TYPE, T], PropertyGetterDdv[PROP_TYPE, T]):
    def __init__(self, constant: PropertyGetter[PROP_TYPE, T]):
        self._constant = constant

    def value_of_any_dependency(self, tcds: Tcds) -> PropertyGetter[PROP_TYPE, T]:
        return self._constant


class PropertyGetterSdvConstant(Generic[PROP_TYPE, T], PropertyGetterSdv[PROP_TYPE, T]):
    def __init__(self, constant: PropertyGetterDdv[PROP_TYPE, T]):
        self._constant = constant

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> PropertyGetterDdv[PROP_TYPE, T]:
        return self._constant


def sdv_of_constant_primitive(constant: PropertyGetter[PROP_TYPE, T]) -> PropertyGetterSdv[PROP_TYPE, T]:
    return PropertyGetterSdvConstant(
        PropertyGetterDdvConstant(constant)
    )
