import os
import pathlib
import unittest

from exactly_lib.section_document.syntax import LINE_COMMENT_MARKER
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.act_phase_setups.test_resources import \
    test_validation_for_single_line_source as single_line_source
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration
from exactly_lib_test.act_phase_setups.test_resources.test_validation_for_single_line_source import \
    TestCaseForConfigurationForValidation
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.execution import tmp_dir as fs_utils
from exactly_lib_test.test_resources.programs.python_program_execution import abs_path_to_interpreter_quoted_for_exactly


def suite_for(configuration: Configuration) -> unittest.TestSuite:
    return unittest.TestSuite([
        single_line_source.suite_for(configuration),
        suite_for_additional(configuration)
    ])


def suite_for_additional(conf: Configuration) -> unittest.TestSuite:
    test_cases = [
        test_succeeds_when_there_is_exactly_one_statement_but_surrounded_by_empty_and_comment_lines,
        test_validate_pre_sds_SHOULD_fail_WHEN_statement_line_is_not_an_existing_file_rel_home,
        test_validate_pre_sds_SHOULD_fail_WHEN_statement_line_is_not_an_existing_file__absolute_file_name,
        test_validate_pre_sds_SHOULD_succeed_WHEN_statement_line_is_absolute_name_of_existing_file_not_under_home,
        test_validate_pre_sds_SHOULD_succeed_WHEN_statement_line_is_absolute_name_of_existing_file__and_arguments,
        test_validate_pre_sds_SHOULD_succeed_WHEN_statement_line_is_relative_name_of_an_existing_file_rel_home,
    ]
    return unittest.TestSuite([tc(conf) for tc in test_cases])


class test_succeeds_when_there_is_exactly_one_statement_but_surrounded_by_empty_and_comment_lines(
    TestCaseForConfigurationForValidation):
    def runTest(self):
        existing_file = abs_path_to_interpreter_quoted_for_exactly()
        act_phase_instructions = [instr(['',
                                         '             ',
                                         LINE_COMMENT_MARKER + ' line comment text',
                                         existing_file,
                                         LINE_COMMENT_MARKER + ' line comment text',
                                         ''])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      actual.status,
                      'Validation result')


class test_validate_pre_sds_SHOULD_fail_WHEN_statement_line_is_not_an_existing_file_rel_home(
    TestCaseForConfigurationForValidation):
    def runTest(self):
        act_phase_instructions = [instr(['name-of-non-existing-file'])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')


class test_validate_pre_sds_SHOULD_fail_WHEN_statement_line_is_not_an_existing_file__absolute_file_name(
    TestCaseForConfigurationForValidation):
    def runTest(self):
        absolute_name_of_non_existing_file = str(pathlib.Path().resolve() / 'non' / 'existing' / 'file' / 'oiasdlkv')
        act_phase_instructions = [instr([absolute_name_of_non_existing_file])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')


class test_validate_pre_sds_SHOULD_succeed_WHEN_statement_line_is_absolute_name_of_existing_file_not_under_home(
    TestCaseForConfigurationForValidation):
    def runTest(self):
        existing_file = abs_path_to_interpreter_quoted_for_exactly()
        act_phase_instructions = [instr([existing_file])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      actual.status,
                      'Validation result')


class test_validate_pre_sds_SHOULD_succeed_WHEN_statement_line_is_absolute_name_of_existing_file__and_arguments(
    TestCaseForConfigurationForValidation):
    def runTest(self):
        existing_file = abs_path_to_interpreter_quoted_for_exactly()
        abs_path_and_arguments = ' '.join([existing_file, 'arg1', '"quoted arg"'])
        act_phase_instructions = [instr([abs_path_and_arguments])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      actual.status,
                      'Validation result')


class test_validate_pre_sds_SHOULD_succeed_WHEN_statement_line_is_relative_name_of_an_existing_file_rel_home(
    TestCaseForConfigurationForValidation):
    def runTest(self):
        act_phase_instructions = [instr(['system-under-test'])]
        with fs_utils.tmp_dir(fs.DirContents([fs.empty_file('system-under-test')])) as home_dir_path:
            environment = InstructionEnvironmentForPreSdsStep(home_dir_path, dict(os.environ))
            executor = self.constructor.apply(ACT_PHASE_OS_PROCESS_EXECUTOR, environment, act_phase_instructions)
            actual = executor.validate_pre_sds(environment)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.SUCCESS,
                      actual.status,
                      'Validation result')
