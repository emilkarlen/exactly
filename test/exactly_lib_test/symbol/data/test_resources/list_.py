from typing import Sequence, List

from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.data.concrete_strings import string_ddv_of_single_string
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    is_any_data_type_reference_restrictions
from exactly_lib_test.symbol.data.test_resources.list_sdvs import ListSdvTestImplForConstantListDdv
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolTableValue, SdvSymbolContext
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class ListSymbolTableValue(SymbolTableValue[ListSdv]):
    @staticmethod
    def of_sdv(sdv: ListSdv) -> 'ListSymbolTableValue':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return ListSymbolTableValue(sdv)

    @staticmethod
    def of_ddv(ddv: ListDdv) -> 'ListSymbolTableValue':
        return ListSymbolTableValue.of_sdv(ListSdvTestImplForConstantListDdv(ddv))

    @staticmethod
    def of_constant(elements: Sequence[str]) -> 'ListSymbolTableValue':
        return ListSymbolTableValue.of_ddv(_ddv_of_constant(elements))

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return asrt_sym_ref.matches_reference_2(
            symbol_name,
            is_any_data_type_reference_restrictions())


class ListSymbolContext(SdvSymbolContext[ListSdv]):
    def __init__(self,
                 name: str,
                 value: ListSymbolTableValue,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdv(name: str, sdv: ListSdv) -> 'ListSymbolContext':
        return ListSymbolContext(
            name,
            ListSymbolTableValue.of_sdv(sdv)
        )

    @staticmethod
    def of_ddv(name: str, ddv: ListDdv) -> 'ListSymbolContext':
        return ListSymbolContext(name, ListSymbolTableValue.of_ddv(ddv))

    @staticmethod
    def of_constant(name: str, elements: Sequence[str]) -> 'ListSymbolContext':
        return ListSymbolContext(name, ListSymbolTableValue.of_constant(elements))


class DdvListSymbolContext(ListSymbolContext):
    def __init__(self,
                 name: str,
                 ddv: ListDdv,
                 ):
        super().__init__(name, ListSymbolTableValue.of_ddv(ddv))
        self._ddv = ddv

    @staticmethod
    def of_constant(name: str, elements: Sequence[str]) -> 'DdvListSymbolContext':
        return DdvListSymbolContext(name, _ddv_of_constant(elements))

    @property
    def ddv(self) -> ListDdv:
        return self._ddv


class ConstantListSymbolContext(DdvListSymbolContext):
    def __init__(self,
                 name: str,
                 constant: Sequence[str],
                 ):
        super().__init__(name, _ddv_of_constant(constant))
        self._constant = constant

    @property
    def constant(self) -> Sequence[str]:
        return self._constant

    @property
    def constant_list(self) -> List[str]:
        return list(self._constant)


def _ddv_of_constant(elements: Sequence[str]) -> ListDdv:
    return ListDdv([
        string_ddv_of_single_string(element)
        for element in elements
    ])
