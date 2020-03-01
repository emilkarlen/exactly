import unittest

from exactly_lib_test.symbol.test_resources.file_matcher import is_file_matcher_reference_to__ref
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args, validation_cases
from exactly_lib_test.test_case_utils.files_condition.test_resources import arguments_building as fc_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources.files_condition import CONTAINS_AND_EQUALS_CASES
from exactly_lib_test.test_case_utils.files_matcher.test_resources.integration_check import CHECKER
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_validation_SHOULD_fail_WHEN_validation_of_files_condition_fails(self):
        # ARRANGE #
        fm_symbol_name = 'the_file_matcher'
        fc_argument = fc_args.FilesCondition([
            fc_args.FileCondition('file-name',
                                  fm_args.SymbolReferenceWSyntax(fm_symbol_name))
        ])
        for case in CONTAINS_AND_EQUALS_CASES:
            fsm = case.arguments_for_fc(fc_argument)
            with self.subTest(case.name):
                # ACT & ASSERT #
                CHECKER.check_multi__w_source_variants(
                    self,
                    fsm.as_arguments,
                    symbol_references=asrt.matches_singleton_sequence(
                        is_file_matcher_reference_to__ref(fm_symbol_name)
                    ),
                    input_=None,
                    execution=validation_cases.failing_validation_cases__multi_exe(fm_symbol_name)
                )