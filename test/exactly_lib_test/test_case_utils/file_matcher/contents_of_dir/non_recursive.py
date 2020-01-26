import unittest

from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType, RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref
from exactly_lib_test.test_case_file_structure.test_resources import sds_populator, tcds_populators
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources import invalid_model, \
    files_matcher_integration
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.hard_error import \
    HardErrorDueToHardErrorFromFilesMatcherHelper
from exactly_lib_test.test_case_utils.file_matcher.contents_of_dir.test_resources.model_contents import \
    model_checker
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.models.test_resources import test_data
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import validation_cases
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import arrangement_w_tcds, \
    ExecutionExpectation, ParseExpectation
from exactly_lib_test.test_resources.files.file_structure import DirContents, empty_dir, Dir
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as asrt_renderer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestFilesMatcherShouldBeValidated(),
        TestHardErrorDueToInvalidModel(),
        TestHardErrorDueToHardErrorFromFilesMatcher(),
        TestApplication(),
        TestFilesOfModel(),
        unittest.makeSuite(TestConcreteMatcher),
    ])


class TestFilesMatcherShouldBeValidated(unittest.TestCase):
    def runTest(self):
        fsm_symbol_name = 'the_files_matcher'
        integration_check.CHECKER.check_multi__w_source_variants(
            self,
            args.DirContents(args.SymbolReference(fsm_symbol_name)
                             ).as_arguments,
            symbol_references=asrt.matches_singleton_sequence(
                is_reference_to_files_matcher__ref(fsm_symbol_name)
            ),
            model_constructor=
            integration_check.constant_relative_file_name('arbitrary-file-argument'),
            execution=validation_cases.failing_validation_cases__multi_exe(fsm_symbol_name)
        )


class TestHardErrorDueToInvalidModel(unittest.TestCase):
    def runTest(self):
        unconditionally_constant_true = NameAndValue(
            'unconditionally_constant_true',
            FilesMatcherSdv(
                matchers.sdv_from_bool(True)
            )
        )
        symbols = symbol_utils.symbol_table_from_name_and_sdvs([unconditionally_constant_true])

        location = RelSdsOptionType.REL_TMP
        model_file_name = 'the-checked-file'

        integration_check.CHECKER.check_multi__w_source_variants(
            self,
            arguments=
            args.DirContents(
                args.SymbolReference(unconditionally_constant_true.name)
            ).as_arguments,
            symbol_references=
            asrt.matches_singleton_sequence(
                is_reference_to_files_matcher__ref(unconditionally_constant_true.name)
            ),
            model_constructor=
            integration_check.file_in_sds(location, model_file_name),
            execution=[
                NExArr(
                    invalid_file_case.name,
                    ExecutionExpectation(
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

        integration_check.CHECKER.check(
            self,
            source=fm_args.DirContents(
                fms_args.SymbolReference(helper.files_matcher_name)
            ).as_remaining_source,
            model_constructor=helper.model_constructor(),
            arrangement=helper.arrangement(),
            expectation=helper.expectation()
        )


class TestApplication(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        files_matcher_name = 'the_files_matcher'
        checked_dir_location = RelSdsOptionType.REL_TMP
        checked_dir = empty_dir('checked-dir')

        # ACT & ASSERT #

        integration_check.CHECKER.check_multi__w_source_variants(
            self,
            arguments=fm_args.DirContents(
                fms_args.SymbolReference(files_matcher_name)
            ).as_arguments,
            model_constructor=
            integration_check.file_in_sds(checked_dir_location, checked_dir.name),
            symbol_references=asrt.matches_singleton_sequence(
                is_reference_to_files_matcher__ref(files_matcher_name)
            ),
            execution=[
                NExArr(
                    'checked dir is empty',
                    ExecutionExpectation(
                        main_result=asrt_matching_result.matches_value(matcher_result)
                    ),
                    arrangement_w_tcds(
                        non_hds_contents=sds_populator.contents_in(
                            checked_dir_location,
                            DirContents([checked_dir])
                        ),
                        symbols=symbol_utils.symbol_table_from_name_and_sdv_mapping({
                            files_matcher_name:
                                FilesMatcherSdv(matchers.sdv_from_bool(matcher_result))
                        }),
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

        integration_check.CHECKER.check_multi(
            self,
            arguments=fm_args.DirContents(
                fms_args.SymbolReference(model_checker_symbol_name)
            ).as_arguments,
            parse_expectation=
            ParseExpectation(
                symbol_references=asrt.matches_singleton_sequence(
                    is_reference_to_files_matcher__ref(model_checker_symbol_name)
                ),
            ),
            model_constructor=
            integration_check.file_in_tcds(model_location, model_name),
            execution=[
                NExArr(
                    contents_case.name,
                    ExecutionExpectation(),
                    arrangement_w_tcds(
                        tcds_contents=tcds_populators.TcdsPopulatorForRelOptionType(
                            model_location,
                            DirContents([
                                Dir(model_name, contents_case.actual)
                            ])
                        ),
                        symbols=symbol_utils.symbol_table_from_name_and_sdv_mapping({
                            model_checker_symbol_name:
                                model_checker.matcher(self, model_path, contents_case.expected)
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
        integration_check.CHECKER.check_multi__w_source_variants(
            self,
            arguments=helper.arg__non_recursive().as_arguments,
            model_constructor=
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
        integration_check.CHECKER.check_multi__w_source_variants(
            self,
            arguments=helper.arg__non_recursive().as_arguments,
            model_constructor=
            integration_check.file_in_sds(helper.checked_dir_location,
                                          helper.checked_dir_name),
            symbol_references=asrt.is_empty_sequence,
            execution=helper.execution_cases()
        )
