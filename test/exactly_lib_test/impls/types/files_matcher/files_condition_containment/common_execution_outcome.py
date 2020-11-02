import unittest

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.impls.types.files_condition.test_resources import arguments_building as fc_args
from exactly_lib_test.impls.types.files_matcher.test_resources.files_condition import \
    check_non_full_and_full__multi, check_non_full_and_full, Case, NON_MATCHING_EXECUTION_EXPECTATION, \
    MATCHING_EXECUTION_EXPECTATION, IS_REGULAR_FILE_FILE_MATCHER, IS_DIR_FILE_MATCHER, \
    IS_REGULAR_AND_IS_DIR_MATCHER_SYMBOLS
from exactly_lib_test.impls.types.files_matcher.test_resources.model import model_constructor__non_recursive, \
    model_constructor__recursive
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, ParseExpectation, \
    ExecutionExpectation, PrimAndExeExpectation, Expectation
from exactly_lib_test.impls.types.matcher.test_resources import matchers
from exactly_lib_test.impls.types.test_resources.dir_arg_helper import DirArgumentHelper
from exactly_lib_test.test_resources.files.file_structure import Dir, File
from exactly_lib_test.test_resources.test_utils import NExArr, NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.test_resources.file_matcher import FileMatcherSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestResultShouldBeHardErrorWhenFileMatcherReportsHardError(),
        TestFailWhenFewerFilesInModel(),
        unittest.makeSuite(TestNonMatchingCasesWithSameNumberOfFilesInFcAndModel),
        unittest.makeSuite(TestMatchingCasesWithSameNumberOfFilesInFcAndModel),
    ])


class TestResultShouldBeHardErrorWhenFileMatcherReportsHardError(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'a-dir')

        unconditionally_hard_error_file_matcher = FileMatcherSymbolContext.of_primitive(
            'unconditionally_hard_error_file_matcher',
            matchers.MatcherThatReportsHardError()
        )
        file_in_model = 'a-file'
        # ACT & ASSERT #
        check_non_full_and_full(
            self,
            fc_args.FilesCondition([
                fc_args.FileCondition(
                    file_in_model,
                    fm_args.SymbolReferenceWReferenceSyntax(
                        unconditionally_hard_error_file_matcher.name
                    )),
            ]),
            model_constructor__non_recursive(checked_dir.path_sdv),
            Arrangement(
                symbols=unconditionally_hard_error_file_matcher.symbol_table,
                tcds=checked_dir.tcds_arrangement_dir_with_contents([
                    File.empty(file_in_model)
                ])
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_singleton_sequence(
                        unconditionally_hard_error_file_matcher.reference_assertion
                    )
                ),
                ExecutionExpectation(
                    is_hard_error=asrt_text_doc.is_any_text()
                )
            ),
        )


class TestFailWhenFewerFilesInModel(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        checked_dir = DirArgumentHelper(RelOptionType.REL_ACT, 'a-dir')

        fc_file_1 = 'file-1'
        fc_file_2 = 'file-2'
        file_name_not_in_fc = 'not-in-fc'

        unconditionally_matching_file_matcher = FileMatcherSymbolContext.of_primitive_constant(
            'unconditionally_matching_file_matcher',
            True
        )

        unconditionally_matching_file_matcher_sym_ref_arg = fm_args.SymbolReferenceWReferenceSyntax(
            unconditionally_matching_file_matcher.name
        )
        unconditionally_matching_file_matcher_sym_ref_assertion = unconditionally_matching_file_matcher.reference_assertion
        symbol_table_with_unconditionally_matching_file_matcher = unconditionally_matching_file_matcher.symbol_table

        files_condition_w_2_files_cases = [
            NIE(
                'no file matcher',
                asrt.is_empty_sequence,
                fc_args.FilesCondition([
                    fc_args.FileCondition(fc_file_1),
                    fc_args.FileCondition(fc_file_2),
                ]),
            ),
            NIE(
                'file matcher on one file',
                asrt.matches_sequence([
                    unconditionally_matching_file_matcher_sym_ref_assertion,
                ]),
                fc_args.FilesCondition([
                    fc_args.FileCondition(fc_file_1, unconditionally_matching_file_matcher_sym_ref_arg),
                    fc_args.FileCondition(fc_file_2),
                ]),
            ),
            NIE(
                'file matcher on all files',
                asrt.matches_sequence([
                    unconditionally_matching_file_matcher_sym_ref_assertion,
                    unconditionally_matching_file_matcher_sym_ref_assertion,
                ]),
                fc_args.FilesCondition([
                    fc_args.FileCondition(fc_file_1, unconditionally_matching_file_matcher_sym_ref_arg),
                    fc_args.FileCondition(fc_file_2, unconditionally_matching_file_matcher_sym_ref_arg),
                ]),
            ),
        ]

        expectation_of_matching_giving_false = PrimAndExeExpectation.of_exe(
            main_result=asrt.equals(False)
        )

        model_contents_cases = [
            NExArr(
                'model is empty',
                expectation_of_matching_giving_false,
                Arrangement(
                    symbols=symbol_table_with_unconditionally_matching_file_matcher,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([])
                ),
            ),
            NExArr(
                'model contains single file with name in FILES-CONDITION',
                expectation_of_matching_giving_false,
                Arrangement(
                    symbols=symbol_table_with_unconditionally_matching_file_matcher,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(fc_file_1)
                    ])
                ),
            ),
            NExArr(
                'model contains single file with name not in FILES-CONDITION',
                expectation_of_matching_giving_false,
                Arrangement(
                    symbols=symbol_table_with_unconditionally_matching_file_matcher,
                    tcds=checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(file_name_not_in_fc)
                    ])
                ),
            ),
        ]
        for files_condition_w_2_files_case in files_condition_w_2_files_cases:
            with self.subTest(files_condition_w_2_files_case.name):
                # ACT & ASSERT #
                check_non_full_and_full__multi(
                    self,
                    files_condition_w_2_files_case.input_value,
                    symbol_references=files_condition_w_2_files_case.expected_value,
                    model=model_constructor__non_recursive(checked_dir.path_sdv),
                    execution=model_contents_cases,
                )


class TestNonMatchingCasesWithSameNumberOfFilesInFcAndModel(unittest.TestCase):
    def test_single_file(self):
        # ARRANGE #
        name_of_file_in_model = 'file-in-model'
        name_of_file_not_in_model = 'file-not-in-model'

        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'dir-w-single-file')

        cases = [
            Case(
                'no file matcher - different names',
                fc_args.FilesCondition([
                    fc_args.FileCondition(name_of_file_not_in_model),
                ]),
                Arrangement(
                    IS_REGULAR_AND_IS_DIR_MATCHER_SYMBOLS,
                    checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_in_model)
                    ])
                ),
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.is_empty_sequence
                    ),
                    NON_MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
            Case(
                'same names - non-matching matcher/actual is dir',
                fc_args.FilesCondition([
                    fc_args.FileCondition(
                        name_of_file_in_model,
                        fm_args.SymbolReferenceWReferenceSyntax(IS_REGULAR_FILE_FILE_MATCHER.name)
                    ),
                ]),
                Arrangement(
                    IS_REGULAR_AND_IS_DIR_MATCHER_SYMBOLS,
                    checked_dir.tcds_arrangement_dir_with_contents([
                        Dir.empty(name_of_file_in_model)
                    ])
                ),
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.matches_singleton_sequence(
                            IS_REGULAR_FILE_FILE_MATCHER.reference_assertion
                        )
                    ),
                    NON_MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
            Case(
                'same names - non-matching matcher/actual is regular file',
                fc_args.FilesCondition([
                    fc_args.FileCondition(
                        name_of_file_in_model,
                        fm_args.SymbolReferenceWReferenceSyntax(IS_DIR_FILE_MATCHER.name)
                    ),
                ]),
                Arrangement(
                    IS_REGULAR_AND_IS_DIR_MATCHER_SYMBOLS,
                    checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_file_in_model)
                    ])
                ),
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.matches_singleton_sequence(
                            IS_DIR_FILE_MATCHER.reference_assertion
                        )
                    ),
                    NON_MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_non_full_and_full(
                    self,
                    case.files_condition,
                    model_constructor__non_recursive(checked_dir.path_sdv),
                    case.arrangement,
                    case.expectation,
                )

    def test_multiple_files(self):
        # ARRANGE #
        name_of_file_in_model__regular = 'a-regular-file-in-model'
        name_of_file_in_model__dir = 'a-dir-in-model'
        name_of_file_not_in_model = 'file-not-in-model'

        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'dir-w-multiple-files')

        arrangement = Arrangement(
            IS_REGULAR_AND_IS_DIR_MATCHER_SYMBOLS,
            checked_dir.tcds_arrangement_dir_with_contents([
                File.empty(name_of_file_in_model__regular),
                Dir.empty(name_of_file_in_model__dir),
            ])
        )
        cases = [
            Case(
                'no file matchers - one name not in model',
                fc_args.FilesCondition([
                    fc_args.FileCondition(name_of_file_in_model__regular),
                    fc_args.FileCondition(name_of_file_not_in_model),
                ]),
                arrangement,
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.is_empty_sequence
                    ),
                    NON_MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
            Case(
                'expected names - one matcher that do not match',
                fc_args.FilesCondition([
                    fc_args.FileCondition(name_of_file_in_model__regular),
                    fc_args.FileCondition(name_of_file_in_model__dir,
                                          fm_args.SymbolReferenceWReferenceSyntax(IS_REGULAR_FILE_FILE_MATCHER.name)),
                ]),
                arrangement,
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.matches_singleton_sequence(
                            IS_REGULAR_FILE_FILE_MATCHER.reference_assertion
                        )
                    ),
                    NON_MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
            Case(
                'expected names - all with matchers, 1st matches, 2nd do not match',
                fc_args.FilesCondition([
                    fc_args.FileCondition(name_of_file_in_model__regular,
                                          fm_args.SymbolReferenceWReferenceSyntax(IS_REGULAR_FILE_FILE_MATCHER.name)),
                    fc_args.FileCondition(name_of_file_in_model__dir,
                                          fm_args.SymbolReferenceWReferenceSyntax(IS_REGULAR_FILE_FILE_MATCHER.name)),
                ]),
                arrangement,
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.matches_sequence([
                            IS_REGULAR_FILE_FILE_MATCHER.reference_assertion,
                            IS_REGULAR_FILE_FILE_MATCHER.reference_assertion,
                        ]
                        )
                    ),
                    NON_MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
            Case(
                'expected names - all with matchers, 1st do not match, 2nd matches',
                fc_args.FilesCondition([
                    fc_args.FileCondition(name_of_file_in_model__regular,
                                          fm_args.SymbolReferenceWReferenceSyntax(IS_DIR_FILE_MATCHER.name)),
                    fc_args.FileCondition(name_of_file_in_model__dir,
                                          fm_args.SymbolReferenceWReferenceSyntax(IS_DIR_FILE_MATCHER.name)),
                ]),
                arrangement,
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.matches_sequence([
                            IS_DIR_FILE_MATCHER.reference_assertion,
                            IS_DIR_FILE_MATCHER.reference_assertion,
                        ]
                        )
                    ),
                    NON_MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_non_full_and_full(
                    self,
                    case.files_condition,
                    model_constructor__non_recursive(checked_dir.path_sdv),
                    case.arrangement,
                    case.expectation,
                )

    def test_recursive_model(self):
        # ARRANGE #
        file_in_sub_dir = File.empty('file-in-sub-dir')
        dir_in_checked_dir = Dir(
            'top-level-dir',
            [file_in_sub_dir],
        )
        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'the-dir')
        # ACT & ASSERT #
        check_non_full_and_full(
            self,
            fc_args.FilesCondition([
                fc_args.FileCondition(dir_in_checked_dir.name),
                fc_args.FileCondition(file_in_sub_dir.name),
            ]),
            model_constructor__recursive(checked_dir.path_sdv),
            Arrangement(
                tcds=checked_dir.tcds_arrangement_dir_with_contents([dir_in_checked_dir])
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.is_empty_sequence
                ),
                ExecutionExpectation(
                    main_result=asrt.equals(False)
                ),
            ),
        )


class TestMatchingCasesWithSameNumberOfFilesInFcAndModel(unittest.TestCase):
    def test_empty(self):
        # ARRANGE #
        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'empty-dir')
        # ACT & ASSERT #
        check_non_full_and_full(
            self,
            fc_args.FilesCondition([]),
            model_constructor__non_recursive(checked_dir.path_sdv),
            Arrangement(
                tcds=checked_dir.tcds_arrangement_dir_with_contents([])
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.is_empty_sequence
                ),
                ExecutionExpectation(
                    main_result=asrt.equals(True)
                ),
            ),
        )

    def test_single_file(self):
        # ARRANGE #
        name_of_single_file = 'the-single-file'
        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'dir-w-single-file')
        cases = [
            Case(
                'no file matcher',
                fc_args.FilesCondition([
                    fc_args.FileCondition(name_of_single_file),
                ]),
                Arrangement(
                    IS_REGULAR_AND_IS_DIR_MATCHER_SYMBOLS,
                    checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_single_file)
                    ])
                ),
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.is_empty_sequence
                    ),
                    MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
            Case(
                'with file matcher (actual is regular file)',
                fc_args.FilesCondition([
                    fc_args.FileCondition(
                        name_of_single_file,
                        fm_args.SymbolReferenceWReferenceSyntax(IS_REGULAR_FILE_FILE_MATCHER.name)
                    ),
                ]),
                Arrangement(
                    IS_REGULAR_AND_IS_DIR_MATCHER_SYMBOLS,
                    checked_dir.tcds_arrangement_dir_with_contents([
                        File.empty(name_of_single_file)
                    ])
                ),
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.matches_singleton_sequence(
                            IS_REGULAR_FILE_FILE_MATCHER.reference_assertion
                        )
                    ),
                    MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
            Case(
                'with file matcher (actual is dir)',
                fc_args.FilesCondition([
                    fc_args.FileCondition(
                        name_of_single_file,
                        fm_args.SymbolReferenceWReferenceSyntax(IS_DIR_FILE_MATCHER.name)
                    ),
                ]),
                Arrangement(
                    IS_REGULAR_AND_IS_DIR_MATCHER_SYMBOLS,
                    checked_dir.tcds_arrangement_dir_with_contents([
                        Dir.empty(name_of_single_file)
                    ])
                ),
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.matches_singleton_sequence(
                            IS_DIR_FILE_MATCHER.reference_assertion
                        )
                    ),
                    MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_non_full_and_full(
                    self,
                    case.files_condition,
                    model_constructor__non_recursive(checked_dir.path_sdv),
                    case.arrangement,
                    case.expectation,
                )

    def test_multiple_files(self):
        # ARRANGE #
        name_of_regular_file = 'a-regular-file'
        name_of_dir = 'a-dir'

        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'dir-w-multiple-files')

        arrangement = Arrangement(
            IS_REGULAR_AND_IS_DIR_MATCHER_SYMBOLS,
            checked_dir.tcds_arrangement_dir_with_contents([
                File.empty(name_of_regular_file),
                Dir.empty(name_of_dir),
            ])
        )
        cases = [
            Case(
                'no file matchers',
                fc_args.FilesCondition([
                    fc_args.FileCondition(name_of_regular_file),
                    fc_args.FileCondition(name_of_dir),
                ]),
                arrangement,
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.is_empty_sequence
                    ),
                    MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
            Case(
                'with matcher on regular file',
                fc_args.FilesCondition([
                    fc_args.FileCondition(name_of_regular_file,
                                          fm_args.SymbolReferenceWReferenceSyntax(IS_REGULAR_FILE_FILE_MATCHER.name)
                                          ),
                    fc_args.FileCondition(name_of_dir),
                ]),
                arrangement,
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.matches_singleton_sequence(
                            IS_REGULAR_FILE_FILE_MATCHER.reference_assertion
                        )
                    ),
                    MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
            Case(
                'with matcher on dir',
                fc_args.FilesCondition([
                    fc_args.FileCondition(name_of_regular_file),
                    fc_args.FileCondition(name_of_dir,
                                          fm_args.SymbolReferenceWReferenceSyntax(IS_DIR_FILE_MATCHER.name)
                                          ),
                ]),
                arrangement,
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.matches_singleton_sequence(
                            IS_DIR_FILE_MATCHER.reference_assertion
                        )
                    ),
                    MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
            Case(
                'with matcher on both files',
                fc_args.FilesCondition([
                    fc_args.FileCondition(name_of_regular_file,
                                          fm_args.SymbolReferenceWReferenceSyntax(IS_REGULAR_FILE_FILE_MATCHER.name)
                                          ),
                    fc_args.FileCondition(name_of_dir,
                                          fm_args.SymbolReferenceWReferenceSyntax(IS_DIR_FILE_MATCHER.name)
                                          ),
                ]),
                arrangement,
                Expectation(
                    ParseExpectation(
                        symbol_references=asrt.matches_sequence([
                            IS_REGULAR_FILE_FILE_MATCHER.reference_assertion,
                            IS_DIR_FILE_MATCHER.reference_assertion,
                        ]
                        )
                    ),
                    MATCHING_EXECUTION_EXPECTATION,
                ),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                check_non_full_and_full(
                    self,
                    case.files_condition,
                    model_constructor__non_recursive(checked_dir.path_sdv),
                    case.arrangement,
                    case.expectation,
                )

    def test_recursive_model(self):
        # ARRANGE #
        file_in_sub_dir = File.empty('file-in-sub-dir')
        dir_in_checked_dir = Dir(
            'top-level-dir',
            [file_in_sub_dir],
        )
        checked_dir = DirArgumentHelper(RelOptionType.REL_TMP, 'the-dir')
        # ACT & ASSERT #
        check_non_full_and_full(
            self,
            fc_args.FilesCondition([
                fc_args.FileCondition(dir_in_checked_dir.name),
                fc_args.FileCondition('/'.join((dir_in_checked_dir.name,
                                                file_in_sub_dir.name)
                                               )
                                      ),
            ]),
            model_constructor__recursive(checked_dir.path_sdv),
            Arrangement(
                tcds=checked_dir.tcds_arrangement_dir_with_contents([dir_in_checked_dir])
            ),
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.is_empty_sequence
                ),
                ExecutionExpectation(
                    main_result=asrt.equals(True)
                ),
            ),
        )
