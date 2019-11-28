from typing import Generic, Sequence, TypeVar, Optional

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter, PropertyGetterValue, \
    PropertyGetterSdv
from exactly_lib.test_case_utils.matcher.property_matcher import PROP_TYPE
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class PropertyGetterValueConstant(Generic[PROP_TYPE, T], PropertyGetterValue[PROP_TYPE, T]):
    def __init__(self, constant: PropertyGetter[PROP_TYPE, T]):
        self._constant = constant

    @property
    def name(self) -> Optional[str]:
        return self._constant.name

    def value_of_any_dependency(self, tcds: Tcds) -> PropertyGetter[PROP_TYPE, T]:
        return self._constant


class PropertyGetterSdvConstant(Generic[PROP_TYPE, T], PropertyGetterSdv[PROP_TYPE, T]):
    def __init__(self, constant: PropertyGetterValue[PROP_TYPE, T]):
        self._constant = constant

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> PropertyGetterValue[PROP_TYPE, T]:
        return self._constant
