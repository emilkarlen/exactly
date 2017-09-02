import unittest

from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath, \
    PathPartAsNothing, \
    PathPart, PathPartVisitor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def equals_path_part_string(file_name: str) -> asrt.ValueAssertion:
    return asrt.is_instance_with(PathPartAsFixedPath,
                                 asrt.sub_component('value',
                                                    lambda x: x.value(),
                                                    asrt.equals(file_name)))


def equals_path_part_nothing() -> asrt.ValueAssertion:
    return asrt.is_instance(PathPartAsNothing)


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
        return equals_path_part_string(expected.value()).apply(self.put, self.actual, self.message_builder)

    def visit_nothing(self, path_suffix: PathPartAsNothing):
        return equals_path_part_nothing().apply(self.put, self.actual, self.message_builder)


class _EqualsPathPart(asrt.ValueAssertion):
    def __init__(self, expected: PathPart):
        self.expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        _EqualsPathPartVisitor(value, put, message_builder).visit(self.expected)
