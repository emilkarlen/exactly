from typing import Sequence, List

from exactly_lib.symbol.data import list_sdvs
from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolContainer
from exactly_lib.type_system.data.concrete_strings import string_ddv_of_single_string
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    is_any_data_type_reference_restrictions
from exactly_lib_test.symbol.data.test_resources.list_sdvs import ListSdvTestImplForConstantListDdv
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref, symbol_utils
from exactly_lib_test.symbol.test_resources.symbols_setup import DataTypeSymbolContext, \
    DataSymbolValueContext
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class ListSymbolValueContext(DataSymbolValueContext[ListSdv]):
    @staticmethod
    def of_sdv(sdv: ListSdv) -> 'ListSymbolValueContext':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return ListSymbolValueContext(sdv)

    @staticmethod
    def of_ddv(ddv: ListDdv) -> 'ListSymbolValueContext':
        return ListSymbolValueContext.of_sdv(ListSdvTestImplForConstantListDdv(ddv))

    @staticmethod
    def of_constants(elements: Sequence[str]) -> 'ListSymbolValueContext':
        return ListSymbolValueContext.of_sdv(list_sdvs.from_str_constants(elements))

    @staticmethod
    def of_empty() -> 'ListSymbolValueContext':
        return ListSymbolValueContext.of_constants(())

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return asrt_sym_ref.matches_reference_2(
            symbol_name,
            is_any_data_type_reference_restrictions())

    @property
    def container(self) -> SymbolContainer:
        return symbol_utils.container(self.sdtv)

    @property
    def container__of_builtin(self) -> SymbolContainer:
        return symbol_utils.container_of_builtin(self.sdtv)


class ListSymbolContext(DataTypeSymbolContext[ListSdv]):
    def __init__(self,
                 name: str,
                 value: ListSymbolValueContext,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdv(name: str, sdv: ListSdv) -> 'ListSymbolContext':
        return ListSymbolContext(
            name,
            ListSymbolValueContext.of_sdv(sdv)
        )

    @staticmethod
    def of_ddv(name: str, ddv: ListDdv) -> 'ListSymbolContext':
        return ListSymbolContext(name, ListSymbolValueContext.of_ddv(ddv))

    @staticmethod
    def of_constants(name: str, elements: Sequence[str]) -> 'ListSymbolContext':
        return ListSymbolContext(name, ListSymbolValueContext.of_constants(elements))

    @staticmethod
    def of_empty(name: str) -> 'ListSymbolContext':
        return ListSymbolContext(name, ListSymbolValueContext.of_empty())


class ListDdvSymbolContext(ListSymbolContext):
    def __init__(self,
                 name: str,
                 ddv: ListDdv,
                 ):
        super().__init__(name, ListSymbolValueContext.of_ddv(ddv))
        self._ddv = ddv

    @staticmethod
    def of_constants(name: str, elements: Sequence[str]) -> 'ListDdvSymbolContext':
        return ListDdvSymbolContext(name, _ddv_of_constant(elements))

    @property
    def ddv(self) -> ListDdv:
        return self._ddv


class ListConstantSymbolContext(ListDdvSymbolContext):
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


ARBITRARY_SYMBOL_VALUE_CONTEXT = ListSymbolValueContext.of_constants(['arbitrary', 'value'])
