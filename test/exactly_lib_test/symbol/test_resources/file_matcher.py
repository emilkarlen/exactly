from typing import Sequence

from exactly_lib.symbol.resolver_structure import FileMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import resolver_structure_assertions as asrt_ne
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


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

    def resolve(self, named_elements: SymbolTable) -> FileMatcher:
        return self._resolved_value


IS_FILE_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.FILE_MATCHER)


def is_file_matcher_reference_to(symbol_name: str) -> asrt.ValueAssertion:
    return asrt_ne.matches_reference(asrt.equals(symbol_name),
                                     IS_FILE_REFERENCE_RESTRICTION)
