import unittest

from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.impls.types.files_condition.test_resources import arguments_building as fc_args
from exactly_lib_test.impls.types.files_matcher.test_resources.files_condition import FULL_AND_NON_FULL_CASES
from exactly_lib_test.impls.types.files_matcher.test_resources.integration_check import CHECKER__PARSE_FULL
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources import validation_cases
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.references import is_reference_to_file_matcher


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_validation_SHOULD_fail_WHEN_validation_of_files_condition_fails(self):
        # ARRANGE #
        fm_symbol_name = 'the_file_matcher'
        fc_argument = fc_args.FilesCondition([
            fc_args.FileCondition('file-name',
                                  fm_args.SymbolReferenceWReferenceSyntax(fm_symbol_name))
        ])
        for case in FULL_AND_NON_FULL_CASES:
            fsm = case.arguments_for_fc(fc_argument)
            with self.subTest(case.name):
                # ACT & ASSERT #
                CHECKER__PARSE_FULL.check_multi__w_source_variants(
                    self,
                    fsm.as_arguments,
                    symbol_references=asrt.matches_singleton_sequence(
                        is_reference_to_file_matcher(fm_symbol_name)
                    ),
                    input_=None,
                    execution=validation_cases.failing_validation_cases__multi_exe(fm_symbol_name)
                )
