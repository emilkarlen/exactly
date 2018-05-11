from exactly_lib.symbol.resolver_structure import StringTransformerResolver, LogicValueResolver
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.test_case_utils.string_transformers.test_resources.value_assertions import \
    equals_lines_transformer
from exactly_lib_test.test_case_utils.test_resources import resolver_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def resolved_value_equals_lines_transformer(value: StringTransformer,
                                            references: asrt.ValueAssertion = asrt.is_empty_sequence,
                                            symbols: symbol_table.SymbolTable = None
                                            ) -> asrt.ValueAssertion[LogicValueResolver]:
    return resolver_assertions.matches_resolver_of_logic_type2(StringTransformerResolver,
                                                               LogicValueType.STRING_TRANSFORMER,
                                                               ValueType.STRING_TRANSFORMER,
                                                               equals_lines_transformer(value,
                                                                                        'resolved lines transformer'),
                                                               references,
                                                               symbols)
