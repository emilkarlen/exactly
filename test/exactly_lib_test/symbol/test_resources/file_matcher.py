from typing import Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherSdv, \
    FileMatcherModel
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION, \
    MatcherSymbolValueContext, MatcherTypeSymbolContext
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

IS_FILE_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.FILE_MATCHER)


def is_reference_to_file_matcher(symbol_name: str) -> ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_FILE_REFERENCE_RESTRICTION)


def is_reference_to_file_matcher__ref(symbol_name: str) -> ValueAssertion[SymbolReference]:
    return asrt.is_instance_with(
        SymbolReference,
        asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                         IS_FILE_REFERENCE_RESTRICTION)
    )


class FileMatcherSymbolValueContext(MatcherSymbolValueContext[FileMatcherModel]):
    def __init__(self,
                 sdv: FileMatcherSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_sdv(sdv: FileMatcherSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'FileMatcherSymbolValueContext':
        return FileMatcherSymbolValueContext(sdv, definition_source)

    @staticmethod
    def of_primitive(primitive: FileMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'FileMatcherSymbolValueContext':
        return FileMatcherSymbolValueContext.of_sdv(matchers.sdv_from_primitive_value(primitive),
                                                    definition_source)

    @staticmethod
    def of_primitive_constant(result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'FileMatcherSymbolValueContext':
        return FileMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                          definition_source)

    @staticmethod
    def of_arbitrary_value() -> 'FileMatcherSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILE_MATCHER

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_reference_to_file_matcher__ref(symbol_name)


class FileMatcherSymbolContext(MatcherTypeSymbolContext[FileMatcherModel]):
    def __init__(self,
                 name: str,
                 value: FileMatcherSymbolValueContext,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdv(name: str,
               sdv: FileMatcherSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'FileMatcherSymbolContext':
        return FileMatcherSymbolContext(
            name,
            FileMatcherSymbolValueContext.of_sdv(sdv, definition_source)
        )

    @staticmethod
    def of_primitive(name: str,
                     primitive: FileMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'FileMatcherSymbolContext':
        return FileMatcherSymbolContext(
            name,
            FileMatcherSymbolValueContext.of_primitive(primitive, definition_source)
        )

    @staticmethod
    def of_primitive_constant(name: str,
                              result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'FileMatcherSymbolContext':
        return FileMatcherSymbolContext.of_primitive(name,
                                                     constant.MatcherWithConstantResult(result),
                                                     definition_source)

    @staticmethod
    def of_arbitrary_value(name: str) -> 'FileMatcherSymbolContext':
        return FileMatcherSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)


ARBITRARY_SYMBOL_VALUE_CONTEXT = FileMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
