from typing import Generic, Sequence

from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.matcher.applier import MODEL
from exactly_lib.test_case_utils.matcher.element_getter import ElementGetter, ElementGetterValue, ElementGetterResolver
from exactly_lib.test_case_utils.matcher.matcher import T
from exactly_lib.util.symbol_table import SymbolTable


class ElementGetterValueConstant(Generic[MODEL, T], ElementGetterValue[MODEL, T]):
    def __init__(self, constant: ElementGetter[MODEL, T]):
        self._constant = constant

    def value_of_any_dependency(self, tcds: HomeAndSds) -> ElementGetter[MODEL, T]:
        return self._constant


class ElementGetterResolverConstant(Generic[MODEL, T], ElementGetterResolver[MODEL, T]):
    def __init__(self, constant: ElementGetterValue[MODEL, T]):
        self._constant = constant

    @property
    def references(self) -> Sequence[SymbolReference]:
        return ()

    def resolve(self, symbols: SymbolTable) -> ElementGetterValue[MODEL, T]:
        return self._constant
