import unittest

from exactly_lib.test_case import file_ref as _file_ref
from exactly_lib.test_case import file_refs
from exactly_lib.test_case.value_definition import FileRefValue, ValueReference, ValueReferenceVisitor, \
    ValueReferenceOfPath, ValueDefinitionVisitor, ValueDefinitionOfPath, ValueDefinition
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTable, Value, Entry
from exactly_lib_test.test_case.test_resources.file_ref_relativity import file_ref_relativity_equals
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def file_ref_value(file_ref: _file_ref.FileRef = file_refs.rel_cwd('file-name-rel-cd'),
                   line_num: int = 1,
                   source_line: str = 'value def line') -> FileRefValue:
    return FileRefValue(Line(line_num, source_line),
                        file_ref)


def entry(name: str, value_: Value = file_ref_value()) -> Entry:
    return Entry(name, value_)


def symbol_table_from_none_or_value(symbol_table_or_none: SymbolTable) -> SymbolTable:
    return SymbolTable() if symbol_table_or_none is None else symbol_table_or_none


def symbol_table_from_names(names: iter) -> SymbolTable:
    elements = [(name, file_ref_value(source_line=name,
                                      file_ref=file_refs.rel_cwd(name)))
                for name in names]
    return SymbolTable(dict(elements))


def symbol_table_from_value_definitions(value_definitions: iter) -> SymbolTable:
    """
    :param value_definitions: [`ValueDefinition`]
    """
    elements = [(vd.name, file_ref_value(source_line=vd.name,
                                         file_ref=file_refs.rel_cwd(vd.name)))
                for vd in value_definitions]
    return SymbolTable(dict(elements))


def symbol_table_from_entries(entries: iter) -> SymbolTable:
    """
    :param entries: [`Entry`]
    """
    elements = [(entry.name, entry.value)
                for entry in entries]
    return SymbolTable(dict(elements))


def assert_value_usages_is_singleton_list_with_value_reference(expected: ValueReference) -> asrt.ValueAssertion:
    return asrt.is_instance_with(list,
                                 asrt.And([
                                     asrt.len_equals(1),
                                     asrt.sub_component('singleton element',
                                                        lambda l: l[0],
                                                        equals_value_reference(expected))
                                 ]))


def assert_value_usages_is_singleton_list(assertion: asrt.ValueAssertion) -> asrt.ValueAssertion:
    return asrt.is_instance_with(list,
                                 asrt.And([
                                     asrt.len_equals(1),
                                     asrt.sub_component('singleton element',
                                                        lambda l: l[0],
                                                        assertion)
                                 ]))


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


class _EqualsFileRefValue(asrt.ValueAssertion):
    # TODO Probably needs access to PathResolvingEnvironmentPreOrPostSds
    # or at least SymbolTable
    # to be able to check all properties of a FileRef
    def __init__(self, expected: FileRefValue):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, FileRefValue)


def equals_file_ref_value(expected: FileRefValue) -> asrt.ValueAssertion:
    return _EqualsFileRefValue(expected)


class _EqualsValueDefinition(ValueDefinitionVisitor):
    # TODO Probably needs access to PathResolvingEnvironmentPreOrPostSds
    # or at least SymbolTable
    # to be able to check all properties of a FileRef
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.put = put
        self.actual = actual

    def _visit_path(self, expected: ValueDefinitionOfPath):
        self._common(expected)

    def _common(self, expected: ValueDefinition):
        self.put.assertIsInstance(self.actual, type(expected),
                                  self.message_builder.apply('object class'))
        assert isinstance(self.actual, ValueDefinition)
        self.put.assertEqual(self.actual.name,
                             expected.name,
                             self.message_builder.apply('name'))


class _EqualsValueDefinitionAssertion(asrt.ValueAssertion):
    def __init__(self, expected: ValueDefinition):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value, message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        _EqualsValueDefinition(value, put, message_builder).visit(self.expected)


class _EqualsValueReference(ValueReferenceVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.put = put
        self.actual = actual

    def _visit_path(self, expected: ValueReferenceOfPath):
        self._common(expected)
        file_ref_relativity_equals(expected.valid_relativities).apply(self.put,
                                                                      self.actual.valid_relativities,
                                                                      self.message_builder)

    def _common(self, expected: ValueReference):
        self.put.assertIsInstance(self.actual, type(expected),
                                  self.message_builder.apply('object class'))
        assert isinstance(self.actual, ValueReference)
        self.put.assertEqual(self.actual.name,
                             expected.name,
                             self.message_builder.apply('name'))


class _EqualsValueReferenceAssertion(asrt.ValueAssertion):
    def __init__(self, expected: ValueReference):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value, message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        _EqualsValueReference(value, put, message_builder).visit(self.expected)


def equals_value_definition(expected: ValueDefinition) -> asrt.ValueAssertion:
    return _EqualsValueDefinitionAssertion(expected)


def equals_value_reference(expected: ValueReference) -> asrt.ValueAssertion:
    return _EqualsValueReferenceAssertion(expected)
