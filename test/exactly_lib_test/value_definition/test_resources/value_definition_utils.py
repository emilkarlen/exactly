import unittest

from exactly_lib.test_case_file_structure import file_ref as _file_ref
from exactly_lib.test_case_file_structure.file_ref_relativity import RelOptionType
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTable, Entry
from exactly_lib.value_definition.concrete_restrictions import NoRestriction
from exactly_lib.value_definition.concrete_values import FileRefValue, StringValue
from exactly_lib.value_definition.value_structure import ValueContainer, Value, ValueReference2, ValueRestriction, \
    ValueDefinition2
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def string_value_container(string_value: str,
                           line_num: int = 1,
                           source_line: str = 'value def line') -> ValueContainer:
    return ValueContainer(Line(line_num, source_line),
                          StringValue(string_value))


def value_reference(name: str, value_restriction: ValueRestriction = NoRestriction()) -> ValueReference2:
    return ValueReference2(name, value_restriction)


def string_value_definition(name: str, string_value: str = 'string value') -> ValueDefinition2:
    return ValueDefinition2(name, string_value_container(string_value))


def file_ref_value(file_ref: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                                    relativity=RelOptionType.REL_CWD)
                   ) -> FileRefValue:
    return FileRefValue(file_ref)


def file_ref_value_container(file_ref: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                                              relativity=RelOptionType.REL_CWD),
                             line_num: int = 1,
                             source_line: str = 'value def line') -> ValueContainer:
    return ValueContainer(Line(line_num, source_line),
                          FileRefValue(file_ref))


def entry(name: str, value: Value = StringValue('string value'),
          line_num: int = 1,
          source_line: str = 'value def line') -> Entry:
    return Entry(name, ValueContainer(Line(line_num, source_line), value))


def symbol_table_from_names(names: iter) -> SymbolTable:
    elements = [(name, string_value_container(name, source_line='source line for {}'.format(name)))
                for name in names]
    return SymbolTable(dict(elements))


def symbol_table_from_value_definitions(value_definitions: iter) -> SymbolTable:
    """
    :param value_definitions: [`ValueDefinition`]
    """
    elements = [(vd.name, vd.value_container)
                for vd in value_definitions]
    return SymbolTable(dict(elements))


def symbol_table_from_entries(entries: iter) -> SymbolTable:
    """
    :param entries: [`Entry`]
    """
    elements = [(entry.key, entry.value)
                for entry in entries]
    return SymbolTable(dict(elements))


def assert_value_usages_is_singleton_list(assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.matches_sequence([assertion])


class _AssertSymbolTableIsSingleton(asrt.ValueAssertion):
    def __init__(self,
                 expected_name: str,
                 value_assertion: asrt.ValueAssertion):
        self.expected_name = expected_name
        self.value_assertion = value_assertion

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        assert isinstance(value, SymbolTable)
        put.assertEqual(1,
                        len(value.names_set),
                        'Expecting a single entry')
        put.assertTrue(value.contains(self.expected_name),
                       'SymbolTable should contain the expected name')
        self.value_assertion.apply_with_message(put,
                                                value.lookup(self.expected_name),
                                                'value')


def assert_symbol_table_is_singleton(expected_name: str, value_assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return _AssertSymbolTableIsSingleton(expected_name, value_assertion)
