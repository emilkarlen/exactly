from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.execution.phases import SETUP
from shellcheck_lib.instructions.multi_phase_instructions import execute
from shellcheck_lib.instructions.utils import sub_process_execution
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder

DESCRIPTION = execute.description("Executes a program")


def parser(instruction_name: str) -> SingleInstructionParser:
    return execute.InstructionParser(sub_process_execution.InstructionMetaInfo(SETUP.name,
                                                                               instruction_name),
                                     lambda setup: _Instruction(setup))


class _Instruction(SetupPhaseInstruction):
    def __init__(self,
                 setup: execute.Setup):
        self.setup = setup

    def pre_validate(self,
                     global_environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        error_message = self.setup.executable.validate_pre_eds_if_applicable(global_environment.home_directory)
        if error_message is not None:
            return svh.new_svh_validation_error(error_message)
        return svh.new_svh_success()

    def validate(self, environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        error_message = self.setup.executable.validate_post_eds_if_applicable(environment.eds)
        if error_message is not None:
            return svh.new_svh_validation_error(error_message)
        return svh.new_svh_success()

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        result_and_err = execute.execute_setup_and_read_stderr_if_non_zero_exitcode(self.setup,
                                                                                    environment.home_and_eds)
        result = result_and_err.result
        if not result.is_success:
            return sh.new_sh_hard_error(result.error_message)
        if result.exit_code != 0:
            return sh.new_sh_hard_error(execute.failure_message_for_nonzero_status(result_and_err))
        return sh.new_sh_success()
