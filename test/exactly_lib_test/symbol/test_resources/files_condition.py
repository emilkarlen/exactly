from typing import Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_utils.files_condition.structure import FilesConditionSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import LogicTypeSymbolContext, LogicSymbolValueContext, \
    ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

IS_FILES_CONDITION_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.FILES_CONDITION)


def arbitrary_sdv() -> FilesConditionSdv:
    return FilesConditionSdv.empty()


def is_files_condition_reference_to(symbol_name: str) -> ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_FILES_CONDITION_REFERENCE_RESTRICTION)


class FilesConditionSymbolValueContext(LogicSymbolValueContext[FilesConditionSdv]):
    def __init__(self,
                 sdv: FilesConditionSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_sdv(sdv: FilesConditionSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'FilesConditionSymbolValueContext':
        return FilesConditionSymbolValueContext(sdv,
                                                definition_source)

    @staticmethod
    def of_arbitrary_value() -> 'FilesConditionSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILES_CONDITION

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_files_condition_reference_to(symbol_name)


class FilesConditionSymbolContext(LogicTypeSymbolContext[FilesConditionSdv]):
    def __init__(self,
                 name: str,
                 value: FilesConditionSymbolValueContext,
                 ):
        super().__init__(name)
        self._value = value

    @staticmethod
    def of_sdv(name: str,
               sdv: FilesConditionSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'FilesConditionSymbolContext':
        return FilesConditionSymbolContext(
            name,
            FilesConditionSymbolValueContext.of_sdv(sdv, definition_source)
        )

    @staticmethod
    def of_arbitrary_value(name: str) -> 'FilesConditionSymbolContext':
        return FilesConditionSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)

    @property
    def value(self) -> FilesConditionSymbolValueContext:
        return self._value


ARBITRARY_SYMBOL_VALUE_CONTEXT = FilesConditionSymbolValueContext.of_sdv(arbitrary_sdv())
