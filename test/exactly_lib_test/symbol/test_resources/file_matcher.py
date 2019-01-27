from typing import Sequence

from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherValue
from exactly_lib.type_system.logic.file_matchers import FileMatcherValueFromPrimitiveValue
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class FileMatcherResolverConstantTestImpl(FileMatcherResolver):
    def __init__(self, resolved_value: FileMatcher,
                 references: Sequence[SymbolReference] = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> FileMatcher:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> FileMatcherValue:
        return FileMatcherValueFromPrimitiveValue(self._resolved_value)


IS_FILE_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.FILE_MATCHER)


def is_file_matcher_reference_to(symbol_name: str) -> ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_FILE_REFERENCE_RESTRICTION)
