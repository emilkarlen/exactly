import unittest

from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.file_selectors.file_matchers import FileMatcherFromSelectors
from exactly_lib.test_case_utils.file_selectors.resolvers import FileSelectorConstant
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib.util.symbol_table import singleton_symbol_table_2
from exactly_lib_test.named_element.symbol.test_resources import symbol_utils
from exactly_lib_test.named_element.test_resources import named_elem_utils
from exactly_lib_test.named_element.test_resources.file_matcher import FileSelectorResolverConstantTestImpl
from exactly_lib_test.test_case_utils.file_selectors.test_resources import resolver_assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestResolvedValueEqualsFileSelector),
    ])


class TestResolvedValueEqualsFileSelector(unittest.TestCase):
    def test_equals_file_selector(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             named_elem_utils.container(fake()),
                         )),

        ]
        name_patterns = frozenset(['first name pattern',
                                   'second name pattern'])
        actual_and_expected = FileMatcherFromSelectors(Selectors(name_patterns=name_patterns))
        resolver = FileSelectorConstant(actual_and_expected)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.resolved_value_equals_file_selector(actual_and_expected,
                                                                             environment=case.value)
                # ACT & ASSERT #
                assertion_to_check.apply_without_message(self, resolver)

    def test_not_equals_file_selector(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             named_elem_utils.container(fake()),
                         )),

        ]
        common_name_patterns = frozenset(['first name pattern'])
        actual = FileMatcherFromSelectors(Selectors(name_patterns=common_name_patterns))
        expected = FileMatcherFromSelectors(Selectors(name_patterns=common_name_patterns,
                                                      file_types=frozenset([FileType.REGULAR])))

        resolver_of_actual = FileSelectorConstant(actual)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_equals_expected = sut.resolved_value_equals_file_selector(expected,
                                                                                    environment=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_equals_expected, resolver_of_actual)

    def test_equals_references(self):
        # ARRANGE #
        actual_reference = symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        resolver = fake(Selectors(),
                        references=actual_references)
        assertion_to_check = sut.resolved_value_equals_file_selector(resolver.resolved_value,
                                                                     expected_references=asrt.matches_sequence([
                                                                         asrt.is_(actual_reference)
                                                                     ]),
                                                                     )
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, resolver)

    def test_not_equals_references(self):
        # ARRANGE #
        actual_reference = symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        resolver = fake(Selectors(),
                        references=actual_references)

        cases = [
            NameAndValue('assert no references',
                         asrt.is_empty_list),
            NameAndValue('assert single invalid reference',
                         asrt.matches_sequence([
                             asrt.not_(asrt.is_(actual_reference))
                         ])),
        ]

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.resolved_value_equals_file_selector(resolver.resolved_value,
                                                                             expected_references=case.value,
                                                                             )
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, resolver)


def fake(selectors: Selectors = Selectors(),
         references: list = None) -> FileSelectorResolverConstantTestImpl:
    return FileSelectorResolverConstantTestImpl(FileMatcherFromSelectors(selectors),
                                                references if references else [])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
