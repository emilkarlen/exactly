import unittest

from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.test_case_utils.file_matcher.sdvs import file_matcher_constant_sdv
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv
from exactly_lib.util.symbol_table import singleton_symbol_table_2
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils, string_sdvs
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.file_matcher import file_matcher_sdv_constant_test_impl
from exactly_lib_test.test_case_utils.file_matcher.test_resources import sdv_assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestResolvedValueMatchesFileMatcher)


class TestResolvedValueMatchesFileMatcher(unittest.TestCase):
    def test_SHOULD_not_match_WHEN_value_does_not_match(self):
        # ARRANGE #
        cases = [
            NameAndValue('without symbol table',
                         None),
            NameAndValue('with symbol table',
                         singleton_symbol_table_2(
                             'the symbol name',
                             symbol_utils.container(ARBITRARY_FILE_MATCHER_SDV),
                         )),

        ]
        sdv_of_actual = string_sdvs.arbitrary_sdv()
        for case in cases:
            with self.subTest(name=case.name):
                assertion_equals_expected = sut.resolved_ddv_matches_file_matcher(asrt.fail('unconditional'),
                                                                                  symbols=case.value)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_equals_expected, sdv_of_actual)

    def test_matches_file_matcher(self):
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
        sdv = file_matcher_constant_sdv(constant.MatcherWithConstantResult(True))
        for case in cases:
            with self.subTest(name=case.name):
                assertion_to_check = sut.resolved_ddv_matches_file_matcher(asrt.is_instance(MatcherDdv),
                                                                           symbols=case.value)
                # ACT & ASSERT #
                assertion_to_check.apply_without_message(self, sdv)

    def test_equals_references(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        sdv = fake(references=actual_references)
        assertion_to_check = sut.resolved_ddv_matches_file_matcher(asrt.anything_goes(),
                                                                   references=asrt.matches_sequence([
                                                                       asrt.is_(actual_reference)
                                                                   ]),
                                                                   )
        # ACT & ASSERT #
        assertion_to_check.apply_without_message(self, sdv)

    def test_not_equals_references(self):
        # ARRANGE #
        actual_reference = data_symbol_utils.symbol_reference('referenced element')
        actual_references = [actual_reference]
        sdv = fake(references=actual_references)

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
                assertion_to_check = sut.resolved_ddv_matches_file_matcher(asrt.anything_goes(),
                                                                           references=case.value,
                                                                           )
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check, sdv)


def fake(references: list = None) -> FileMatcherSdv:
    return file_matcher_sdv_constant_test_impl(constant.MatcherWithConstantResult(False),
                                               references if references else [])


ARBITRARY_FILE_MATCHER_SDV = file_matcher_sdv_constant_test_impl(constant.MatcherWithConstantResult(False), [])

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())