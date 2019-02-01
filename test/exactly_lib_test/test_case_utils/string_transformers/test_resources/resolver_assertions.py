from typing import Sequence

from exactly_lib.symbol.logic.logic_value_resolver import LogicValueResolver
from exactly_lib.symbol.logic.string_transformer import StringTransformerResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.line_matcher import LineMatcher
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.test_case_utils.string_transformers.test_resources.transformers import replace_transformer, \
    select_regex_transformer, select_transformer
from exactly_lib_test.test_case_utils.string_transformers.test_resources.value_assertions import \
    equals_string_transformer
from exactly_lib_test.test_case_utils.test_resources import resolver_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def resolved_value_equals_string_transformer(value: StringTransformer,
                                             references: ValueAssertion[
                                                 Sequence[SymbolReference]] = asrt.is_empty_sequence,
                                             symbols: symbol_table.SymbolTable = None
                                             ) -> ValueAssertion[LogicValueResolver]:
    return resolver_assertions.matches_resolver_of_logic_type2(StringTransformerResolver,
                                                               LogicValueType.STRING_TRANSFORMER,
                                                               ValueType.STRING_TRANSFORMER,
                                                               equals_string_transformer(value,
                                                                                         'resolved string transformer'),
                                                               references,
                                                               symbols)


def resolved_value_is_replace_transformer(regex_str: str,
                                          replacement_str: str,
                                          references: ValueAssertion = asrt.is_empty_sequence
                                          ) -> ValueAssertion[LogicValueResolver]:
    expected_transformer = replace_transformer(regex_str, replacement_str)
    return resolved_value_equals_string_transformer(expected_transformer,
                                                    references=references)


def resolved_value_is_select_regex_transformer(regex_str: str,
                                               references: ValueAssertion = asrt.is_empty_sequence
                                               ) -> ValueAssertion[LogicValueResolver]:
    expected_transformer = select_regex_transformer(regex_str)
    return resolved_value_equals_string_transformer(expected_transformer,
                                                    references=references)


def resolved_value_is_select_transformer(line_matcher: LineMatcher,
                                         references: ValueAssertion = asrt.is_empty_sequence
                                         ) -> ValueAssertion[LogicValueResolver]:
    expected_transformer = select_transformer(line_matcher)
    return resolved_value_equals_string_transformer(expected_transformer,
                                                    references=references)
