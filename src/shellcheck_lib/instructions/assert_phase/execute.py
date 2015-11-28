import os

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.execution.phases import ASSERT
from shellcheck_lib.instructions.multi_phase_instructions import execute
from shellcheck_lib.instructions.utils import sub_process_execution
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh

DESCRIPTION = execute.description("Executes a program and succeeds if it's exit-code is 0")


def parser(instruction_name: str) -> SingleInstructionParser:
    return execute.InstructionParser(sub_process_execution.InstructionMetaInfo(ASSERT.name,
                                                                               instruction_name),
                                     lambda setup: _Instruction(setup))


class _Instruction(AssertPhaseInstruction):
    def __init__(self,
                 setup: execute.Setup):
        self.setup = setup

    def validate(self, environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        error_message = self.setup.executable.validate_pre_or_post_eds(environment.home_and_eds)
        if error_message is not None:
            return svh.new_svh_validation_error(error_message)
        return svh.new_svh_success()

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        result_and_err = execute.execute_setup_and_read_stderr_if_non_zero_exitcode(self.setup,
                                                                                    environment.home_and_eds)
        result = result_and_err.result
        if not result.is_success:
            return pfh.new_pfh_hard_error(result.error_message)
        if result.exit_code != 0:
            msg_tail = ''
            if result_and_err.stderr_contents:
                msg_tail = os.linesep + result_and_err.stderr_contents
            return pfh.new_pfh_fail('Exit code {}{}'.format(result.exit_code, msg_tail))
        return pfh.new_pfh_pass()
