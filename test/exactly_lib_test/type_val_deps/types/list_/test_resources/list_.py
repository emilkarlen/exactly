from typing import Sequence, List, Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolDependentValue
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.list_.list_ddv import ListDdv
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv
from exactly_lib.type_val_deps.types.string_.strings_ddvs import string_ddv_of_single_string
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.data_restrictions_assertions import \
    is_reference_restrictions__w_str_rendering
from exactly_lib_test.type_val_deps.test_resources.w_str_rend.symbol_context import DataSymbolValueContext, \
    DataTypeSymbolContext
from exactly_lib_test.type_val_deps.types.list_.test_resources import list_assertions as asrt_list
from exactly_lib_test.type_val_deps.types.list_.test_resources.list_sdvs import ListSdvTestImplForConstantListDdv


class ListSymbolValueContext(DataSymbolValueContext[ListSdv]):
    def __init__(self,
                 sdv: ListSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_sdv(sdv: ListSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'ListSymbolValueContext':
        """
        Use this to create from an SDV, since constructor will
        may be changed to take other type of arg.
        """
        return ListSymbolValueContext(sdv, definition_source)

    @staticmethod
    def of_ddv(ddv: ListDdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'ListSymbolValueContext':
        return ListSymbolValueContext.of_sdv(ListSdvTestImplForConstantListDdv(ddv), definition_source)

    @staticmethod
    def of_constants(elements: Sequence[str],
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'ListSymbolValueContext':
        return ListSymbolValueContext.of_sdv(list_sdvs.from_str_constants(elements), definition_source)

    @staticmethod
    def of_empty(definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
                 ) -> 'ListSymbolValueContext':
        return ListSymbolValueContext.of_constants((), definition_source)

    @staticmethod
    def of_arbitrary_value() -> 'ListSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.LIST

    @property
    def assert_equals_sdv(self) -> Assertion[SymbolDependentValue]:
        return asrt_list.equals_list_sdv(self.sdv)

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return asrt_sym_ref.matches_reference_2(
            symbol_name,
            is_reference_restrictions__w_str_rendering())


class ListSymbolContext(DataTypeSymbolContext[ListSdv]):
    def __init__(self,
                 name: str,
                 value: ListSymbolValueContext,
                 ):
        super().__init__(name, )
        self._value = value

    @staticmethod
    def of_sdv(name: str,
               sdv: ListSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'ListSymbolContext':
        return ListSymbolContext(
            name,
            ListSymbolValueContext.of_sdv(sdv, definition_source)
        )

    @staticmethod
    def of_ddv(name: str,
               ddv: ListDdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'ListSymbolContext':
        return ListSymbolContext(name, ListSymbolValueContext.of_ddv(ddv, definition_source))

    @staticmethod
    def of_constants(name: str,
                     elements: Sequence[str],
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'ListSymbolContext':
        return ListSymbolContext(name, ListSymbolValueContext.of_constants(elements, definition_source))

    @staticmethod
    def of_empty(name: str) -> 'ListSymbolContext':
        return ListSymbolContext(name, ListSymbolValueContext.of_empty())

    @staticmethod
    def of_arbitrary_value(name: str) -> 'ListSymbolContext':
        return ListSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)

    @property
    def value(self) -> ListSymbolValueContext:
        return self._value


class ListDdvSymbolContext(ListSymbolContext):
    def __init__(self,
                 name: str,
                 ddv: ListDdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(name, ListSymbolValueContext.of_ddv(ddv, definition_source))
        self._ddv = ddv

    @staticmethod
    def of_constants(name: str,
                     elements: Sequence[str],
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'ListDdvSymbolContext':
        return ListDdvSymbolContext(name,
                                    _ddv_of_constant(elements),
                                    definition_source)

    @property
    def ddv(self) -> ListDdv:
        return self._ddv


class ListConstantSymbolContext(ListDdvSymbolContext):
    def __init__(self,
                 name: str,
                 constant: Sequence[str],
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(name, _ddv_of_constant(constant), definition_source)
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
