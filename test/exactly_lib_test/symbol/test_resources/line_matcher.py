from typing import Sequence

from exactly_lib.symbol.logic.line_matcher import LineMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator, constant_success_validator
from exactly_lib.test_case_utils.line_matcher.line_matcher_values import LineMatcherValueFromPrimitiveValue
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib.test_case_utils.line_matcher.resolvers import LineMatcherResolverFromParts
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherValue, LineMatcherLine
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class LineMatcherConstantTestImpl(LineMatcher):
    """Matcher with constant result."""

    def __init__(self, result: bool):
        self._result = result

    @property
    def option_description(self) -> str:
        return 'any line' if self._result else 'no line'

    @property
    def result_constant(self) -> bool:
        return self._result

    def matches(self, line: LineMatcherLine) -> bool:
        return self._result


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
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> LineMatcherValue:
        return LineMatcherValueFromPrimitiveValue(self._resolved_value)


class LineMatcherResolverConstantValueTestImpl(LineMatcherResolver):
    def __init__(self,
                 resolved_value: LineMatcherValue,
                 references: Sequence[SymbolReference] = ()):
        self._resolved_value = resolved_value
        self._references = list(references)

    @property
    def resolved_value(self) -> LineMatcher:
        return self._resolved_value

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._references

    def resolve(self, symbols: SymbolTable) -> LineMatcherValue:
        return self._resolved_value


IS_LINE_MATCHER_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.LINE_MATCHER)


def is_line_matcher_reference_to(symbol_name: str) -> ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_LINE_MATCHER_REFERENCE_RESTRICTION)


def successful_matcher_with_validation(validator: PreOrPostSdsValueValidator):
    return LineMatcherResolverConstantValueTestImpl(
        LineMatcherValueFromPrimitiveValue(
            LineMatcherConstantTestImpl(True),
            validator
        )
    )


def line_matcher_from_primitive_value(resolved_value: LineMatcher = LineMatcherConstant(True),
                                      references: Sequence[SymbolReference] = (),
                                      validator: PreOrPostSdsValueValidator = constant_success_validator(),
                                      ) -> LineMatcherResolver:
    def get_value(symbol: SymbolTable) -> LineMatcherValue:
        return LineMatcherValueFromPrimitiveValue(resolved_value, validator)

    return LineMatcherResolverFromParts(
        references=references,
        make_value=get_value,
    )


def resolver_of_unconditionally_matching_matcher() -> LineMatcherResolver:
    return LineMatcherResolverConstantTestImpl(LineMatcherConstantTestImpl(True))


def value_of_unconditionally_matching_matcher() -> LineMatcherValue:
    return LineMatcherValueFromPrimitiveValue(
        LineMatcherConstantTestImpl(True)
    )
