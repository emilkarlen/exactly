import unittest

from exactly_lib.impls.types.files_matcher import parse_files_matcher as sut
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.impls.types.files_condition.test_resources import arguments_building as fc_args
from exactly_lib_test.impls.types.files_matcher.test_resources.files_condition import FULL_AND_NON_FULL_CASES
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.file_matcher.test_resources.references import is_reference_to_file_matcher


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
                                  fm_args.SymbolReferenceWReferenceSyntax(fm_symbol_name))
        ])
        symbol_references_expectation = asrt.matches_singleton_sequence(
            is_reference_to_file_matcher(fm_symbol_name),
        )

        parser = sut.parsers().full

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
