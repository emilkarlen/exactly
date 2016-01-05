from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.execution.phases import ASSERT
from shellcheck_lib.instructions.multi_phase_instructions import execute
from shellcheck_lib.instructions.utils import sub_process_execution
from shellcheck_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationErrorValidator
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import svh


def description(instruction_name: str) -> Description:
    return execute.TheDescription(instruction_name,
                                  "Executes a program and succeeds if it's exit-code is 0.")


def parser(instruction_name: str) -> SingleInstructionParser:
    return execute.InstructionParser(sub_process_execution.InstructionMetaInfo(ASSERT.identifier,
                                                                               instruction_name),
                                     lambda setup: _Instruction(setup))


class _Instruction(AssertPhaseInstruction):
    def __init__(self,
                 setup: execute.SetupForExecutableWithArguments):
        self.setup = setup
        self.validator = PreOrPostEdsSvhValidationErrorValidator(setup.validator)

    def validate_post_setup(self,
                            environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return self.validator.validate_pre_or_post_eds(environment.home_and_eds)

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        result_and_err = execute.execute_setup_and_read_stderr_if_non_zero_exitcode(self.setup,
                                                                                    environment.home_and_eds)
        result = result_and_err.result
        if not result.is_success:
            return pfh.new_pfh_hard_error(result.error_message)
        if result.exit_code != 0:
            return pfh.new_pfh_fail(execute.failure_message_for_nonzero_status(result_and_err))
        return pfh.new_pfh_pass()
