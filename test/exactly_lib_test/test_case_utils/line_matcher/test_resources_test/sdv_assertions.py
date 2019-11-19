import unittest

from exactly_lib.test_case_utils.file_matcher.sdvs import FileMatcherConstantSdv
from exactly_lib.test_case_utils.line_matcher.line_matchers import LineMatcherConstant
from exactly_lib.test_case_utils.line_matcher.sdvs import LineMatcherSdvConstant
from exactly_lib.util.symbol_table import singleton_symbol_table_2
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.line_matcher import LineMatcherSdvConstantTestImpl
from exactly_lib_test.test_case_utils.line_matcher.test_resources import sdv_assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources.values import FileMatcherTestImpl


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestResolvedValueMatchesLineMatcher)


class TestResolvedValueMatchesLineMatcher(unittest.TestCase):
    def test_equals_line_matcher(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_LINE_MATCHER_SDV),
                         )),

        ]
        sdv = LineMatcherSdvConstant(LineMatcherConstant(False))
        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.resolved_ddv_matches_line_matcher(asrt.anything_goes(),
                                                                           symbols=case.value)
                # ACT & ASSERT #
                assertion_to_check.apply_without_message(self, sdv)

    def test_SHOULD_not_equal_line_matcher_WHEN_assertion_on_value_fails(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_LINE_MATCHER_SDV),
                         )),

        ]
        sdv_of_actual = FileMatcherConstantSdv(FileMatcherTestImpl())
        for case in cases:
            with self.subTest(name=case.name):
                assertion_equals_expected = sut.resolved_ddv_matches_line_matcher(
                    asrt.fail('unconditional failure of value assertion'),
                    symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_equals_expected, sdv_of_actual)

    def test_equals_references(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_sdv = LineMatcherSdvConstantTestImpl(
            LineMatcherConstant(False),
            references=actual_references)
        assertion_to_check = sut.resolved_ddv_matches_line_matcher(asrt.anything_goes(),
                                                                   references=asrt.matches_sequence([
                                                                         asrt.is_(actual_reference)
                                                                     ]),
                                                                   )
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, actual_sdv)

    def test_not_equals_references(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        actual_sdv = LineMatcherSdvConstantTestImpl(
            LineMatcherConstant(False),
            references=actual_references)

        cases = [
            NameAndValue('assert no references',
                         asrt.is_empty_sequence),
            NameAndValue('assert single invalid reference',
                         asrt.matches_sequence([
                             asrt.not_(asrt.is_(actual_reference))
                         ])),
        ]

        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.resolved_ddv_matches_line_matcher(asrt.anything_goes(),
                                                                           references=case.value,
                                                                           )
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, actual_sdv)


ARBITRARY_LINE_MATCHER_SDV = LineMatcherSdvConstantTestImpl(LineMatcherConstant(False), [])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
