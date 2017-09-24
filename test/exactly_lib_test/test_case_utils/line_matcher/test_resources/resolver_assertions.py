from exactly_lib.symbol.resolver_structure import LineMatcherResolver
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.test_case_utils.line_matcher.test_resources.value_assertions import equals_line_matcher
from exactly_lib_test.test_case_utils.test_resources.resolver_assertions import matches_resolver_of_logic_type
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def resolved_value_equals_line_matcher(value: LineMatcher,
                                       references: asrt.ValueAssertion = asrt.is_empty_list,
                                       symbols: symbol_table.SymbolTable = None) -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`LineMatcherResolver`
    """
    return matches_resolver_of_logic_type(LineMatcherResolver,
                                          LogicValueType.LINE_MATCHER,
                                          ValueType.LINE_MATCHER,
                                          equals_line_matcher(value),
                                          references,
                                          symbols)
