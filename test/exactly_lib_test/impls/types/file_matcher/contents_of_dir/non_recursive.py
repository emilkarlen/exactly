import unittest

from exactly_lib.tcfs.path_relativity import RelSdsOptionType, RelOptionType
from exactly_lib.type_val_deps.types.path import path_sdvs
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources import invalid_model, \
    files_matcher_integration, executor_for_dir_contents
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources.cases import file_type
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources.hard_error import \
    HardErrorDueToHardErrorFromFilesMatcherHelper
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as args
from exactly_lib_test.impls.types.file_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.files_matcher.models.test_resources import model_checker
from exactly_lib_test.impls.types.files_matcher.models.test_resources import test_data
from exactly_lib_test.impls.types.files_matcher.test_resources import arguments_building as fsm_args
from exactly_lib_test.impls.types.files_matcher.test_resources import instruction_validation_cases
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    PrimAndExeExpectation, Expectation, ExecutionExpectation
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.tcfs.test_resources import sds_populator, tcds_populators
from exactly_lib_test.test_resources.files.file_structure import DirContents, Dir
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources.references import is_reference_to_files_matcher
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources.symbol_context import FilesMatcherSymbolContext, \
    FilesMatcherSymbolContextOfPrimitiveConstant
from exactly_lib_test.type_val_prims.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as asrt_renderer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestFilesMatcherShouldBeValidated(),
        TestFilesMatcherShouldBeParsedAsSimpleExpression(),
        TestHardErrorDueToInvalidModel(),
        TestHardErrorDueToHardErrorFromFilesMatcher(),
        TestApplication(),
        TestFilesOfModel(),
        unittest.makeSuite(TestConcreteMatcher),
        TestDetectionOfFileType(),
    ])


class TestFilesMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        files_matcher = FilesMatcherSymbolContextOfPrimitiveConstant(
            'MATCHER',
            True,
        )
        after_bin_op = 'after bin op'
        # ACT & ASSERT #
        fsm_argument = fsm_args.conjunction([
            fsm_args.SymbolReference(files_matcher.name),
            fsm_args.Custom(after_bin_op),
        ])
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            source=args.DirContents(
                fsm_argument,
            ).as_remaining_source,
            input_=integration_check.current_directory(),
            arrangement=arrangement_w_tcds(
                symbols=files_matcher.symbol_table,
            ),
            expectation=Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_line(
                        current_line_number=1,
                        remaining_part_of_current_line=fsm_argument.operator + ' ' + after_bin_op),
                    symbol_references=files_matcher.references_assertion
                ),
                ExecutionExpectation(
                    main_result=asrt_matching_result.matches_value(files_matcher.result_value)
                )
            ),
        )


class TestFilesMatcherShouldBeValidated(unittest.TestCase):
    def runTest(self):
        fsm_symbol_name = 'the_files_matcher'
        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
            self,
            args.DirContents(args.SymbolReference(fsm_symbol_name)
                             ).as_arguments,
            symbol_references=asrt.matches_singleton_sequence(
                is_reference_to_files_matcher(fsm_symbol_name)
            ),
            input_=
            integration_check.constant_relative_file_name('arbitrary-file-argument'),
            execution=instruction_validation_cases.failing_validation_cases__multi_exe(fsm_symbol_name)
        )


class TestHardErrorDueToInvalidModel(unittest.TestCase):
    def runTest(self):
        unconditionally_constant_true = FilesMatcherSymbolContext.of_primitive_constant(
            'unconditionally_constant_true',
            True)
        symbols = unconditionally_constant_true.symbol_table

        location = RelSdsOptionType.REL_TMP
        model_file_name = 'the-checked-file'

        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
            self,
            arguments=
            args.DirContents(
                args.SymbolReference(unconditionally_constant_true.name)
            ).as_arguments,
            symbol_references=
            asrt.matches_singleton_sequence(
                unconditionally_constant_true.reference_assertion
            ),
            input_=
            integration_check.file_in_sds(location, model_file_name),
            execution=[
                NExArr(
                    invalid_file_case.name,
                    PrimAndExeExpectation.of_exe(
                        is_hard_error=asrt_renderer.is_renderer_of_major_blocks()
                    ),
                    arrangement_w_tcds(
                        symbols=symbols,
                        non_hds_contents=sds_populator.contents_in(
                            location,
                            invalid_file_case.value
                        )
                    )
                )
                for invalid_file_case in invalid_model.cases(model_file_name)
            ]
        )


class TestHardErrorDueToHardErrorFromFilesMatcher(unittest.TestCase):
    def runTest(self):
        helper = HardErrorDueToHardErrorFromFilesMatcherHelper()

        integration_check.CHECKER__PARSE_FULL.check(
            self,
            source=args.DirContents(
                fsm_args.SymbolReference(helper.files_matcher_name)
            ).as_remaining_source,
            input_=helper.model_constructor(),
            arrangement=helper.arrangement(),
            expectation=helper.expectation()
        )


class TestApplication(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        files_matcher_name = 'the_files_matcher'
        checked_dir_location = RelSdsOptionType.REL_TMP
        checked_dir = Dir.empty('checked-dir')

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
            self,
            arguments=args.DirContents(
                fsm_args.SymbolReference(files_matcher_name)
            ).as_arguments,
            input_=
            integration_check.file_in_sds(checked_dir_location, checked_dir.name),
            symbol_references=asrt.matches_singleton_sequence(
                is_reference_to_files_matcher(files_matcher_name)
            ),
            execution=[
                NExArr(
                    'checked dir is empty',
                    PrimAndExeExpectation.of_exe(
                        main_result=asrt_matching_result.matches_value(matcher_result)
                    ),
                    arrangement_w_tcds(
                        non_hds_contents=sds_populator.contents_in(
                            checked_dir_location,
                            DirContents([checked_dir])
                        ),
                        symbols=FilesMatcherSymbolContext.of_primitive_constant(files_matcher_name,
                                                                                matcher_result
                                                                                ).symbol_table,
                    ),
                )
                for matcher_result in [False, True]
            ],
        )


class TestFilesOfModel(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model_location = RelOptionType.REL_TMP
        model_name = 'the-model-dir'
        model_path = path_sdvs.of_rel_option_with_const_file_name(model_location, model_name)

        model_checker_symbol_name = 'symbol_that_checks_model'

        contents_cases = test_data.strip_file_type_info_s(
            [
                test_data.expected_is_direct_contents_of_actual(case.name, case.value)
                for case in test_data.cases()
            ]
        )

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check_multi(
            self,
            arguments=args.DirContents(
                fsm_args.SymbolReference(model_checker_symbol_name)
            ).as_arguments,
            parse_expectation=
            ParseExpectation(
                symbol_references=asrt.matches_singleton_sequence(
                    is_reference_to_files_matcher(model_checker_symbol_name)
                ),
            ),
            input_=
            integration_check.file_in_tcds(model_location, model_name),
            execution=[
                NExArr(
                    contents_case.name,
                    PrimAndExeExpectation.of_exe(),
                    arrangement_w_tcds(
                        tcds_contents=tcds_populators.TcdsPopulatorForRelOptionType(
                            model_location,
                            DirContents([
                                Dir(model_name, contents_case.actual)
                            ])
                        ),
                        symbols=SymbolTable({
                            model_checker_symbol_name:
                                model_checker.matcher__sym_tbl_container(self, model_path, contents_case.expected)
                        })
                    ),
                )
                for contents_case in contents_cases
            ],
        )


class TestConcreteMatcher(unittest.TestCase):
    def test_wo_selection(self):
        # ARRANGE #
        helper = files_matcher_integration.NumFilesWoSelectionTestCaseHelper(
            files_matcher_integration.MODEL_CONTENTS__NON_RECURSIVE,
            RelSdsOptionType.REL_ACT,
            'checked-dir',
        )
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
            self,
            arguments=helper.arg__non_recursive().as_arguments,
            input_=
            integration_check.file_in_sds(helper.checked_dir_location,
                                          helper.checked_dir_name),
            symbol_references=asrt.is_empty_sequence,
            execution=helper.execution_cases()
        )

    def test_w_selection(self):
        # ARRANGE #
        helper = files_matcher_integration.NumFilesWFileTypeSelectionTestCaseHelper(
            files_matcher_integration.MODEL_CONTENTS__NON_RECURSIVE__SELECTION_TYPE_FILE,
            RelSdsOptionType.REL_TMP,
            'checked-dir',
        )
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
            self,
            arguments=helper.arg__non_recursive().as_arguments,
            input_=
            integration_check.file_in_sds(helper.checked_dir_location,
                                          helper.checked_dir_name),
            symbol_references=asrt.is_empty_sequence,
            execution=helper.execution_cases()
        )


class TestDetectionOfFileType(unittest.TestCase):
    def runTest(self):
        _EXECUTOR.execute_list(
            self,
            file_type.file_type_detection__non_recursive()
        )


_EXECUTOR = executor_for_dir_contents.ExecutorOfCaseGeneratorForDirContents()
