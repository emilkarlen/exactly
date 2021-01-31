from abc import ABC, abstractmethod
from typing import Generic, Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolUsage, SymbolContainer, SymbolDependentValue, \
    SymbolDefinition
from exactly_lib.symbol.value_type import DataValueType
from exactly_lib.type_val_deps.sym_ref.data import reference_restrictions
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.symbol_context import SDV_TYPE, SymbolValueContext, SymbolContext
from exactly_lib_test.symbol.test_resources.symbol_usage_assertions import matches_definition
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.data.test_resources import concrete_restriction_assertion as asrt_rest
from exactly_lib_test.type_val_deps.sym_ref.test_resources.container_assertions import matches_container_of_data_type


class DataSymbolValueContext(Generic[SDV_TYPE], SymbolValueContext[SDV_TYPE], ABC):
    def __init__(self,
                 sdv: SDV_TYPE,
                 definition_source: Optional[SourceLocationInfo],
                 ):
        super().__init__(sdv, definition_source)

    @property
    @abstractmethod
    def data_value_type(self) -> DataValueType:
        pass

    @staticmethod
    def reference_assertion__any_data_type(symbol_name: str) -> Assertion[SymbolReference]:
        return asrt_sym_usage.matches_reference_2__ref(
            symbol_name,
            asrt_rest.is_any_data_type_reference_restrictions()
        )

    @staticmethod
    def usage_assertion__any_data_type(symbol_name: str) -> Assertion[SymbolUsage]:
        return asrt_sym_usage.matches_reference_2(
            symbol_name,
            asrt_rest.is_any_data_type_reference_restrictions()
        )

    @property
    def assert_matches_container_of_sdv(self) -> Assertion[SymbolContainer]:
        return matches_container_of_data_type(
            data_value_type=self.data_value_type,
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
    def reference__any_data_type(self) -> SymbolReference:
        return SymbolReference(
            self.name,
            reference_restrictions.is_any_data_type()
        )

    @property
    def reference_assertion__any_data_type(self) -> Assertion[SymbolReference]:
        return DataSymbolValueContext.reference_assertion__any_data_type(self.name)

    @property
    def reference_assertion__convertible_to_string(self) -> Assertion[SymbolReference]:
        return DataSymbolValueContext.reference_assertion__any_data_type(self.name)

    @property
    def usage_assertion__any_data_type(self) -> Assertion[SymbolUsage]:
        return DataSymbolValueContext.usage_assertion__any_data_type(self.name)

    @property
    def assert_matches_definition_of_sdv(self) -> Assertion[SymbolDefinition]:
        return matches_definition(
            name=asrt.equals(self.name),
            container=self.value.assert_matches_container_of_sdv
        )
