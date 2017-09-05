from exactly_lib.named_element import resolver_structure
from exactly_lib.named_element.resolver_structure import LineMatcherResolver
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.named_element.test_resources.type_assertions import is_resolver_of_logic_type
from exactly_lib_test.test_case_utils.line_matcher.test_resources.value_assertions import equals_line_matcher
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def resolved_value_equals_line_matcher(value: LineMatcher,
                                       references: asrt.ValueAssertion = asrt.is_empty_list,
                                       symbols: symbol_table.SymbolTable = None) -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`LinesTransformerResolver`
    """
    named_elements = symbol_table.symbol_table_from_none_or_value(symbols)

    def resolve_value(resolver: LineMatcherResolver) -> LineMatcher:
        return resolver.resolve(named_elements)

    return asrt.is_instance_with(LineMatcherResolver,
                                 asrt.and_([
                                     is_resolver_of_logic_type(LogicValueType.LINE_MATCHER,
                                                               ValueType.LINE_MATCHER),

                                     asrt.on_transformed(resolve_value,
                                                         equals_line_matcher(value,
                                                                             'resolved matcher')),

                                     asrt.sub_component('references',
                                                        resolver_structure.get_references,
                                                        references),
                                 ]))
