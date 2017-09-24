from exactly_lib.symbol.resolver_structure import LinesTransformerResolver
from exactly_lib.type_system.logic.lines_transformer import LinesTransformer
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.test_case_utils.lines_transformers.test_resources.value_assertions import equals_lines_transformer
from exactly_lib_test.test_case_utils.test_resources import resolver_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def resolved_value_equals_lines_transformer(value: LinesTransformer,
                                            references: asrt.ValueAssertion = asrt.is_empty_list,
                                            symbols: symbol_table.SymbolTable = None) -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`LinesTransformerResolver`
    """
    return resolver_assertions.matches_resolver_of_logic_type(LinesTransformerResolver,
                                                              LogicValueType.LINES_TRANSFORMER,
                                                              ValueType.LINES_TRANSFORMER,
                                                              equals_lines_transformer(value,
                                                                                       'resolved lines transformer'),
                                                              references,
                                                              symbols)
