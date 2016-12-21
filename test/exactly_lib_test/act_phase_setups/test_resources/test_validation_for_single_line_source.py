import os
import pathlib
import unittest

from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutorConstructor
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.programs.python_program_execution import abs_path_to_interpreter_quoted_for_exactly


def suite_for(conf: Configuration) -> unittest.TestSuite:
    test_cases = [
        test_fails_when_there_are_no_instructions,
        test_fails_when_there_is_more_than_one_instruction,
        test_fails_when_there_are_no_statements,
        test_fails_when_there_is_more_than_one_statement,
    ]
    return unittest.TestSuite([tc(conf) for tc in test_cases])


class TestCaseForConfigurationForValidation(unittest.TestCase):
    def __init__(self, configuration: Configuration):
        super().__init__()
        self.conf = configuration
        self.constructor = configuration.sut
        assert isinstance(self.constructor, ActSourceAndExecutorConstructor)
        self.home_dir_as_current_dir = pathlib.Path()
        self.pre_sds_env = InstructionEnvironmentForPreSdsStep(self.home_dir_as_current_dir,
                                                               dict(os.environ))

    def runTest(self):
        raise NotImplementedError()

    @staticmethod
    def _new_environment() -> InstructionEnvironmentForPreSdsStep:
        home_dir_path = pathlib.Path()
        return InstructionEnvironmentForPreSdsStep(home_dir_path, dict(os.environ))

    def _do_validate_pre_sds(self, act_phase_instructions: list) -> svh.SuccessOrValidationErrorOrHardError:
        executor = self.constructor.apply(ACT_PHASE_OS_PROCESS_EXECUTOR, self.pre_sds_env, act_phase_instructions)
        return executor.validate_pre_sds(self.pre_sds_env)


class test_fails_when_there_are_no_instructions(TestCaseForConfigurationForValidation):
    def runTest(self):
        act_phase_instructions = []
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')


class test_fails_when_there_is_more_than_one_instruction(TestCaseForConfigurationForValidation):
    def runTest(self):
        act_phase_instructions = [instr(['']),
                                  instr([''])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')


class test_fails_when_there_are_no_statements(TestCaseForConfigurationForValidation):
    def runTest(self):
        act_phase_instructions = [instr([''])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')


class test_fails_when_there_is_more_than_one_statement(TestCaseForConfigurationForValidation):
    def runTest(self):
        existing_file = abs_path_to_interpreter_quoted_for_exactly()
        act_phase_instructions = [instr([existing_file,
                                         existing_file])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')
