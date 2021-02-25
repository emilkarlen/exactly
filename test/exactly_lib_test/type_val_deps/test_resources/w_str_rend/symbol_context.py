from abc import ABC, abstractmethod
from typing import Generic, Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolUsage, SymbolContainer, SymbolDependentValue, \
    SymbolDefinition
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.symbol_context import SDV_TYPE, SymbolValueContext, SymbolContext
from exactly_lib_test.symbol.test_resources.symbol_usage_assertions import matches_definition
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.sym_ref.test_resources.container_assertions import \
    matches_container
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_rest


class DataSymbolValueContext(Generic[SDV_TYPE], SymbolValueContext[SDV_TYPE], ABC):
    def __init__(self,
                 sdv: SDV_TYPE,
                 definition_source: Optional[SourceLocationInfo],
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def reference_assertion__w_str_rendering(symbol_name: str) -> Assertion[SymbolReference]:
        return asrt_sym_usage.matches_reference_2__ref(
            symbol_name,
            asrt_rest.is__w_str_rendering()
        )

    @staticmethod
    def usage_assertion__w_str_rendering(symbol_name: str) -> Assertion[SymbolUsage]:
        return asrt_sym_usage.matches_reference_2(
            symbol_name,
            asrt_rest.is__w_str_rendering()
        )

    @property
    def assert_matches_container_of_sdv(self) -> Assertion[SymbolContainer]:
        return matches_container(
            value_type=asrt.equals(self.value_type),
            sdv=self.assert_equals_sdv,
            definition_source=asrt.anything_goes()
        )

    @property
    @abstractmethod
    def assert_equals_sdv(self) -> Assertion[SymbolDependentValue]:
        pass


class DataTypeSymbolContext(Generic[SDV_TYPE], SymbolContext[SDV_TYPE], ABC):
    def __init__(self, name: str, ):
        super().__init__(name)

    @property
    @abstractmethod
    def value(self) -> DataSymbolValueContext[SDV_TYPE]:
        pass

    @property
    def reference__w_str_rendering(self) -> SymbolReference:
        return SymbolReference(
            self.name,
            reference_restrictions.is_any_type_w_str_rendering()
        )

    @property
    def reference_assertion__w_str_rendering(self) -> Assertion[SymbolReference]:
        return DataSymbolValueContext.reference_assertion__w_str_rendering(self.name)

    @property
    def usage_assertion__w_str_rendering(self) -> Assertion[SymbolUsage]:
        return DataSymbolValueContext.usage_assertion__w_str_rendering(self.name)

    @property
    def assert_matches_definition_of_sdv(self) -> Assertion[SymbolDefinition]:
        return matches_definition(
            name=asrt.equals(self.name),
            container=self.value.assert_matches_container_of_sdv
        )
