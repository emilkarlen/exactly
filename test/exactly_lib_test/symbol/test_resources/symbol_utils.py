import unittest

from exactly_lib.symbol.concrete_restrictions import NoRestriction, ReferenceRestrictionsOnDirectAndIndirect
from exactly_lib.symbol.concrete_values import FileRefResolver
from exactly_lib.symbol.string_resolver import string_constant
from exactly_lib.symbol.symbol_usage import SymbolDefinition, SymbolReference
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.symbol.value_restriction import ValueRestriction
from exactly_lib.symbol.value_structure import ValueContainer, Value
from exactly_lib.test_case_file_structure import file_ref as _file_ref
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTable, Entry
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def container(value: Value,
              line_num: int = 1,
              source_line: str = 'value def line') -> ValueContainer:
    return ValueContainer(Line(line_num, source_line),
                          value)


def string_value_container(string_value: str,
                           line_num: int = 1,
                           source_line: str = 'value def line') -> ValueContainer:
    return ValueContainer(Line(line_num, source_line),
                          string_constant(string_value))


def symbol_reference(name: str, value_restriction: ValueRestriction = NoRestriction()) -> SymbolReference:
    return SymbolReference(name, ReferenceRestrictionsOnDirectAndIndirect(value_restriction))


def string_symbol_definition(name: str, string_value: str = 'string value') -> SymbolDefinition:
    return SymbolDefinition(name, string_value_container(string_value))


def file_ref_symbol_definition(name: str,
                               file_ref: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                                                relativity=RelOptionType.REL_CWD)
                               ) -> SymbolDefinition:
    return SymbolDefinition(name, file_ref_value_container(file_ref))


def symbol_table_with_single_string_value(name: str, string_value: str = 'string value') -> SymbolTable:
    return symbol_table_from_symbols([string_symbol_definition(name, string_value)])


def symbol_table_with_single_file_ref_value(name: str,
                                            file_ref: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                                                             relativity=RelOptionType.REL_CWD),
                                            line_num: int = 1,
                                            source_line: str = 'value def line') -> SymbolTable:
    return symbol_table_from_symbols([file_ref_symbol(name, file_ref, line_num, source_line)])


def file_ref_value(file_ref: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                                    relativity=RelOptionType.REL_CWD)
                   ) -> FileRefResolver:
    return FileRefConstant(file_ref)


def file_ref_value_container(file_ref: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                                              relativity=RelOptionType.REL_CWD),
                             line_num: int = 1,
                             source_line: str = 'value def line') -> ValueContainer:
    return ValueContainer(Line(line_num, source_line),
                          FileRefConstant(file_ref))


def file_ref_resolver_container(file_ref_resolver: FileRefResolver,
                                line_num: int = 1,
                                source_line: str = 'value def line') -> ValueContainer:
    return ValueContainer(Line(line_num, source_line),
                          file_ref_resolver)


def file_ref_symbol(name: str,
                    file_ref: _file_ref.FileRef = file_ref_test_impl('file-name-rel-cd',
                                                                     relativity=RelOptionType.REL_CWD),
                    line_num: int = 1,
                    source_line: str = 'value def line') -> SymbolDefinition:
    return SymbolDefinition(name, file_ref_value_container(file_ref, line_num, source_line))


def entry(name: str, value: Value = string_constant('string value'),
          line_num: int = 1,
          source_line: str = 'value def line') -> Entry:
    return Entry(name, ValueContainer(Line(line_num, source_line), value))


def symbol_table_from_names(names: iter) -> SymbolTable:
    elements = [(name, string_value_container(name, source_line='source line for {}'.format(name)))
                for name in names]
    return SymbolTable(dict(elements))


def symbol_table_from_symbols(symbols: iter) -> SymbolTable:
    """
    :param symbols: [`ValueDefinition`]
    """
    elements = [(vd.name, vd.value_container)
                for vd in symbols]
    return SymbolTable(dict(elements))


def symbol_table_from_entries(entries: iter) -> SymbolTable:
    """
    :param entries: [`Entry`]
    """
    elements = [(entry.key, entry.value)
                for entry in entries]
    return SymbolTable(dict(elements))


def assert_symbol_usages_is_singleton_list(assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
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
