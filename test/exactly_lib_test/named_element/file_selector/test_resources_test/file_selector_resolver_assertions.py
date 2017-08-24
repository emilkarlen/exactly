import unittest

from exactly_lib.named_element.file_selector import FileSelectorConstant
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system_values.file_selector import FileSelector
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib.util.symbol_table import singleton_symbol_table_2
from exactly_lib_test.named_element.file_selector.test_resources import file_selector_resolver_assertions as sut
from exactly_lib_test.named_element.file_selector.test_resources import file_selector_resolvers as resolvers
from exactly_lib_test.named_element.test_resources import named_elem_utils
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestResolvedValueEqualsFileSelector),
    ])


class TestResolvedValueEqualsFileSelector(unittest.TestCase):
    def test_equals(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             named_elem_utils.container(resolvers.constant()),
                         )),

        ]
        name_patterns = frozenset(['first name pattern',
                                   'second name pattern'])
        actual_and_expected = FileSelector(Selectors(name_patterns=name_patterns))
        resolver = FileSelectorConstant(actual_and_expected)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.resolved_value_equals_file_selector(actual_and_expected,
                                                                             environment=case.value)
                # ACT & ASSERT #
                assertion_to_check.apply_without_message(self, resolver)

    def test_not_equals(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             named_elem_utils.container(resolvers.constant()),
                         )),

        ]
        common_name_patterns = frozenset(['first name pattern'])
        actual = FileSelector(Selectors(name_patterns=common_name_patterns))
        expected = FileSelector(Selectors(name_patterns=common_name_patterns,
                                          file_types=frozenset([FileType.REGULAR])))

        resolver_of_actual = FileSelectorConstant(actual)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_equals_expected = sut.resolved_value_equals_file_selector(expected,
                                                                                    environment=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_equals_expected, resolver_of_actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
