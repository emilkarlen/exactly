from typing import Optional

from exactly_lib.impls.types.matcher.impls import constant
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.files_matcher import FilesMatcherSdv
from exactly_lib.type_val_prims.matcher.files_matcher import FilesMatcher, FilesMatcherModel
from exactly_lib_test.impls.types.files_matcher.test_resources import arguments_building as args
from exactly_lib_test.impls.types.files_matcher.test_resources.arguments_building import FilesMatcherArg
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources.abstract_syntax import \
    FilesMatcherSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.test_resources.files_matcher import is_reference_to_files_matcher
from exactly_lib_test.type_val_deps.types.test_resources.matcher_symbol_context import MatcherSymbolValueContext, \
    MatcherTypeSymbolContext


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
        return FilesMatcherSymbolValueContext.of_sdv(
            sdv_ddv.sdv_from_primitive_value(primitive),
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

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return is_reference_to_files_matcher(symbol_name)


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

    @property
    def argument(self) -> FilesMatcherArg:
        return args.SymbolReferenceWReferenceSyntax(self.name)

    @property
    def abstract_syntax(self) -> FilesMatcherSymbolReferenceAbsStx:
        return FilesMatcherSymbolReferenceAbsStx(self.name)


class FilesMatcherSymbolContextOfPrimitiveConstant(FilesMatcherSymbolContext):
    def __init__(self,
                 name: str,
                 result: bool,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(name,
                         FilesMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                                     definition_source))
        self._result = result

    @property
    def result_value(self) -> bool:
        return self._result


ARBITRARY_SYMBOL_VALUE_CONTEXT = FilesMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
