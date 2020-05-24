import unittest

from exactly_lib.symbol.data.data_type_sdv import DataTypeSdv
from exactly_lib.symbol.data.list_sdv import ListSdv
from exactly_lib.symbol.data.path_sdv import PathSdv
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.data.visitor import DataTypeSdvPseudoVisitor
from exactly_lib.type_system.value_type import TypeCategory
from exactly_lib_test.symbol.data.test_resources.concrete_value_assertions import equals_path_sdv, \
    equals_string_sdv
from exactly_lib_test.symbol.data.test_resources.list_assertions import equals_list_sdv
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, ValueAssertionBase


def equals_data_type_sdv(expected: DataTypeSdv) -> ValueAssertion[DataTypeSdv]:
    return _EqualsSdv(expected)


class _EqualsDataTypeSdvVisitor(DataTypeSdvPseudoVisitor):
    def __init__(self,
                 actual,
                 put: unittest.TestCase,
                 message_builder: asrt.MessageBuilder):
        self.message_builder = message_builder
        self.put = put
        self.actual = actual

    def visit_path(self, expected: PathSdv):
        return equals_path_sdv(expected).apply(self.put, self.actual, self.message_builder)

    def visit_string(self, expected: StringSdv):
        return equals_string_sdv(expected).apply(self.put, self.actual, self.message_builder)

    def visit_list(self, expected: ListSdv):
        return equals_list_sdv(expected).apply(self.put, self.actual, self.message_builder)


class _EqualsSdv(ValueAssertionBase[DataTypeSdv]):
    def __init__(self, expected: DataTypeSdv):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value: DataTypeSdv,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, DataTypeSdv)
        assert isinstance(value, DataTypeSdv)
        _EqualsDataTypeSdvVisitor(value, put, message_builder).visit(self.expected)


_ELEMENT_TYPE_ERROR_MESSAGE = 'the {} of a {} must be {}'.format(
    TypeCategory,
    DataTypeSdv,
    TypeCategory.DATA,
)
