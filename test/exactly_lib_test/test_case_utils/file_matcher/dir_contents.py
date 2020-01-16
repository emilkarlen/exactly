import unittest

from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.test_case_file_structure.path_relativity import RelSdsOptionType
from exactly_lib_test.symbol.test_resources import symbol_utils
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref
from exactly_lib_test.test_case_file_structure.test_resources import sds_populator
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.files_matcher.test_resources import arguments_building as fms_args
from exactly_lib_test.test_case_utils.files_matcher.test_resources import validation_cases
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.matcher.test_resources.integration_check import arrangement_w_tcds, Expectation, \
    ExecutionExpectation, ParseExpectation, arrangement_wo_tcds
from exactly_lib_test.test_resources.files.file_structure import empty_file, DirContents, empty_dir, Dir
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.trace.test_resources import matching_result_assertions as asrt_matching_result


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestFilesMatcherShouldBeValidated(),
        unittest.makeSuite(TestHardError),
        TestApplication(),
        TestConcreteMatcher(),
    ])


class TestFilesMatcherShouldBeValidated(unittest.TestCase):
    def runTest(self):
        for case in validation_cases.failing_validation_cases():
            symbol_context = case.value.symbol_context
            symbols = symbol_context.symbol_table

            with self.subTest(case.name):
                integration_check.CHECKER.check_with_source_variants(
                    self,
                    arguments=
                    fm_args.DirContents(fms_args.SymbolReference(symbol_context.name)).as_arguments,
                    model_constructor=
                    integration_check.constant_relative_file_name('arbitrary-file-argument'),
                    arrangement=
                    arrangement_wo_tcds(
                        symbols=symbols,
                    ),
                    expectation=
                    Expectation(
                        ParseExpectation(
                            symbol_references=symbol_context.references_assertion,
                        ),
                        ExecutionExpectation(
                            validation=case.value.expectation,
                        ),
                    ),
                )


class TestHardError(unittest.TestCase):
    UNCONDITIONALLY_CONSTANT_TRUE = NameAndValue(
        'unconditionally_constant_true',
        FilesMatcherSdv(
            matchers.sdv_from_bool(True)
        )
    )

    def test_WHEN_file_does_not_exist(self):
        integration_check.CHECKER.check_with_source_variants(
            self,
            arguments=fm_args.DirContents(
                fms_args.SymbolReference(self.UNCONDITIONALLY_CONSTANT_TRUE.name)
            ).as_arguments,
            model_constructor=
            integration_check.constant_relative_file_name('non-existing-file'),
            arrangement=
            arrangement_w_tcds(
                symbols=symbol_utils.symbol_table_from_name_and_sdvs([self.UNCONDITIONALLY_CONSTANT_TRUE]),
            ),
            expectation=
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_singleton_sequence(
                        is_reference_to_files_matcher__ref(self.UNCONDITIONALLY_CONSTANT_TRUE.name)
                    )
                ),
                ExecutionExpectation(
                    is_hard_error=asrt.anything_goes()
                ),
            ),
        )

    def test_WHEN_file_is_not_a_directory(self):
        actual_regular_file = empty_file('regular-file')

        file_location = RelSdsOptionType.REL_ACT
        integration_check.CHECKER.check_with_source_variants(
            self,
            arguments=fm_args.DirContents(
                fms_args.SymbolReference(self.UNCONDITIONALLY_CONSTANT_TRUE.name)
            ).as_arguments,
            model_constructor=
            integration_check.file_in_sds(file_location, actual_regular_file.name),
            arrangement=
            arrangement_w_tcds(
                symbols=symbol_utils.symbol_table_from_name_and_sdvs([self.UNCONDITIONALLY_CONSTANT_TRUE]),
                non_hds_contents=sds_populator.contents_in(
                    file_location,
                    DirContents([actual_regular_file]),
                ),
            ),
            expectation=
            Expectation(
                ParseExpectation(
                    symbol_references=asrt.matches_singleton_sequence(
                        is_reference_to_files_matcher__ref(self.UNCONDITIONALLY_CONSTANT_TRUE.name)
                    )
                ),
                ExecutionExpectation(
                    is_hard_error=asrt.anything_goes()
                ),
            ),
        )


class TestApplication(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        files_matcher_name = 'the_files_matcher'
        checked_dir_location = RelSdsOptionType.REL_TMP
        checked_dir = empty_dir('checked-dir')

        # ACT & ASSERT #

        integration_check.CHECKER.check_multi_execution(
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
                        })
                    ),
                )
                for matcher_result in [False, True]
            ],
        )


class TestConcreteMatcher(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        location = RelSdsOptionType.REL_ACT
        checked_dir_name = 'checked-dir'
        # ACT & ASSERT #
        integration_check.CHECKER.check_multi_execution(
            self,
            arguments=fm_args.DirContents(
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
