import unittest

from exactly_lib.symbol.data.data_value_resolver import DataValueResolver
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.list_resolver import ListResolver
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.data.visitor import DataValueResolverPseudoVisitor
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib_test.symbol.data.test_resources.concrete_value_assertions import equals_file_ref_resolver, \
    equals_string_resolver
from exactly_lib_test.symbol.data.test_resources.list_assertions import equals_list_resolver
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def equals_resolver(expected: DataValueResolver) -> ValueAssertion:
    return _EqualsResolver(expected)


class _EqualsDataValueResolverVisitor(DataValueResolverPseudoVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.put = put
        self.actual = actual

    def visit_file_ref(self, expected: FileRefResolver):
        return equals_file_ref_resolver(expected).apply(self.put, self.actual, self.message_builder)

    def visit_string(self, expected: StringResolver):
        return equals_string_resolver(expected).apply(self.put, self.actual, self.message_builder)

    def visit_list(self, expected: ListResolver):
        return equals_list_resolver(expected).apply(self.put, self.actual, self.message_builder)


class _EqualsResolver(ValueAssertionBase):
    def __init__(self, expected: DataValueResolver):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, DataValueResolver)
        assert isinstance(value, DataValueResolver)
        put.assertEqual(TypeCategory.DATA,
                        value.type_category,
                        _ELEMENT_TYPE_ERROR_MESSAGE)
        put.assertIs(self.expected.data_value_type,
                     value.data_value_type,
                     'data_value_type')
        put.assertIs(self.expected.value_type,
                     value.value_type,
                     'value_type')
        _EqualsDataValueResolverVisitor(value, put, message_builder).visit(self.expected)


_ELEMENT_TYPE_ERROR_MESSAGE = 'the {} of a {} must be {}'.format(
    TypeCategory,
    DataValueResolver,
    TypeCategory.DATA,
)
