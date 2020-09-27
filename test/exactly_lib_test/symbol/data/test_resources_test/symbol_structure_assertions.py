import unittest

from exactly_lib.symbol.data import path_sdvs
from exactly_lib_test.section_document.test_resources.source_location import single_line_sequence
from exactly_lib_test.symbol.data.test_resources import symbol_structure_assertions as sut
from exactly_lib_test.symbol.data.test_resources.path import PathSymbolValueContext
from exactly_lib_test.symbol.test_resources.string import StringSymbolValueContext
from exactly_lib_test.tcfs.test_resources.simple_path import path_test_impl
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsSymbolContainer),
    ])


class TestEqualsSymbolContainer(unittest.TestCase):
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
