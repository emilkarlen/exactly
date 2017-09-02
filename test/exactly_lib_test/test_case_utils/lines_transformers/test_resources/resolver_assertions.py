from exactly_lib.named_element import resolver_structure
from exactly_lib.named_element.resolver_structure import LinesTransformerResolver
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.named_element.test_resources.type_assertions import is_resolver_of_logic_type
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.value_assertions import equals_lines_transformer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def resolved_value_equals_lines_transformer(value: LinesTransformer,
                                            references: asrt.ValueAssertion = asrt.is_empty_list,
                                            symbols: symbol_table.SymbolTable = None) -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`LinesTransformerResolver`
    """
    named_elements = symbol_table.symbol_table_from_none_or_value(symbols)

    def resolve_value(resolver: LinesTransformerResolver) -> LinesTransformer:
        return resolver.resolve(named_elements)

    return asrt.is_instance_with(LinesTransformerResolver,
                                 asrt.and_([
                                     is_resolver_of_logic_type(LogicValueType.LINES_TRANSFORMER,
                                                               ValueType.LINES_TRANSFORMER),

                                     asrt.on_transformed(resolve_value,
                                                         equals_lines_transformer(value,
                                                                                  'resolved lines transformer')),

                                     asrt.sub_component('references',
                                                        resolver_structure.get_references,
                                                        references),
                                 ]))
