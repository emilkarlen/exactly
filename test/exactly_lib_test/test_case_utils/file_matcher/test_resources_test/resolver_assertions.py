import unittest

from exactly_lib.test_case_utils.file_matcher.file_matchers import FileMatcherConstant
from exactly_lib.test_case_utils.file_matcher.resolvers import FileMatcherConstantResolver
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib.test_case_utils.line_matcher.resolvers import LineMatcherConstantResolver
from exactly_lib.util.symbol_table import singleton_symbol_table_2
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherResolverConstantTestImpl
from exactly_lib_test.test_case_utils.file_matcher.test_resources import resolver_assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestResolvedValueEqualsFileMatcher)


class TestResolvedValueEqualsFileMatcher(unittest.TestCase):
    def test_SHOULD_not_equal_WHEN_actual_is_line_matcher(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_FILE_MATCHER_RESOLVER),
                         )),

        ]
        actual = LineMatcherConstant(False)
        expected = FileMatcherConstant(False)

        resolver_of_actual = LineMatcherConstantResolver(actual)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_equals_expected = sut.resolved_value_equals_file_matcher(expected,
                                                                                   symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_equals_expected, resolver_of_actual)

    def test_equals_file_matcher(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(fake()),
                         )),

        ]
        actual_and_expected = FileMatcherConstant(True)
        resolver = FileMatcherConstantResolver(actual_and_expected)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.resolved_value_equals_file_matcher(actual_and_expected,
                                                                            symbols=case.value)
                # ACT & ASSERT #
                assertion_to_check.apply_without_message(self, resolver)

    def test_not_equals_file_matcher(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(fake()),
                         )),

        ]
        actual = FileMatcherConstant(False)
        expected = FileMatcherConstant(True)

        resolver_of_actual = FileMatcherConstantResolver(actual)
        for case in cases:
            with self.subTest(name=case.name):
                assertion_equals_expected = sut.resolved_value_equals_file_matcher(expected,
                                                                                   symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_equals_expected, resolver_of_actual)

    def test_equals_references(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        resolver = fake(references=actual_references)
        assertion_to_check = sut.resolved_value_equals_file_matcher(resolver.resolved_value,
                                                                    expected_references=asrt.matches_sequence([
                                                                        asrt.is_(actual_reference)
                                                                    ]),
                                                                    )
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, resolver)

    def test_not_equals_references(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        resolver = fake(references=actual_references)

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
                assertion_to_check = sut.resolved_value_equals_file_matcher(resolver.resolved_value,
                                                                            expected_references=case.value,
                                                                            )
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, resolver)


def fake(references: list = None) -> FileMatcherResolverConstantTestImpl:
    return FileMatcherResolverConstantTestImpl(FileMatcherConstant(False),
                                               references if references else [])


ARBITRARY_FILE_MATCHER_RESOLVER = FileMatcherResolverConstantTestImpl(FileMatcherConstant(False), [])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
