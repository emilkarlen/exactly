from typing import Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.logic.files_matcher import FilesMatcherSdv, FilesMatcher, FilesMatcherModel
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref
from exactly_lib_test.symbol.test_resources.symbols_setup import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION, \
    MatcherSymbolValueContext, MatcherTypeSymbolContext
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class FilesMatcherSymbolValueContext(MatcherSymbolValueContext[FilesMatcherModel]):
    def __init__(self,
                 sdv: FilesMatcherSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_sdv(sdv: FilesMatcherSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'FilesMatcherSymbolValueContext':
        return FilesMatcherSymbolValueContext(sdv,
                                              definition_source)

    @staticmethod
    def of_primitive(primitive: FilesMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'FilesMatcherSymbolValueContext':
        return FilesMatcherSymbolValueContext.of_sdv(matchers.sdv_from_primitive_value(primitive),
                                                     definition_source)

    @staticmethod
    def of_primitive_constant(result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'FilesMatcherSymbolValueContext':
        return FilesMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                           definition_source)

    @staticmethod
    def of_arbitrary_value() -> 'FilesMatcherSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILES_MATCHER

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_reference_to_files_matcher__ref(symbol_name)


class FilesMatcherSymbolContext(MatcherTypeSymbolContext[FilesMatcherModel]):
    def __init__(self,
                 name: str,
                 value: FilesMatcherSymbolValueContext,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdv(name: str,
               sdv: FilesMatcherSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'FilesMatcherSymbolContext':
        return FilesMatcherSymbolContext(
            name,
            FilesMatcherSymbolValueContext.of_sdv(sdv, definition_source)
        )

    @staticmethod
    def of_primitive(name: str,
                     primitive: FilesMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'FilesMatcherSymbolContext':
        return FilesMatcherSymbolContext(
            name,
            FilesMatcherSymbolValueContext.of_primitive(primitive, definition_source)
        )

    @staticmethod
    def of_primitive_constant(name: str,
                              result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'FilesMatcherSymbolContext':
        return FilesMatcherSymbolContext.of_primitive(name,
                                                      constant.MatcherWithConstantResult(result),
                                                      definition_source)

    @staticmethod
    def of_arbitrary_value(name: str) -> 'FilesMatcherSymbolContext':
        return FilesMatcherSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)


ARBITRARY_SYMBOL_VALUE_CONTEXT = FilesMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
