import unittest

from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath, \
    PathPartAsStringSymbolReference, \
    PathPart, PathPartVisitor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources.concrete_restriction_assertion import \
    is_string_value_restriction
from exactly_lib_test.value_definition.test_resources.value_reference_assertions import equals_value_reference


def equals_path_part_string(file_name: str) -> asrt.ValueAssertion:
    return asrt.is_instance_with(PathPartAsFixedPath,
                                 asrt.sub_component('file_name',
                                                    PathPartAsFixedPath.file_name.fget,
                                                    asrt.equals(file_name)))


def equals_path_part_with_symbol_reference(expected: PathPartAsStringSymbolReference) -> asrt.ValueAssertion:
    return asrt.is_instance_with(
        PathPartAsStringSymbolReference,
        asrt.and_([
            asrt.sub_component('symbol_name',
                               PathPartAsStringSymbolReference.symbol_name.fget,
                               asrt.equals(expected.symbol_name)),
            asrt.sub_component('value_references',
                               PathPartAsStringSymbolReference.value_references.fget,
                               asrt.matches_sequence([equals_value_reference(vr.name,
                                                                             is_string_value_restriction)
                                                      for vr in expected.value_references])),
        ])
    )


def equals_path_part(expected: PathPart) -> asrt.ValueAssertion:
    return _EqualsPathPart(expected)


class _EqualsPathPartVisitor(PathPartVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.put = put
        self.actual = actual

    def visit_fixed_path(self, expected: PathPartAsFixedPath):
        return equals_path_part_string(expected.file_name).apply(self.put, self.actual, self.message_builder)

    def visit_symbol_reference(self, expected: PathPartAsStringSymbolReference):
        return equals_path_part_with_symbol_reference(expected).apply(self.put, self.actual, self.message_builder)


class _EqualsPathPart(asrt.ValueAssertion):
    def __init__(self, expected: PathPart):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        _EqualsPathPartVisitor(value, put, message_builder).visit(self.expected)
