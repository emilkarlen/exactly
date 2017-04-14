import unittest

from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.concrete_values import StringResolver
from exactly_lib.value_definition.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.value_definition.value_resolvers.string_resolvers import StringConstant
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.value_definition.test_resources import concrete_value_assertions_2 as sut


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEqualsValue)


class TestEqualsValue(unittest.TestCase):
    def test_equals__file_ref(self):
        # ARRANGE #
        value = FileRefConstant(file_ref_test_impl('file-name'))
        # ACT & ASSERT #
        sut.value_equals3(value).apply_without_message(self, value)

    def test_equals__string(self):
        # ARRANGE #
        value = StringConstant('string')
        # ACT & ASSERT #
        sut.value_equals3(value).apply_without_message(self, value)

    def test_not_equals__different_types(self):
        # ARRANGE #
        expected = FileRefConstant(file_ref_test_impl('file-name'))
        actual = StringConstant('string value')
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.value_equals3(expected).apply_without_message(put, actual)

    def test_not_equals__file_ref(self):
        # ARRANGE #
        expected = FileRefConstant(file_ref_test_impl('expected-file-name'))
        actual = FileRefConstant(file_ref_test_impl('actual-file-name'))
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.value_equals3(expected).apply_without_message(put, actual)

    def test_not_equals__string(self):
        # ARRANGE #
        expected = StringConstant('expected string')
        actual = StringConstant('actual string')
        put = test_case_with_failure_exception_set_to_test_exception()
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.value_equals3(expected).apply_without_message(put, actual)


class _StringResolverTestImpl(StringResolver):
    def __init__(self,
                 value: str,
                 explicit_references: list):
        self.value = value
        self.explicit_references = explicit_references

    def resolve(self, symbols: SymbolTable) -> str:
        return self.value

    @property
    def references(self) -> list:
        return self.explicit_references
