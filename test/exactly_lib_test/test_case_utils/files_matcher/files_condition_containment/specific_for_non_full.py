import unittest

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.test_case_utils.files_matcher.impl.matches.common import \
    MATCHES_NON_FULL__STRUCTURE_NAME
from exactly_lib_test.symbol.test_resources.file_matcher import is_reference_to_file_matcher
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_case_utils.files_condition.test_resources import arguments_building as fc_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources.files_condition import \
    exe_w_added_header_matcher, IS_REGULAR_FILE_FILE_MATCHER, prim_and_exe_w_header_matcher, \
    MATCHING_EXECUTION_EXPECTATION, is_dir_file_matcher, is_regular_file_matcher
from exactly_lib_test.test_case_utils.files_matcher.test_resources.model import model_constructor__non_recursive
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Arrangement, ParseExpectation, \
    PrimAndExeExpectation, Expectation
from exactly_lib_test.test_case_utils.test_resources.dir_arg_helper import DirArgumentHelper
from exactly_lib_test.test_resources.files.file_structure import File, Dir
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestModelContainsMoreFilesThanFc)


class TestModelContainsMoreFilesThanFc(unittest.TestCase):
    def test_empty_fc(self):
        # ARRANGE #
        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'dir-w-single-file')
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check__w_source_variants(
            self,
            args.matches_non_full(fc_args.FilesConditionArg.empty()).as_arguments,
            model_constructor__non_recursive(checked_dir.path_sdv),
            Arrangement(
                tcds=checked_dir.tcds_arrangement_dir_with_contents([
                    File.empty('a-file')
                ])
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.is_empty_sequence
                ),
                exe_w_added_header_matcher(MATCHES_NON_FULL__STRUCTURE_NAME,
                                           MATCHING_EXECUTION_EXPECTATION),
            ),
        )

    def test_1_file_in_fc_wo_matcher(self):
        # ARRANGE #
        name_of_file_in_fc = 'file-in-files-condition'
        name_of_file_not_in_fc_1 = 'file-not-in-files-condition-1'
        name_of_file_not_in_fc_2 = 'file-not-in-files-condition-2'

        arguments = args.matches_non_full(
            fc_args.FilesCondition([fc_args.FileCondition(name_of_file_in_fc)])
        )

        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'dir-w-more-than-one-file')

        execution_cases = [
            NExArr(
                '2 files: one file name matches',
                PRIM_AND_EXE_EXPECTATION__MATCH,
                Arrangement(
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_in_fc),
                        File.empty(name_of_file_not_in_fc_1),
                    ])
                )
            ),
            NExArr(
                '2 files: no file name matches',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_not_in_fc_1),
                        File.empty(name_of_file_not_in_fc_2),
                    ])
                )
            ),
            NExArr(
                '3 files: one file name matches',
                PRIM_AND_EXE_EXPECTATION__MATCH,
                Arrangement(
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_in_fc),
                        File.empty(name_of_file_not_in_fc_1),
                        File.empty(name_of_file_not_in_fc_2),
                    ])
                )
            )
        ]
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
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

        arguments = args.matches_non_full(
            fc_args.FilesCondition([
                fc_args.FileCondition(name_of_file_in_fc,
                                      fm_args.SymbolReferenceWReferenceSyntax(IS_REGULAR_FILE_FILE_MATCHER.name)),
            ])
        )

        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'dir-w-more-than-one-file')

        execution_cases = [
            NExArr(
                '2 files: one file name matches, and matcher matches',
                PRIM_AND_EXE_EXPECTATION__MATCH,
                Arrangement(
                    symbols=IS_REGULAR_FILE_FILE_MATCHER.symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_in_fc),
                        File.empty(name_of_file_not_in_fc_1),
                    ])
                )
            ),
            NExArr(
                '2 files: one file name matches, but matcher does not match',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    symbols=is_dir_file_matcher(IS_REGULAR_FILE_FILE_MATCHER.name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_in_fc),
                        File.empty(name_of_file_not_in_fc_1),
                    ])
                )
            ),
            NExArr(
                '3 files: one file name matches, and matcher matches',
                PRIM_AND_EXE_EXPECTATION__MATCH,
                Arrangement(
                    symbols=is_dir_file_matcher(IS_REGULAR_FILE_FILE_MATCHER.name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        Dir.empty(name_of_file_in_fc),
                        File.empty(name_of_file_not_in_fc_1),
                        File.empty(name_of_file_not_in_fc_2),
                    ])
                )
            )
        ]
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
            self,
            arguments.as_arguments,
            symbol_references=asrt.matches_sequence([
                IS_REGULAR_FILE_FILE_MATCHER.reference_assertion,
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
        name_of_file_not_in_fc__3 = 'file-not-in-files-condition-3'

        file_matcher_name = 'the_file_matcher'
        arguments = args.matches_non_full(
            fc_args.FilesCondition([
                fc_args.FileCondition(name_of_file_in_fc__1,
                                      fm_args.SymbolReferenceWReferenceSyntax(file_matcher_name)),
                fc_args.FileCondition(name_of_file_in_fc__2),
            ])
        )

        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'dir-w-more-than-two-files')

        execution_cases = [
            NExArr(
                '3 files: no file name matches',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    symbols=is_regular_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_not_in_fc__1),
                        File.empty(name_of_file_not_in_fc__2),
                        File.empty(name_of_file_not_in_fc__3),
                    ])
                )
            ),
            NExArr(
                '3 files: one file name matches, and matcher matches',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    symbols=is_regular_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_in_fc__1),
                        File.empty(name_of_file_not_in_fc__1),
                        File.empty(name_of_file_not_in_fc__2),
                    ])
                )
            ),
            NExArr(
                '3 files: both file names matches, and matcher matches',
                PRIM_AND_EXE_EXPECTATION__MATCH,
                Arrangement(
                    symbols=is_regular_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_in_fc__1),
                        File.empty(name_of_file_in_fc__2),
                        File.empty(name_of_file_not_in_fc__1),
                    ])
                )
            ),
            NExArr(
                '3 files: both file name matches, but matcher does not match',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    symbols=is_dir_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_in_fc__1),
                        File.empty(name_of_file_in_fc__2),
                        File.empty(name_of_file_not_in_fc__1),
                    ])
                )
            ),
            NExArr(
                '4 files: both file name matches, and matcher matches',
                PRIM_AND_EXE_EXPECTATION__MATCH,
                Arrangement(
                    symbols=is_regular_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_in_fc__1),
                        File.empty(name_of_file_in_fc__2),
                        File.empty(name_of_file_not_in_fc__1),
                        File.empty(name_of_file_not_in_fc__2),
                    ])
                )
            ),
            NExArr(
                '4 files: both file name matches, but matcher does not match',
                PRIM_AND_EXE_EXPECTATION__NON_MATCH,
                Arrangement(
                    symbols=is_dir_file_matcher(file_matcher_name).symbol_table,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_in_fc__1),
                        File.empty(name_of_file_in_fc__2),
                        File.empty(name_of_file_not_in_fc__1),
                        File.empty(name_of_file_not_in_fc__2),
                    ])
                )
            ),
        ]
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
            self,
            arguments.as_arguments,
            symbol_references=asrt.matches_sequence([
                is_reference_to_file_matcher(file_matcher_name),
            ]),
            input_=model_constructor__non_recursive(checked_dir.path_sdv),
            execution=execution_cases
        )


PRIM_AND_EXE_EXPECTATION__NON_MATCH = prim_and_exe_w_header_matcher(
    MATCHES_NON_FULL__STRUCTURE_NAME,
    PrimAndExeExpectation.of_exe(main_result=asrt.equals(False))
)

PRIM_AND_EXE_EXPECTATION__MATCH = prim_and_exe_w_header_matcher(
    MATCHES_NON_FULL__STRUCTURE_NAME,
    PrimAndExeExpectation.of_exe(main_result=asrt.equals(True))
)
