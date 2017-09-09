from exactly_lib.named_element.resolver_structure import FileMatcherResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.test_case_utils.file_matcher.test_resources.value_assertions import equals_file_matcher
from exactly_lib_test.test_case_utils.test_resources import resolver_assertions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def resolved_value_equals_file_matcher(expected: FileMatcher,
                                       expected_references: asrt.ValueAssertion = asrt.is_empty_list,
                                       symbols: symbol_table.SymbolTable = None) -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`FileMatcherResolver`
    """
    return resolver_assertions.matches_resolver_of_logic_type(FileMatcherResolver,
                                                              LogicValueType.FILE_MATCHER,
                                                              ValueType.FILE_MATCHER,
                                                              equals_file_matcher(expected),
                                                              expected_references,
                                                              symbols)
