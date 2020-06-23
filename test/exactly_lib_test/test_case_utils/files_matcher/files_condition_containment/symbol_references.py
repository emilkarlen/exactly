import unittest

from exactly_lib.test_case_utils.files_matcher import parse_files_matcher as sut
from exactly_lib_test.symbol.test_resources.file_matcher import is_file_matcher_reference_to__ref
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_case_utils.files_condition.test_resources import arguments_building as fc_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources.files_condition import FULL_AND_NON_FULL_CASES
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        Test(),
    ])


class Test(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        fm_symbol_name = 'file_matcher_symbol'
        fc_argument = fc_args.FilesCondition([
            fc_args.FileCondition('file-name',
                                  fm_args.SymbolReferenceWSyntax(fm_symbol_name))
        ])
        symbol_references_expectation = asrt.matches_singleton_sequence(
            is_file_matcher_reference_to__ref(fm_symbol_name),
        )

        parser = sut.files_matcher_parser()

        for case in FULL_AND_NON_FULL_CASES:
            fsm = case.arguments_for_fc(fc_argument)
            with self.subTest(case.name):
                # ACT #
                sdv = parser.parse(fsm.as_remaining_source)
                # ASSERT #
                symbol_references_expectation.apply_without_message(
                    self,
                    sdv.references,
                )
