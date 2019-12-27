import unittest

from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.data import string_sdvs
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.symbol.symbol_usage import SymbolDefinition
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as sut
from exactly_lib_test.symbol.test_resources.symbol_utils import single_line_sequence
from exactly_lib_test.test_case_file_structure.test_resources.simple_path import path_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsValueContainer),
        unittest.makeSuite(TestEqualsValueDefinition),
    ])


class TestEqualsValueContainer(unittest.TestCase):
    def test_pass(self):
        value_cases = [
            string_sdvs.str_constant('s'),
            path_sdvs.constant(path_test_impl('file-name')),
        ]
        for value in value_cases:
            for ignore_source_line in [False, True]:
                with self.subTest():
                    # ARRANGE #
                    container = SymbolContainer(value, single_line_sequence(1, 'source code'))
                    assertion = sut.equals_container(container, ignore_source_line=ignore_source_line)
                    # ACT #
                    assertion.apply_without_message(self, container)

    def test_pass__different_string_but_source_line_check_is_ignored(self):
        # ARRANGE #
        common_value = string_sdvs.str_constant('common string value')
        expected = SymbolContainer(common_value, single_line_sequence(4, 'source code 4'))
        actual = SymbolContainer(common_value, single_line_sequence(5, 'source code 5'))
        assertion = sut.equals_container(expected, ignore_source_line=True)
        assertion.apply_without_message(self, actual)

    def test_fail__different_source_line_and_source_line_check_is_not_ignored(self):
        # ARRANGE #
        common_value = path_sdvs.constant(path_test_impl('common file-name'))
        expected = SymbolContainer(common_value, single_line_sequence(1, 'source code 1'))
        actual = SymbolContainer(common_value, single_line_sequence(2, 'source code 2'))
        assertion = sut.equals_container(expected, ignore_source_line=False)
        assert_that_assertion_fails(assertion, actual)


class TestEqualsValueDefinition(unittest.TestCase):
    def test_pass(self):
        value_cases = [
            string_sdvs.str_constant('s'),
            path_sdvs.constant(path_test_impl('file-name')),
        ]
        for value in value_cases:
            for ignore_source_line in [False, True]:
                with self.subTest():
                    # ARRANGE #
                    container = SymbolContainer(value, single_line_sequence(1, 'source code'))
                    symbol = SymbolDefinition('value name', container)
                    # ACT #
                    assertion = sut.equals_symbol(symbol, ignore_source_line=ignore_source_line)
                    assertion.apply_without_message(self, symbol)

    def test_pass__different_string_but_source_line_check_is_ignored(self):
        # ARRANGE #
        common_value_sdv = string_sdvs.str_constant('common string value')
        expected_container = SymbolContainer(common_value_sdv, single_line_sequence(4, 'source code 4'))
        actual_container = SymbolContainer(common_value_sdv, single_line_sequence(5, 'source code 5'))
        common_name = 'value name'
        expected_symbol = SymbolDefinition(common_name, expected_container)
        actual_symbol = SymbolDefinition(common_name, actual_container)
        # ACT #
        assertion = sut.equals_symbol(expected_symbol, ignore_source_line=True)
        assertion.apply_without_message(self, actual_symbol)

    def test_fail__different_name(self):
        # ARRANGE #
        common_container = SymbolContainer(string_sdvs.str_constant('common string value'),
                                           single_line_sequence(1, 'source code'))
        expected_symbol = SymbolDefinition('expected value name', common_container)
        actual_symbol = SymbolDefinition('actual value name', common_container)
        assertion = sut.equals_symbol(expected_symbol)
        assert_that_assertion_fails(assertion, actual_symbol)

    def test_fail__failing_assertion_on_container(self):
        # ARRANGE #
        common_name_source = single_line_sequence(1, 'source code')
        common_name = 'value name'
        expected_symbol = SymbolDefinition(common_name,
                                           SymbolContainer(string_sdvs.str_constant('expected string value'),
                                                           common_name_source))
        actual_symbol = SymbolDefinition(common_name,
                                         SymbolContainer(string_sdvs.str_constant('actual string value'),
                                                         common_name_source))
        assertion = sut.equals_symbol(expected_symbol)
        assert_that_assertion_fails(assertion, actual_symbol)
