import os
import pathlib
import unittest

from exactly_lib.act_phase_setups import command_line as sut
from exactly_lib.test_case.os_services import ACT_PHASE_OS_PROCESS_EXECUTOR
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import svh
from exactly_lib_test.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.programs.python_program_execution import abs_path_to_interpreter_quoted_for_exactly


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestValidation))
    return ret_val


class TestValidation(unittest.TestCase):
    def __init__(self, method_name):
        super().__init__(method_name)
        self.constructor = sut.Constructor()
        self.home_dir_as_current_dir = pathlib.Path()
        self.pre_sds_env = InstructionEnvironmentForPreSdsStep(self.home_dir_as_current_dir, dict(os.environ))

    def test_fails_when_there_are_no_instructions(self):
        act_phase_instructions = []
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')

    def test_fails_when_there_is_more_than_one_instruction(self):
        act_phase_instructions = [instr(['']),
                                  instr([''])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')

    def test_fails_when_there_are_no_statements(self):
        act_phase_instructions = [instr([''])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')

    def test_fails_when_there_is_more_than_one_statement(self):
        existing_file = abs_path_to_interpreter_quoted_for_exactly()
        act_phase_instructions = [instr([existing_file,
                                         existing_file])]
        actual = self._do_validate_pre_sds(act_phase_instructions)
        self.assertIs(svh.SuccessOrValidationErrorOrHardErrorEnum.VALIDATION_ERROR,
                      actual.status,
                      'Validation result')

    @staticmethod
    def _new_environment() -> InstructionEnvironmentForPreSdsStep:
        home_dir_path = pathlib.Path()
        return InstructionEnvironmentForPreSdsStep(home_dir_path, dict(os.environ))

    def _do_validate_pre_sds(self, act_phase_instructions: list) -> svh.SuccessOrValidationErrorOrHardError:
        executor = self.constructor.apply(ACT_PHASE_OS_PROCESS_EXECUTOR, self.pre_sds_env, act_phase_instructions)
        return executor.validate_pre_sds(self.pre_sds_env)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
