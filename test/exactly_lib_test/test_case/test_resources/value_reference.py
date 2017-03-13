import unittest

from exactly_lib.test_case.value_definition import ValueReference, ValueReferenceVisitor, \
    ValueReferenceOfPath
from exactly_lib_test.test_case.test_resources.file_ref_relativity import path_relativity_variants_equals
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_value_reference(expected: ValueReference) -> asrt.ValueAssertion:
    return _EqualsValueReferenceAssertion(expected)


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
        path_relativity_variants_equals(expected.valid_relativities).apply(self.put,
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
