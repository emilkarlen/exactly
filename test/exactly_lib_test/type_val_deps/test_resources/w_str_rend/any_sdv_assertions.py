import unittest

from exactly_lib.definitions.type_system import TypeCategory
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_type import DataTypeSdv
from exactly_lib.type_val_deps.dep_variants.sdv.w_str_rend.sdv_visitor import WStrRenderingTypeSdvPseudoVisitor
from exactly_lib.type_val_deps.types.list_.list_sdv import ListSdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, AssertionBase
from exactly_lib_test.type_val_deps.types.list_.test_resources.list_assertions import equals_list_sdv
from exactly_lib_test.type_val_deps.types.path.test_resources.sdv_assertions import equals_path_sdv
from exactly_lib_test.type_val_deps.types.string_.test_resources.sdv_assertions import equals_string_sdv


def equals_data_type_sdv(expected: DataTypeSdv) -> Assertion[DataTypeSdv]:
    return _EqualsSdv(expected)


class _EqualsWStrRenderingTypeSdvVisitor(WStrRenderingTypeSdvPseudoVisitor):
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


class _EqualsSdv(AssertionBase[DataTypeSdv]):
    def __init__(self, expected: DataTypeSdv):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value: DataTypeSdv,
               message_builder: asrt.MessageBuilder):
        put.assertIsInstance(value, DataTypeSdv)
        assert isinstance(value, DataTypeSdv)
        _EqualsWStrRenderingTypeSdvVisitor(value, put, message_builder).visit(self.expected)


_ELEMENT_TYPE_ERROR_MESSAGE = 'the {} of a {} must be {}'.format(
    TypeCategory,
    DataTypeSdv,
    TypeCategory.DATA,
)
