import unittest

from exactly_lib.symbol.data import path_sdvs, list_sdvs
from exactly_lib.symbol.data.string_sdvs import str_constant
from exactly_lib_test.symbol.data.test_resources import any_sdv_assertions as sut
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils as su
from exactly_lib_test.symbol.data.visitor import UnknownDataTypeSdvClass
from exactly_lib_test.tcfs.test_resources.simple_path import path_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEqualsResolver)


class TestEqualsResolver(unittest.TestCase):
    def test_equals__path(self):
        # ARRANGE #
        value = path_sdvs.constant(path_test_impl('file-name'))
        # ACT & ASSERT #
        sut.equals_data_type_sdv(value).apply_without_message(self, value)

    def test_equals__string(self):
        # ARRANGE #
        value = str_constant('string')
        # ACT & ASSERT #
        sut.equals_data_type_sdv(value).apply_without_message(self, value)

    def test_equals__list(self):
        # ARRANGE #
        value = list_sdvs.from_str_constants(['value'])
        # ACT & ASSERT #
        sut.equals_data_type_sdv(value).apply_without_message(self, value)

    def test_not_equals__different_symbol_types(self):
        # ARRANGE #
        expected = path_sdvs.constant(path_test_impl('file-name'))
        actual = str_constant('string value')
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_data_type_sdv(expected), actual)

    def test_not_equals__non_symbol_type(self):
        # ARRANGE #
        expected = path_sdvs.constant(path_test_impl('file-name'))
        actual = UnknownDataTypeSdvClass()
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_data_type_sdv(expected), actual)

    def test_not_equals__path(self):
        # ARRANGE #
        expected = path_sdvs.constant(path_test_impl('expected-file-name'))
        actual = path_sdvs.constant(path_test_impl('actual-file-name'))
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_data_type_sdv(expected), actual)

    def test_not_equals__string(self):
        # ARRANGE #
        expected = str_constant('expected string')
        actual = str_constant('actual string')
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_data_type_sdv(expected), actual)

    def test_not_equals__list(self):
        # ARRANGE #
        expected = list_sdvs.from_str_constants(['value'])
        actual = list_sdvs.from_elements([list_sdvs.symbol_element(su.symbol_reference('symbol_name'))])
        # ACT & ASSERT #
        assert_that_assertion_fails(sut.equals_data_type_sdv(expected), actual)
