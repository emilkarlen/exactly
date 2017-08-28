from exactly_lib.named_element import resolver_structure
from exactly_lib.named_element.resolver_structure import FileSelectorResolver
from exactly_lib.type_system_values.file_selector import FileSelector
from exactly_lib.type_system_values.value_type import ElementType
from exactly_lib.util import symbol_table
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system_values.test_resources.file_selector_assertions import equals_file_selector


def resolved_value_equals_file_selector(expected: FileSelector,
                                        expected_references: asrt.ValueAssertion = asrt.is_empty_list,
                                        environment: symbol_table.SymbolTable = None) -> asrt.ValueAssertion:
    """
    :return: A assertion on a :class:`FileSelectorResolver`
    """
    named_elements = symbol_table.symbol_table_from_none_or_value(environment)

    def resolve_value(resolver: FileSelectorResolver) -> FileSelector:
        return resolver.resolve(named_elements)

    return asrt.is_instance_with(FileSelectorResolver,
                                 asrt.and_([
                                     asrt.sub_component('element_type',
                                                        resolver_structure.get_element_type,
                                                        asrt.is_(ElementType.FILE_SELECTOR)),

                                     asrt.on_transformed(resolve_value,
                                                         equals_file_selector(expected,
                                                                              'resolved file selector')),

                                     asrt.sub_component('references',
                                                        resolver_structure.get_references,
                                                        expected_references),
                                 ]))
