import unittest

from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref
from exactly_lib_test.test_case_file_structure.test_resources import sds_populator
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import dir_contents as test_resources
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import validation_cases
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import arrangement_w_tcds, \
    ExecutionExpectation, ParseExpectation
from exactly_lib_test.test_resources.files.file_structure import empty_file, DirContents, empty_dir, Dir
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result
from exactly_lib_test.util.simple_textstruct.test_resources import renderer_assertions as asrt_renderer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestFilesMatcherShouldBeValidated(),
        unittest.makeSuite(TestHardError),
        TestApplication(),
        TestFilesOfModel(),
        TestConcreteMatcher(),
    ])


class TestFilesMatcherShouldBeValidated(unittest.TestCase):
    def runTest(self):
        fsm_symbol_name = 'the_files_matcher'
        integration_check.CHECKER.check_multi__w_source_variants(
            self,
            args.DirContentsRecursive(args.SymbolReference(fsm_symbol_name)
                                      ).as_arguments,
            symbol_references=asrt.matches_singleton_sequence(
                is_reference_to_files_matcher__ref(fsm_symbol_name)
            ),
            model_constructor=
            integration_check.constant_relative_file_name('arbitrary-file-argument'),
            execution=validation_cases.failing_validation_cases__multi_exe(fsm_symbol_name)
        )


class TestHardError(unittest.TestCase):
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
            args.DirContentsRecursive(
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
                for invalid_file_case in test_resources.invalid_file_cases(model_file_name)
            ]
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
            arguments=fm_args.DirContentsRecursive(
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
                        })
                    ),
                )
                for matcher_result in [False, True]
            ],
        )


class TestFilesOfModel(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model_location = RelSdsOptionType.REL_TMP
        model_name = 'the-model-dir'

        model_checker_symbol_name = 'symbol_that_checks_model'

        contents_cases = [
            test_resources.identical_expected_and_actual(case.name, case.value)
            for case in test_resources.model_contents_cases()
        ]

        # ACT & ASSERT #

        integration_check.CHECKER.check_multi(
            self,
            arguments=fm_args.DirContentsRecursive(
                fms_args.SymbolReference(model_checker_symbol_name)
            ).as_arguments,
            parse_expectation=
            ParseExpectation(
                symbol_references=asrt.matches_singleton_sequence(
                    is_reference_to_files_matcher__ref(model_checker_symbol_name)
                ),
            ),
            model_constructor=
            integration_check.file_in_sds(model_location, model_name),
            execution=[
                NExArr(
                    contents_case.name,
                    ExecutionExpectation(),
                    arrangement_w_tcds(
                        non_hds_contents=sds_populator.contents_in(
                            model_location,
                            DirContents([
                                Dir(model_name, contents_case.actual)
                            ])
                        ),
                        symbols=symbol_utils.symbol_table_from_name_and_sdv_mapping({
                            model_checker_symbol_name:
                                test_resources.model_contents_checker(self, contents_case.expected)
                        })
                    ),
                )
                for contents_case in contents_cases
            ],
        )


class TestConcreteMatcher(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        location = RelSdsOptionType.REL_ACT
        checked_dir_name = 'checked-dir'
        # ACT & ASSERT #
        integration_check.CHECKER.check_multi__w_source_variants(
            self,
            arguments=fm_args.DirContentsRecursive(
                fms_args.Empty()
            ).as_arguments,
            model_constructor=
            integration_check.file_in_sds(location, checked_dir_name),
            symbol_references=asrt.is_empty_sequence,
            execution=[
                NExArr(
                    'checked dir is empty',
                    ExecutionExpectation(
                        main_result=asrt_matching_result.matches_value(True)
                    ),
                    arrangement_w_tcds(
                        non_hds_contents=sds_populator.contents_in(
                            location,
                            DirContents([empty_dir(checked_dir_name)])
                        )
                    ),
                ),
                NExArr(
                    'checked dir is not empty',
                    ExecutionExpectation(
                        main_result=asrt_matching_result.matches_value(False)
                    ),
                    arrangement_w_tcds(
                        non_hds_contents=sds_populator.contents_in(
                            location,
                            DirContents([
                                Dir(checked_dir_name,
                                    [empty_file('file-in-checked-dir')])
                            ])
                        )
                    ),
                ),
            ],
        )
