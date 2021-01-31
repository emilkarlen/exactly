import unittest

from exactly_lib.type_val_deps.types.path.path_part_ddvs import PathPartDdvAsFixedPath, \
    PathPartDdvAsNothing, \
    PathPartDdv, PathPartDdvVisitor
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase


def equals_path_part_string(file_name: str) -> Assertion:
    return asrt.is_instance_with(PathPartDdvAsFixedPath,
                                 asrt.sub_component('value',
                                                    lambda x: x.value(),
                                                    asrt.equals(file_name)))


def equals_path_part_nothing() -> Assertion:
    return asrt.is_instance(PathPartDdvAsNothing)


def equals_path_part(expected: PathPartDdv) -> Assertion:
    return _EqualsPathPart(expected)


class _EqualsPathPartDdvVisitor(PathPartDdvVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.put = put
        self.actual = actual

    def visit_fixed_path(self, expected: PathPartDdvAsFixedPath):
        return equals_path_part_string(expected.value()).apply(self.put, self.actual, self.message_builder)

    def visit_nothing(self, path_suffix: PathPartDdvAsNothing):
        return equals_path_part_nothing().apply(self.put, self.actual, self.message_builder)


class _EqualsPathPart(AssertionBase):
    def __init__(self, expected: PathPartDdv):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value,
               message_builder: asrt.MessageBuilder):
        _EqualsPathPartDdvVisitor(value, put, message_builder).visit(self.expected)
