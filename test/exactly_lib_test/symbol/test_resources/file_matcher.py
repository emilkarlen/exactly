from typing import Sequence, Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.logic.file_matcher import FileMatcherStv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolContainer
from exactly_lib.test_case_utils.matcher.impls import sdv_components, ddv_components, constant
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherDdv, GenericFileMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage, symbol_utils
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import LogicTypeSymbolContext, LogicSymbolValueContext, \
    ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources import file_matchers


def arbitrary_sdv() -> FileMatcherStv:
    return file_matcher_sdv_constant_test_impl(
        file_matchers.arbitrary_file_matcher()
    )


def file_matcher_sdv_constant_test_impl(resolved_value: FileMatcher,
                                        references: Sequence[SymbolReference] = ()) -> FileMatcherStv:
    return file_matcher_sdv_constant_value_test_impl(
        ddv_components.MatcherDdvFromConstantPrimitive(resolved_value),
        references,
    )


def file_matcher_sdv_constant_value_test_impl(resolved_value: FileMatcherDdv,
                                              references: Sequence[SymbolReference] = ()) -> FileMatcherStv:
    def make_ddv(symbols: SymbolTable) -> FileMatcherDdv:
        return resolved_value

    return FileMatcherStv(
        sdv_components.MatcherSdvFromParts(
            references,
            make_ddv,
        )
    )


IS_FILE_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.FILE_MATCHER)


def is_file_matcher_reference_to(symbol_name: str) -> ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_FILE_REFERENCE_RESTRICTION)


def is_file_matcher_reference_to__ref(symbol_name: str) -> ValueAssertion[SymbolReference]:
    return asrt.is_instance_with(
        SymbolReference,
        asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                         IS_FILE_REFERENCE_RESTRICTION)
    )


class FileMatcherSymbolValueContext(LogicSymbolValueContext[FileMatcherStv]):
    def __init__(self,
                 sdv: FileMatcherStv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_generic(sdv: GenericFileMatcherSdv,
                   definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                   ) -> 'FileMatcherSymbolValueContext':
        return FileMatcherSymbolValueContext(FileMatcherStv(sdv), definition_source)

    @staticmethod
    def of_primitive(primitive: FileMatcher,
                     definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                     ) -> 'FileMatcherSymbolValueContext':
        return FileMatcherSymbolValueContext.of_generic(matchers.sdv_from_primitive_value(primitive),
                                                        definition_source)

    @staticmethod
    def of_primitive_constant(result: bool,
                              definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                              ) -> 'FileMatcherSymbolValueContext':
        return FileMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(result),
                                                          definition_source)

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_file_matcher_reference_to__ref(symbol_name)

    @property
    def container(self) -> SymbolContainer:
        return symbol_utils.container(self.sdtv)

    @property
    def container__of_builtin(self) -> SymbolContainer:
        return symbol_utils.container_of_builtin(self.sdtv)


class FileMatcherSymbolContext(LogicTypeSymbolContext[FileMatcherStv]):
    def __init__(self,
                 name: str,
                 value: FileMatcherSymbolValueContext,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdtv(name: str,
                sdtv: FileMatcherStv,
                definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                ) -> 'FileMatcherSymbolContext':
        return FileMatcherSymbolContext(
            name,
            FileMatcherSymbolValueContext(sdtv, definition_source)
        )

    @staticmethod
    def of_generic(name: str,
                   sdv: GenericFileMatcherSdv,
                   definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                   ) -> 'FileMatcherSymbolContext':
        return FileMatcherSymbolContext(
            name,
            FileMatcherSymbolValueContext.of_generic(sdv, definition_source)
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


ARBITRARY_SYMBOL_VALUE_CONTEXT = FileMatcherSymbolValueContext.of_primitive(constant.MatcherWithConstantResult(True))
