from typing import Generic, Sequence, TypeVar, Optional

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.property_getter import PropertyGetter, PropertyGetterValue, \
    PropertyGetterSdv
from exactly_lib.test_case_utils.matcher.property_matcher import MODEL
from exactly_lib.util.symbol_table import SymbolTable

T = TypeVar('T')


class PropertyGetterValueConstant(Generic[MODEL, T], PropertyGetterValue[MODEL, T]):
    def __init__(self, constant: PropertyGetter[MODEL, T]):
        self._constant = constant

    @property
    def name(self) -> Optional[str]:
        return self._constant.name

    def value_of_any_dependency(self, tcds: Tcds) -> PropertyGetter[MODEL, T]:
        return self._constant


class PropertyGetterSdvConstant(Generic[MODEL, T], PropertyGetterSdv[MODEL, T]):
    def __init__(self, constant: PropertyGetterValue[MODEL, T]):
        self._constant = constant

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> PropertyGetterValue[MODEL, T]:
        return self._constant
