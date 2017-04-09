import unittest

from exactly_lib.value_definition import value_structure as stc
from exactly_lib.value_definition.concrete_values import FileRefValue, ValueVisitor, StringValue
from exactly_lib_test.test_case_file_structure.test_resources import file_ref as fr_tr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources.value_reference_assertions import equals_value_references


def equals_value(expected: stc.Value) -> asrt.ValueAssertion:
    return _EqualsValue(expected)


def equals_file_ref_value(expected: FileRefValue) -> asrt.ValueAssertion:
    return asrt.is_instance_with(FileRefValue,
                                 asrt.and_([
                                     asrt.sub_component('file_ref',
                                                        FileRefValue.file_ref.fget,
                                                        fr_tr.file_ref_equals(expected.file_ref)),
                                     asrt.sub_component('references',
                                                        lambda x: x.references,
                                                        equals_value_references(expected.references)),
                                 ])
                                 )


def equals_string_value(expected: StringValue) -> asrt.ValueAssertion:
    return asrt.is_instance_with(StringValue,
                                 asrt.and_([
                                     asrt.sub_component('string',
                                                        StringValue.string.fget,
                                                        asrt.equals(expected.string)),
                                     asrt.sub_component('references',
                                                        lambda x: x.references,
                                                        equals_value_references(expected.references)),
                                 ])
                                 )


class _EqualsValueVisitor(ValueVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.put = put
        self.actual = actual

    def _visit_file_ref(self, expected: FileRefValue):
        return equals_file_ref_value(expected).apply(self.put, self.actual, self.message_builder)

    def _visit_string(self, expected: StringValue):
        return equals_string_value(expected).apply(self.put, self.actual, self.message_builder)


class _EqualsValue(asrt.ValueAssertion):
    def __init__(self, expected: stc.Value):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        _EqualsValueVisitor(value, put, message_builder).visit(self.expected)
