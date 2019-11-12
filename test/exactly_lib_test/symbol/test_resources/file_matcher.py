from typing import Sequence

from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.file_matcher.file_matcher_ddvs import FileMatcherValueFromPrimitiveDdv
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import ResolverSymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources import file_matchers


def arbitrary_resolver() -> FileMatcherResolver:
    return FileMatcherResolverConstantTestImpl(
        file_matchers.arbitrary_file_matcher()
    )


class FileMatcherResolverConstantTestImpl(FileMatcherResolver):
    def __init__(self,
                 resolved_value: FileMatcher,
                 references: Sequence[SymbolReference] = ()):
        self._references = list(references)
        self._resolved_value = resolved_value

    @property
    def resolved_value(self) -> FileMatcher:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        return FileMatcherValueFromPrimitiveDdv(self._resolved_value)


class FileMatcherResolverConstantValueTestImpl(FileMatcherResolver):
    def __init__(self,
                 resolved_value: FileMatcherDdv,
                 references: Sequence[SymbolReference] = ()):
        self._references = list(references)
        self._resolved_value = resolved_value

    @property
    def resolved_value(self) -> FileMatcherDdv:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        return self._resolved_value


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


class FileMatcherSymbolContext(ResolverSymbolContext[FileMatcherResolver]):
    def __init__(self,
                 name: str,
                 resolver: FileMatcherResolver):
        super().__init__(name)
        self._resolver = resolver

    @property
    def resolver(self) -> FileMatcherResolver:
        return self._resolver

    @property
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return is_file_matcher_reference_to__ref(self.name)
