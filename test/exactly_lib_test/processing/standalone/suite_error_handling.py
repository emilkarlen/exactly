import unittest
from pathlib import Path
from typing import Optional

from exactly_lib.definitions.entity.directives import INCLUDING_DIRECTIVE_INFO
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.definitions.test_suite import file_names, section_names
from exactly_lib.processing import exit_values
from exactly_lib.processing.standalone import processor as sut
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings, ReportingOption
from exactly_lib.util.string import lines_content
from exactly_lib_test.processing.standalone.test_resources.run_processor import capture_output_from_processor
from exactly_lib_test.processing.test_resources.test_case_setup import \
    test_case_definition_with_only_assert_phase_instructions, setup_with_null_act_phase_and_null_preprocessing
from exactly_lib_test.test_case.actor.test_resources.act_phase_os_process_executor import \
    AtcOsProcessExecutorThatJustReturnsConstant
from exactly_lib_test.test_resources.files.file_structure import DirContents, File, empty_file
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions.process_result_assertions import is_result_for_exit_value
from exactly_lib_test.test_suite.test_resources.test_suite_definition import configuration_section_parser


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSyntaxErrorInSuiteFile),
        unittest.makeSuite(TestFileInclusionErrorInSuiteFile),
        unittest.makeSuite(TestReferenceToNonExistingTestCaseFileInSuiteShouldBeIgnored),
    ])


class TestSyntaxErrorInSuiteFile(unittest.TestCase):
    def test_explicit_suite_to_run_as_part_of(self):
        suite_file_path = Path('test.suite')

        self._run(suite_file_name=str(suite_file_path),
                  run_as_part_of_explicit_suite=suite_file_path)

    def test_implicit_default_suite_to_run_as_part_of(self):
        self._run(suite_file_name=file_names.DEFAULT_SUITE_FILE,
                  run_as_part_of_explicit_suite=None)

    def _run(self,
             suite_file_name: str,
             run_as_part_of_explicit_suite: Optional[Path]):
        # ARRANGE #

        default_test_case_handling = setup_with_null_act_phase_and_null_preprocessing()

        conf_parser_with_no_instructions = configuration_section_parser({})

        test_case_definition = test_case_definition_with_only_assert_phase_instructions([])

        case_file = empty_file('test.case')

        suite_file = File(suite_file_name,
                          lines_content([SectionName('this_is_not_a_suite_section').syntax]))

        suite_and_case_files = DirContents([suite_file,
                                            case_file,
                                            ])

        processor = sut.Processor(test_case_definition,
                                  AtcOsProcessExecutorThatJustReturnsConstant(),
                                  conf_parser_with_no_instructions)

        with tmp_dir_as_cwd(suite_and_case_files) as tmp_dir:
            execution_settings = TestCaseExecutionSettings(case_file.name_as_path,
                                                           tmp_dir,
                                                           ReportingOption.STATUS_CODE,
                                                           default_test_case_handling,
                                                           run_as_part_of_explicit_suite=run_as_part_of_explicit_suite)
            # ACT #
            actual_result = capture_output_from_processor(processor,
                                                          execution_settings)

        # ASSERT #

        expectation = is_result_for_exit_value(exit_values.NO_EXECUTION__SYNTAX_ERROR)
        expectation.apply_without_message(self, actual_result)


class TestFileInclusionErrorInSuiteFile(unittest.TestCase):
    def test_explicit_suite_to_run_as_part_of(self):
        suite_file_path = Path('test.suite')

        self._run(suite_file_name=str(suite_file_path),
                  run_as_part_of_explicit_suite=suite_file_path)

    def test_implicit_default_suite_to_run_as_part_of(self):
        self._run(suite_file_name=file_names.DEFAULT_SUITE_FILE,
                  run_as_part_of_explicit_suite=None)

    def _run(self,
             suite_file_name: str,
             run_as_part_of_explicit_suite: Optional[Path]):
        # ARRANGE #

        default_test_case_handling = setup_with_null_act_phase_and_null_preprocessing()

        conf_parser_with_no_instructions = configuration_section_parser({})

        test_case_definition = test_case_definition_with_only_assert_phase_instructions([])

        case_file = empty_file('test.case')

        suite_file = File(suite_file_name,
                          lines_content([
                              phase_names.ASSERT.syntax,
                              ' '.join([
                                  INCLUDING_DIRECTIVE_INFO.singular_name,
                                  'non-existing-file.txt'
                              ]),
                          ]))

        suite_and_case_files = DirContents([suite_file,
                                            case_file,
                                            ])

        processor = sut.Processor(test_case_definition,
                                  AtcOsProcessExecutorThatJustReturnsConstant(),
                                  conf_parser_with_no_instructions)

        with tmp_dir_as_cwd(suite_and_case_files) as tmp_dir:
            execution_settings = TestCaseExecutionSettings(case_file.name_as_path,
                                                           tmp_dir,
                                                           ReportingOption.STATUS_CODE,
                                                           default_test_case_handling,
                                                           run_as_part_of_explicit_suite=run_as_part_of_explicit_suite)
            # ACT #
            actual_result = capture_output_from_processor(processor,
                                                          execution_settings)

        # ASSERT #

        expectation = is_result_for_exit_value(exit_values.NO_EXECUTION__FILE_ACCESS_ERROR)
        expectation.apply_without_message(self, actual_result)


class TestReferenceToNonExistingTestCaseFileInSuiteShouldBeIgnored(unittest.TestCase):
    def test_explicit_suite_to_run_as_part_of(self):
        suite_file_path = Path('test.suite')

        self._run(suite_file_name=str(suite_file_path),
                  run_as_part_of_explicit_suite=suite_file_path)

    def test_implicit_default_suite_to_run_as_part_of(self):
        self._run(suite_file_name=file_names.DEFAULT_SUITE_FILE,
                  run_as_part_of_explicit_suite=None)

    def _run(self,
             suite_file_name: str,
             run_as_part_of_explicit_suite: Optional[Path]):
        # ARRANGE #

        default_test_case_handling = setup_with_null_act_phase_and_null_preprocessing()

        conf_parser_with_no_instructions = configuration_section_parser({})

        test_case_definition = test_case_definition_with_only_assert_phase_instructions([])

        case_file = empty_file('test.case')

        suite_file = File(suite_file_name,
                          lines_content([
                              section_names.CASES.syntax,
                              'non-existing-test.case',
                          ]))

        suite_and_case_files = DirContents([suite_file,
                                            case_file,
                                            ])

        processor = sut.Processor(test_case_definition,
                                  AtcOsProcessExecutorThatJustReturnsConstant(),
                                  conf_parser_with_no_instructions)

        with tmp_dir_as_cwd(suite_and_case_files) as tmp_dir:
            execution_settings = TestCaseExecutionSettings(case_file.name_as_path,
                                                           tmp_dir,
                                                           ReportingOption.STATUS_CODE,
                                                           default_test_case_handling,
                                                           run_as_part_of_explicit_suite=run_as_part_of_explicit_suite)
            # ACT #
            actual_result = capture_output_from_processor(processor,
                                                          execution_settings)

        # ASSERT #

        expectation = is_result_for_exit_value(exit_values.EXECUTION__PASS)
        expectation.apply_without_message(self, actual_result)
