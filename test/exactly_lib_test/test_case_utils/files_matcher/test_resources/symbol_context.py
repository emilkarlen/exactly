from typing import Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.logic.files_matcher import FilesMatcherStv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolContainer
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.logic.files_matcher import GenericFilesMatcherSdv, FilesMatcher
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref
from exactly_lib_test.symbol.test_resources.symbols_setup import LogicSymbolValueContext, LogicTypeSymbolContext, \
    ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class FilesMatcherSymbolValueContext(LogicSymbolValueContext[FilesMatcherStv]):
    def __init__(self,
                 sdv: FilesMatcherStv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_generic(sdv: GenericFilesMatcherSdv,
                   definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                   ) -> 'FilesMatcherSymbolValueContext':
        return FilesMatcherSymbolValueContext(FilesMatcherStv(sdv),
                                              definition_source)

    @staticmethod
    def of_primitive(primitive: FilesMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'FilesMatcherSymbolValueContext':
        return FilesMatcherSymbolValueContext.of_generic(matchers.sdv_from_primitive_value(primitive),
                                                         definition_source)

    @staticmethod
    def of_primitive_constant(result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'FilesMatcherSymbolValueContext':
        return FilesMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                           definition_source)

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_reference_to_files_matcher__ref(symbol_name)

    @property
    def container(self) -> SymbolContainer:
        return symbol_utils.container(self.sdtv)

    @property
    def container__of_builtin(self) -> SymbolContainer:
        return symbol_utils.container_of_builtin(self.sdtv)


class FilesMatcherSymbolContext(LogicTypeSymbolContext[FilesMatcherStv]):
    def __init__(self,
                 name: str,
                 value: FilesMatcherSymbolValueContext,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdtv(name: str,
                sdtv: FilesMatcherStv,
                definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                ) -> 'FilesMatcherSymbolContext':
        return FilesMatcherSymbolContext(
            name,
            FilesMatcherSymbolValueContext(sdtv, definition_source)
        )

    @staticmethod
    def of_generic(name: str,
                   sdv: GenericFilesMatcherSdv,
                   definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                   ) -> 'FilesMatcherSymbolContext':
        return FilesMatcherSymbolContext(
            name,
            FilesMatcherSymbolValueContext.of_generic(sdv, definition_source)
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


ARBITRARY_SYMBOL_VALUE_CONTEXT = FilesMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
