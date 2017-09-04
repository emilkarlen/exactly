from exactly_lib.named_element import resolver_structure
from exactly_lib.named_element.resolver_structure import FileMatcherResolver
from exactly_lib.test_case_utils.file_matcher.file_matchers import FileMatcherFromSelectors
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.named_element.test_resources.type_assertions import is_resolver_of_logic_type
from exactly_lib_test.test_case_utils.file_matcher.test_resources.value_assertions import equals_file_selector
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def resolved_value_equals_file_selector(expected: FileMatcherFromSelectors,
                                        expected_references: asrt.ValueAssertion = asrt.is_empty_list,
                                        environment: symbol_table.SymbolTable = None) -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`FileSelectorResolver`
    """
    named_elements = symbol_table.symbol_table_from_none_or_value(environment)

    def resolve_value(resolver: FileMatcherResolver) -> FileMatcher:
        return resolver.resolve(named_elements)

    return asrt.is_instance_with(FileMatcherResolver,
                                 asrt.and_([
                                     is_resolver_of_logic_type(LogicValueType.FILE_MATCHER,
                                                               ValueType.FILE_MATCHER),

                                     asrt.on_transformed(resolve_value,
                                                         equals_file_selector(expected,
                                                                              'resolved file selector')),

                                     asrt.sub_component('references',
                                                        resolver_structure.get_references,
                                                        expected_references),
                                 ]))
