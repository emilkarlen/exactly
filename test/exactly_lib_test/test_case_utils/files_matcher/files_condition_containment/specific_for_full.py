import unittest

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.files_matcher.impl.matches.common import \
    MATCHES_FULL__STRUCTURE_NAME
from exactly_lib_test.symbol.test_resources.file_matcher import is_reference_to_file_matcher__ref
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_case_utils.files_condition.test_resources import arguments_building as fc_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources.files_condition import \
    NON_MATCHING_EXECUTION_EXPECTATION, exe_w_added_header_matcher, prim_and_exe_w_header_matcher, \
    is_regular_file_matcher, is_dir_file_matcher
from exactly_lib_test.test_case_utils.files_matcher.test_resources.model import model_constructor__non_recursive
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import Arrangement, \
    Expectation, ParseExpectation, PrimAndExeExpectation
from exactly_lib_test.test_case_utils.test_resources.dir_arg_helper import DirArgumentHelper
from exactly_lib_test.test_resources.files.file_structure import empty_file, empty_dir
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestNoMatchWhenModelContainsMoreFilesThanFc)


class TestNoMatchWhenModelContainsMoreFilesThanFc(unittest.TestCase):
    def test_empty_fc(self):
        # ARRANGE #
        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'dir-w-single-file')
        # ACT & ASSERT #
        integration_check.CHECKER.check__w_source_variants(
            self,
            args.matches_full(fc_args.FilesConditionArg.empty()).as_arguments,
            model_constructor__non_recursive(checked_dir.path_sdv),
            Arrangement(
                tcds=checked_dir.tcds_arrangement_dir_with_contents([
                    empty_file('a-file')
                ])
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.is_empty_sequence
                ),
                exe_w_added_header_matcher(MATCHES_FULL__STRUCTURE_NAME,
                                           NON_MATCHING_EXECUTION_EXPECTATION),
            ),
        )

    def test_1_file_in_fc_wo_matcher(self):
        # ARRANGE #
        name_of_file_in_fc = 'file-in-files-condition'
        name_of_file_not_in_fc_1 = 'file-not-in-files-condition-1'
        name_of_file_not_in_fc_2 = 'file-not-in-files-condition-2'

        arguments = args.matches_full(
            fc_args.FilesCondition([fc_args.FileCondition(name_of_file_in_fc)])
        )

        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'dir-w-more-than-one-file')

        execution_cases = [
            NExArr(
                '2 files: one file name matches',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        empty_file(name_of_file_in_fc),
                        empty_file(name_of_file_not_in_fc_1),
                    ])
                )
            ),
            NExArr(
                '2 files: no file name matches',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        empty_file(name_of_file_not_in_fc_1),
                        empty_file(name_of_file_not_in_fc_2),
                    ])
                )
            ),
            NExArr(
                '3 files: one file name matches',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        empty_file(name_of_file_in_fc),
                        empty_file(name_of_file_not_in_fc_1),
                        empty_file(name_of_file_not_in_fc_2),
                    ])
                )
            )
        ]
        # ACT & ASSERT #
        integration_check.CHECKER.check_multi__w_source_variants(
            self,
            arguments.as_arguments,
            symbol_references=asrt.is_empty_sequence,
            input_=model_constructor__non_recursive(checked_dir.path_sdv),
            execution=execution_cases
        )

    def test_1_file_in_fc_w_matcher(self):
        # ARRANGE #
        name_of_file_in_fc = 'file-in-files-condition'
        name_of_file_not_in_fc_1 = 'file-not-in-files-condition-1'
        name_of_file_not_in_fc_2 = 'file-not-in-files-condition-2'

        file_matcher_name = 'the_file_matcher'
        arguments = args.matches_full(
            fc_args.FilesCondition([
                fc_args.FileCondition(name_of_file_in_fc,
                                      fm_args.SymbolReferenceWSyntax(file_matcher_name)),
            ])
        )

        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'dir-w-more-than-one-file')

        execution_cases = [
            NExArr(
                '2 files: one file name matches, and matcher matches',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    symbols=is_regular_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        empty_file(name_of_file_in_fc),
                        empty_file(name_of_file_not_in_fc_1),
                    ])
                )
            ),
            NExArr(
                '2 files: one file name matches, and matcher does not match',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    symbols=is_dir_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        empty_file(name_of_file_in_fc),
                        empty_file(name_of_file_not_in_fc_1),
                    ])
                )
            ),
            NExArr(
                '3 files: one file name matches, and matcher matches',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    symbols=is_dir_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        empty_dir(name_of_file_in_fc),
                        empty_file(name_of_file_not_in_fc_1),
                        empty_file(name_of_file_not_in_fc_2),
                    ])
                )
            )
        ]
        # ACT & ASSERT #
        integration_check.CHECKER.check_multi__w_source_variants(
            self,
            arguments.as_arguments,
            symbol_references=asrt.matches_sequence([
                is_reference_to_file_matcher__ref(file_matcher_name),
            ]),
            input_=model_constructor__non_recursive(checked_dir.path_sdv),
            execution=execution_cases
        )

    def test_2_files_in_fc(self):
        # ARRANGE #
        name_of_file_in_fc__1 = 'file-in-files-condition-1'
        name_of_file_in_fc__2 = 'file-in-files-condition-2'
        name_of_file_not_in_fc__1 = 'file-not-in-files-condition-1'
        name_of_file_not_in_fc__2 = 'file-not-in-files-condition-2'

        file_matcher_name = 'the_file_matcher'
        arguments = args.matches_full(
            fc_args.FilesCondition([
                fc_args.FileCondition(name_of_file_in_fc__1,
                                      fm_args.SymbolReferenceWSyntax(file_matcher_name)),
                fc_args.FileCondition(name_of_file_in_fc__2),
            ])
        )

        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'dir-w-more-than-two-files')

        execution_cases = [
            NExArr(
                '3 files: one file name matches, and matcher matches',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    symbols=is_regular_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        empty_file(name_of_file_in_fc__1),
                        empty_file(name_of_file_not_in_fc__1),
                        empty_file(name_of_file_not_in_fc__2),
                    ])
                )
            ),
            NExArr(
                '3 files: both file names matches, and matcher matches',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    symbols=is_regular_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        empty_file(name_of_file_in_fc__1),
                        empty_file(name_of_file_in_fc__2),
                        empty_file(name_of_file_not_in_fc__1),
                    ])
                )
            ),
            NExArr(
                '3 files: both file name matches, but matcher does not match',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    symbols=is_dir_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        empty_file(name_of_file_in_fc__1),
                        empty_file(name_of_file_in_fc__2),
                        empty_file(name_of_file_not_in_fc__1),
                    ])
                )
            ),
            NExArr(
                '4 files: both file name matches, and matcher matches',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    symbols=is_regular_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        empty_file(name_of_file_in_fc__1),
                        empty_file(name_of_file_in_fc__2),
                        empty_file(name_of_file_not_in_fc__1),
                        empty_file(name_of_file_not_in_fc__2),
                    ])
                )
            ),
        ]
        # ACT & ASSERT #
        integration_check.CHECKER.check_multi__w_source_variants(
            self,
            arguments.as_arguments,
            symbol_references=asrt.matches_sequence([
                is_reference_to_file_matcher__ref(file_matcher_name),
            ]),
            input_=model_constructor__non_recursive(checked_dir.path_sdv),
            execution=execution_cases
        )


PRIM_AND_EXE_EXPECTATION__NON_MATCH = prim_and_exe_w_header_matcher(
    MATCHES_FULL__STRUCTURE_NAME,
    PrimAndExeExpectation.of_exe(main_result=asrt.equals(False))
)
