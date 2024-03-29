import unittest

from exactly_lib.definitions import logic
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.tcfs.path_relativity import RelSdsOptionType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources import executor_for_dir_contents
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources import invalid_model, \
    files_matcher_integration
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources.cases import file_type
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources.hard_error import \
    HardErrorDueToHardErrorFromFilesMatcherHelper
from exactly_lib_test.impls.types.file_matcher.contents_of_dir.test_resources.helper_utils import \
    IntegrationCheckHelper
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as args
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.impls.types.file_matcher.test_resources import integration_check
from exactly_lib_test.impls.types.files_matcher.models.test_resources import model_checker
from exactly_lib_test.impls.types.files_matcher.models.test_resources import test_data
from exactly_lib_test.impls.types.files_matcher.test_resources import arguments_building as fsm_args
from exactly_lib_test.impls.types.files_matcher.test_resources import instruction_validation_cases
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, \
    PrimAndExeExpectation, ExecutionExpectation, ParseExpectation, Expectation
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.tcfs.test_resources import sds_populator
from exactly_lib_test.test_resources.argument_renderer import OptionArgument
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
        TestParseShouldFailWhenInvalidOption(),
        TestFilesMatcherShouldBeValidated(),
        TestFilesMatcherShouldBeParsedAsSimpleExpression(),
        TestHardErrorDueToInvalidModel(),
        TestHardErrorDueToHardErrorFromFilesMatcher(),
        TestApplication(),
        TestFilesOfModel(),
        unittest.makeSuite(TestConcreteMatcher),
        unittest.makeSuite(TestDetectionOfFileType),
    ])


class TestParseShouldFailWhenInvalidOption(unittest.TestCase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            integration_check.CHECKER__PARSE_FULL.parser.parse(
                fm_args.InvalidDirContents(
                    OptionArgument(a.OptionName('invalid-option'))
                ).as_remaining_source
            )


class TestFilesMatcherShouldBeParsedAsSimpleExpression(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        files_matcher = FilesMatcherSymbolContextOfPrimitiveConstant(
            'MATCHER',
            True,
        )
        after_bin_op = 'after bin op'
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_SIMPLE.check(
            self,
            source=args.DirContentsRecursive(
                fsm_args.conjunction([
                    fsm_args.SymbolReference(files_matcher.name),
                    fsm_args.Custom(after_bin_op),
                ]),
            ).as_remaining_source,
            input_=integration_check.current_directory(),
            arrangement=arrangement_w_tcds(
                symbols=files_matcher.symbol_table,
            ),
            expectation=Expectation(
                ParseExpectation(
                    source=asrt_source.is_at_line(
                        current_line_number=1,
                        remaining_part_of_current_line=logic.AND_OPERATOR_NAME + ' ' + after_bin_op),
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
            args.DirContentsRecursive(args.SymbolReference(fsm_symbol_name)
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
            True
        )
        symbols = unconditionally_constant_true.symbol_table

        location = RelSdsOptionType.REL_TMP
        model_file_name = 'the-checked-file'

        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
            self,
            arguments=
            args.DirContentsRecursive(
                args.SymbolReference(unconditionally_constant_true.name)
            ).as_arguments,
            symbol_references=
            unconditionally_constant_true.references_assertion,
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
            source=fm_args.DirContentsRecursive(
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
            arguments=fm_args.DirContentsRecursive(
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
                                                                                ).symbol_table
                    ),
                )
                for matcher_result in [False, True]
            ],
        )


class TestFilesOfModel(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        helper = IntegrationCheckHelper()

        contents_cases = test_data.strip_file_type_info_s(
            [
                test_data.identical_expected_and_actual(case.name, case.value)
                for case in test_data.cases()
            ]
        )

        # ACT & ASSERT #

        integration_check.CHECKER__PARSE_FULL.check_multi(
            self,
            arguments=fm_args.DirContentsRecursive(
                helper.files_matcher_sym_ref_arg()
            ).as_arguments,
            parse_expectation=
            helper.parse_expectation_of_symbol_references(),
            input_=
            helper.model_constructor_for_checked_dir(),
            execution=[
                NExArr(
                    contents_case.name,
                    PrimAndExeExpectation.of_exe(),
                    helper.arrangement_for_contents_of_model(
                        checked_dir_contents=contents_case.actual,
                        files_matcher_symbol_value=
                        model_checker.matcher(self,
                                              helper.dir_arg.path_sdv,
                                              contents_case.expected,
                                              ),
                    ),
                )
                for contents_case in contents_cases
            ],
        )


class TestConcreteMatcher(unittest.TestCase):
    def test_wo_selection(self):
        # ARRANGE #
        helper = files_matcher_integration.NumFilesWoSelectionTestCaseHelper(
            files_matcher_integration.MODEL_CONTENTS__RECURSIVE,
            RelSdsOptionType.REL_ACT,
            'checked-dir',
        )
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
            self,
            arguments=helper.arg__recursive().as_arguments,
            input_=
            integration_check.file_in_sds(helper.checked_dir_location,
                                          helper.checked_dir_name),
            symbol_references=asrt.is_empty_sequence,
            execution=helper.execution_cases()
        )

    def test_w_selection(self):
        # ARRANGE #
        helper = files_matcher_integration.NumFilesWFileTypeSelectionTestCaseHelper(
            files_matcher_integration.MODEL_CONTENTS__RECURSIVE__SELECTION_TYPE_FILE,
            RelSdsOptionType.REL_TMP,
            'checked-dir',
        )
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check_multi__w_source_variants(
            self,
            arguments=helper.arg__recursive().as_arguments,
            input_=
            integration_check.file_in_sds(helper.checked_dir_location,
                                          helper.checked_dir_name),
            symbol_references=asrt.is_empty_sequence,
            execution=helper.execution_cases()
        )


class TestDetectionOfFileType(unittest.TestCase):
    def test_depth_0(self):
        _EXECUTOR.execute_list(
            self,
            file_type.file_type_detection__recursive__depth_0()
        )

    def test_depth_1(self):
        _EXECUTOR.execute_list(
            self,
            file_type.file_type_detection__recursive__depth_1()
        )


_EXECUTOR = executor_for_dir_contents.ExecutorOfCaseGeneratorForDirContents()
