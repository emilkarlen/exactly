from typing import Optional

from exactly_lib.impls.types.matcher.impls import constant
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherSdv
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcher, FileMatcherModel
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as args
from exactly_lib_test.impls.types.file_matcher.test_resources.argument_building import FileMatcherArg
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.abstract_syntax import \
    FileMatcherSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.references import is_reference_to_file_matcher
from exactly_lib_test.type_val_deps.types.test_resources.matcher_symbol_context import MatcherSymbolValueContext, \
    MatcherTypeSymbolContext


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
        return FileMatcherSymbolValueContext.of_sdv(
            sdv_ddv.sdv_from_primitive_value(primitive),
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

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return is_reference_to_file_matcher(symbol_name)


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

    @property
    def argument(self) -> FileMatcherArg:
        return args.SymbolReferenceWReferenceSyntax(self.name)

    @property
    def abstract_syntax(self) -> FileMatcherSymbolReferenceAbsStx:
        return FileMatcherSymbolReferenceAbsStx(self.name)


class FileMatcherSymbolContextOfPrimitiveConstant(FileMatcherSymbolContext):
    def __init__(self,
                 name: str,
                 result: bool,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(name,
                         FileMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                                    definition_source))
        self._result = result

    @property
    def result_value(self) -> bool:
        return self._result


ARBITRARY_SYMBOL_VALUE_CONTEXT = FileMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
