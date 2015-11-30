import pathlib

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.execution.phases import CLEANUP
from shellcheck_lib.instructions.multi_phase_instructions import execute
from shellcheck_lib.instructions.utils import sub_process_execution
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh

DESCRIPTION = execute.description("Executes a program")


def parser(instruction_name: str) -> SingleInstructionParser:
    return execute.InstructionParser(sub_process_execution.InstructionMetaInfo(CLEANUP.identifier,
                                                                               instruction_name),
                                     lambda setup: _Instruction(setup))


class _Instruction(CleanupPhaseInstruction):
    def __init__(self,
                 setup: execute.SetupForExecutableWithArguments):
        self.setup = setup

    def pre_eds_validate(self,
                         home_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        error_message = self.setup.executable.validate_pre_eds_if_applicable(home_dir_path)
        if error_message is not None:
            return svh.new_svh_validation_error(error_message)
        return svh.new_svh_success()

    def post_eds_validate(self,
                          eds: ExecutionDirectoryStructure) -> sh.SuccessOrHardError:
        error_message = self.setup.executable.validate_post_eds_if_applicable(eds)
        if error_message is not None:
            return svh.new_svh_validation_error(error_message)
        return svh.new_svh_success()

    def _validate_in_absence_of_validation_step_for_cleanup_phase(
            self,
            environment: GlobalEnvironmentForPostEdsPhase) -> sh.SuccessOrHardError:
        result = self.pre_eds_validate(environment.home_directory)
        if result.is_hard_error:
            return result
        return self.post_eds_validate(environment.eds)

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        validation_result = self._validate_in_absence_of_validation_step_for_cleanup_phase(environment)
        if validation_result.is_hard_error:
            return validation_result
        result_and_err = execute.execute_setup_and_read_stderr_if_non_zero_exitcode(self.setup,
                                                                                    environment.home_and_eds)
        result = result_and_err.result
        if not result.is_success:
            return sh.new_sh_hard_error(result.error_message)
        if result.exit_code != 0:
            return sh.new_sh_hard_error(execute.failure_message_for_nonzero_status(result_and_err))
        return sh.new_sh_success()
