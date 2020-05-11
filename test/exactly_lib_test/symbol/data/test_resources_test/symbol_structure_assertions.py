import unittest

from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.sdv_structure import SymbolDefinition
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib_test.section_document.test_resources.source_location import single_line_sequence
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as sut
from exactly_lib_test.symbol.data.test_resources.path import PathSymbolValueContext
from exactly_lib_test.symbol.test_resources.string import StringSymbolValueContext, StringSymbolContext
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
            StringSymbolValueContext.of_constant('s'),
            PathSymbolValueContext.of_rel_arbitrary_and_suffix('file-name'),
        ]
        for value in value_cases:
            for ignore_source_line in [False, True]:
                with self.subTest():
                    # ARRANGE #
                    assertion = sut.equals_container(value.container, ignore_source_line=ignore_source_line)
                    # ACT #
                    assertion.apply_without_message(self, value.container)

    def test_pass__different_string_but_source_line_check_is_ignored(self):
        # ARRANGE #
        common_value = 'common string value'
        expected = StringSymbolValueContext.of_constant(common_value,
                                                        single_line_sequence(4, 'source code 4')).container
        actual = StringSymbolValueContext.of_constant(common_value,
                                                      single_line_sequence(5, 'source code 5')).container
        assertion = sut.equals_container(expected, ignore_source_line=True)
        assertion.apply_without_message(self, actual)

    def test_fail__different_source_line_and_source_line_check_is_not_ignored(self):
        # ARRANGE #
        common_value = path_sdvs.constant(path_test_impl('common file-name'))
        expected = PathSymbolValueContext.of_sdv(common_value,
                                                 definition_source=single_line_sequence(1, 'source code 1')).container
        actual = PathSymbolValueContext.of_sdv(common_value,
                                               definition_source=single_line_sequence(2, 'source code 2')).container
        assertion = sut.equals_container(expected, ignore_source_line=False)
        assert_that_assertion_fails(assertion, actual)


class TestEqualsValueDefinition(unittest.TestCase):
    def test_pass(self):
        value_cases = [
            StringSymbolValueContext.of_constant('s'),
            PathSymbolValueContext.of_rel_opt_and_suffix(RelOptionType.REL_RESULT, 'file-name'),
        ]
        for value in value_cases:
            for ignore_source_line in [False, True]:
                with self.subTest():
                    # ARRANGE #
                    definition = SymbolDefinition('value name', value.container)
                    # ACT #
                    assertion = sut.equals_symbol_definition(definition, ignore_source_line=ignore_source_line)
                    assertion.apply_without_message(self, definition)

    def test_pass__different_source_but_source_check_is_ignored(self):
        # ARRANGE #
        common_value_sdv = 'common string value'
        expected = StringSymbolValueContext.of_constant(common_value_sdv,
                                                        single_line_sequence(4, 'source code 4'))
        actual = StringSymbolValueContext.of_constant(common_value_sdv,
                                                      single_line_sequence(5, 'source code 5'))
        common_name = 'value name'
        expected_symbol = SymbolDefinition(common_name, expected.container)
        actual_symbol = SymbolDefinition(common_name, actual.container)
        # ACT #
        assertion = sut.equals_symbol_definition(expected_symbol, ignore_source_line=True)
        assertion.apply_without_message(self, actual_symbol)

    def test_fail__different_name(self):
        # ARRANGE #
        common_value = StringSymbolValueContext.of_constant('common string value',
                                                            single_line_sequence(1, 'source code'))
        expected_symbol = StringSymbolContext('expected value name', common_value).definition
        actual_symbol = StringSymbolContext('actual value name', common_value).definition
        assertion = sut.equals_symbol_definition(expected_symbol)
        assert_that_assertion_fails(assertion, actual_symbol)

    def test_fail__failing_assertion_on_container(self):
        # ARRANGE #
        common_source = single_line_sequence(1, 'source code')
        common_name = 'value name'
        expected_symbol = StringSymbolContext(common_name,
                                              StringSymbolValueContext.of_constant(
                                                  'expected string value',
                                                  common_source)).definition
        actual_symbol = StringSymbolContext(common_name,
                                            StringSymbolValueContext.of_constant(
                                                'actual string value',
                                                common_source)).definition
        assertion = sut.equals_symbol_definition(expected_symbol)
        assert_that_assertion_fails(assertion, actual_symbol)
