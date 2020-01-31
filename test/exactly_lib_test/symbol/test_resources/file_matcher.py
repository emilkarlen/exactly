from typing import Sequence

from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.matcher.impls import sdv_components, ddv_components
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherDdv, GenericFileMatcherSdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import SdvSymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources import file_matchers


def arbitrary_sdv() -> FileMatcherSdv:
    return file_matcher_sdv_constant_test_impl(
        file_matchers.arbitrary_file_matcher()
    )


def file_matcher_sdv_constant_test_impl(resolved_value: FileMatcher,
                                        references: Sequence[SymbolReference] = ()) -> FileMatcherSdv:
    return file_matcher_sdv_constant_value_test_impl(
        ddv_components.MatcherDdvFromConstantPrimitive(resolved_value),
        references,
    )


def file_matcher_sdv_constant_value_test_impl(resolved_value: FileMatcherDdv,
                                              references: Sequence[SymbolReference] = ()) -> FileMatcherSdv:
    def make_ddv(symbols: SymbolTable) -> FileMatcherDdv:
        return resolved_value

    return FileMatcherSdv(
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


class FileMatcherSymbolContext(SdvSymbolContext[FileMatcherSdv]):
    def __init__(self,
                 name: str,
                 sdv: FileMatcherSdv):
        super().__init__(name)
        self._sdv = sdv

    @staticmethod
    def of_generic(name: str, sdv: GenericFileMatcherSdv) -> 'FileMatcherSymbolContext':
        return FileMatcherSymbolContext(
            name,
            FileMatcherSdv(sdv)
        )

    @property
    def sdv(self) -> FileMatcherSdv:
        return self._sdv

    @property
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return is_file_matcher_reference_to__ref(self.name)
