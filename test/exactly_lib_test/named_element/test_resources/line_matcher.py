from exactly_lib.named_element.resolver_structure import LineMatcherResolver
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.named_element.test_resources import resolver_structure_assertions as asrt_ne
from exactly_lib_test.named_element.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


class LineMatcherResolverConstantTestImpl(LineMatcherResolver):
    def __init__(self,
                 resolved_value: LineMatcher,
                 references: list = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> LineMatcher:
        return self._resolved_value

    @property
    def references(self) -> list:
        return self._references

    def resolve(self, symbols: SymbolTable) -> LineMatcher:
        return self._resolved_value


IS_LINE_MATCHER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.LINE_MATCHER)


def is_line_matcher_reference_to(symbol_name: str) -> asrt.ValueAssertion:
    return asrt_ne.matches_reference(asrt.equals(symbol_name),
                                     IS_LINE_MATCHER_REFERENCE_RESTRICTION)
