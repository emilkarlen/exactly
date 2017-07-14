import unittest

from exactly_lib.symbol.string_resolver import string_constant
from exactly_lib.symbol.symbol_usage import SymbolDefinition
from exactly_lib.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.symbol.value_structure import ResolverContainer
from exactly_lib.util.line_source import Line
from exactly_lib_test.symbol.test_resources import value_structure_assertions as sut
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsValueContainer),
        unittest.makeSuite(TestEqualsValueDefinition),
    ])


class TestEqualsValueContainer(unittest.TestCase):
    def test_pass(self):
        value_cases = [
            string_constant('s'),
            FileRefConstant(file_ref_test_impl('file-name')),
        ]
        for value in value_cases:
            for ignore_source_line in [False, True]:
                with self.subTest():
                    # ARRANGE #
                    container = ResolverContainer(Line(1, 'source code'), value)
                    assertion = sut.equals_container(container, ignore_source_line=ignore_source_line)
                    # ACT #
                    assertion.apply_without_message(self, container)

    def test_pass__different_string_but_source_line_check_is_ignored(self):
        # ARRANGE #
        common_value = string_constant('common string value')
        expected = ResolverContainer(Line(4, 'source code 4'), common_value)
        actual = ResolverContainer(Line(5, 'source code 5'), common_value)
        put = test_case_with_failure_exception_set_to_test_exception()
        sut.equals_container(expected, ignore_source_line=True).apply_without_message(put, actual)

    def test_fail__different_source_line_and_source_line_check_is_not_ignored(self):
        # ARRANGE #
        common_value = FileRefConstant(file_ref_test_impl('common file-name'))
        expected = ResolverContainer(Line(1, 'source code 1'), common_value)
        actual = ResolverContainer(Line(2, 'source code 2'), common_value)
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            sut.equals_container(expected, ignore_source_line=False).apply_without_message(put, actual)


class TestEqualsValueDefinition(unittest.TestCase):
    def test_pass(self):
        value_cases = [
            string_constant('s'),
            FileRefConstant(file_ref_test_impl('file-name')),
        ]
        for value in value_cases:
            for ignore_source_line in [False, True]:
                with self.subTest():
                    # ARRANGE #
                    container = ResolverContainer(Line(1, 'source code'), value)
                    symbol = SymbolDefinition('value name', container)
                    # ACT #
                    assertion = sut.equals_symbol(symbol, ignore_source_line=ignore_source_line)
                    assertion.apply_without_message(self, symbol)

    def test_pass__different_string_but_source_line_check_is_ignored(self):
        # ARRANGE #
        common_value = string_constant('common string value')
        expected_container = ResolverContainer(Line(4, 'source code 4'), common_value)
        actual_container = ResolverContainer(Line(5, 'source code 5'), common_value)
        common_name = 'value name'
        expected_symbol = SymbolDefinition(common_name, expected_container)
        actual_symbol = SymbolDefinition(common_name, actual_container)
        # ACT #
        assertion = sut.equals_symbol(expected_symbol, ignore_source_line=True)
        assertion.apply_without_message(self, actual_symbol)

    def test_fail__different_name(self):
        # ARRANGE #
        common_container = ResolverContainer(Line(1, 'source code'),
                                             string_constant('common string value'))
        expected_symbol = SymbolDefinition('expected value name', common_container)
        actual_symbol = SymbolDefinition('actual value name', common_container)
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            # ACT #
            assertion = sut.equals_symbol(expected_symbol)
            assertion.apply_without_message(put, actual_symbol)

    def test_fail__failing_assertion_on_container(self):
        # ARRANGE #
        common_name_source = Line(1, 'source code')
        common_name = 'value name'
        expected_symbol = SymbolDefinition(common_name,
                                           ResolverContainer(common_name_source,
                                                             string_constant('expected string value')))
        actual_symbol = SymbolDefinition(common_name,
                                         ResolverContainer(common_name_source,
                                                           string_constant('actual string value')))
        put = test_case_with_failure_exception_set_to_test_exception()
        with put.assertRaises(TestException):
            # ACT #
            assertion = sut.equals_symbol(expected_symbol)
            assertion.apply_without_message(put, actual_symbol)
