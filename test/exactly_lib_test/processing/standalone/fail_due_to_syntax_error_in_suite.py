import unittest

from exactly_lib.definitions.test_case import phase_names
from exactly_lib.processing import exit_values
from exactly_lib.processing.standalone import processor as sut
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings, ReportingOption
from exactly_lib.util.string import lines_content
from exactly_lib_test.processing.standalone.test_resources.run_processor import capture_output_from_processor
from exactly_lib_test.processing.test_resources.test_case_setup import \
    test_case_definition_with_only_assert_phase_instructions, setup_with_null_act_phase_and_null_preprocessing
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_phase_os_process_executor import \
    ActPhaseOsProcessExecutorThatJustReturnsConstant
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.files.tmp_dir import tmp_dir_as_cwd
from exactly_lib_test.test_resources.value_assertions.process_result_assertions import is_result_for_exit_value
from exactly_lib_test.test_suite.test_resources.test_suite_definition import configuration_section_parser


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSyntaxErrorInSuiteFile(),
    ])


class TestSyntaxErrorInSuiteFile(unittest.TestCase):
    def runTest(self):
        default_test_case_handling = setup_with_null_act_phase_and_null_preprocessing()

        conf_parser_with_no_instructions = configuration_section_parser({})

        test_case_definition = test_case_definition_with_only_assert_phase_instructions([])

        case_file = File('test.case',
                         source_with_single_act_phase_instruction('act-phase-content-that-should-be-ignored')
                         )

        suite_file = File('test.suite', '[this_is_not_a_suite_section]\n')

        suite_and_case_files = DirContents([suite_file,
                                            case_file,
                                            ])

        processor = sut.Processor(test_case_definition,
                                  ActPhaseOsProcessExecutorThatJustReturnsConstant(),
                                  conf_parser_with_no_instructions)

        with tmp_dir_as_cwd(suite_and_case_files) as tmp_dir:
            execution_settings = TestCaseExecutionSettings(case_file.name_as_path,
                                                           tmp_dir,
                                                           ReportingOption.STATUS_CODE,
                                                           default_test_case_handling,
                                                           run_as_part_of_explicit_suite=suite_file.name_as_path)
            # ACT #
            actual_result = capture_output_from_processor(processor,
                                                          execution_settings)
        # ASSERT #
        expectation = is_result_for_exit_value(exit_values.NO_EXECUTION__SYNTAX_ERROR)
        expectation.apply_without_message(self, actual_result)


def source_with_single_act_phase_instruction(instruction: str) -> str:
    return lines_content([
        phase_names.ACT.syntax,
        instruction,
    ])
