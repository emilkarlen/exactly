import pathlib

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.execution.phases import CLEANUP
from shellcheck_lib.instructions.multi_phase_instructions import execute
from shellcheck_lib.instructions.utils import sub_process_execution
from shellcheck_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationForSuccessOrHardError
from shellcheck_lib.test_case.help.instruction_description import Description
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.sections.result import sh


def description(instruction_name: str) -> Description:
    return execute.TheDescription(instruction_name,
                                  'Executes a program.')


def parser(instruction_name: str) -> SingleInstructionParser:
    return execute.InstructionParser(sub_process_execution.InstructionMetaInfo(CLEANUP.identifier,
                                                                               instruction_name),
                                     lambda setup: _Instruction(setup))


class _Instruction(CleanupPhaseInstruction):
    def __init__(self,
                 setup: execute.SetupForExecutableWithArguments):
        self.setup = setup
        self.validator = PreOrPostEdsSvhValidationForSuccessOrHardError(self.setup.validator)

    def pre_eds_validate(self,
                         home_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        return self.validator.validate_pre_eds_if_applicable(home_dir_path)

    def post_eds_validate(self,
                          eds: ExecutionDirectoryStructure) -> sh.SuccessOrHardError:
        return self.validator.validate_post_eds_if_applicable(eds)

    def _validate_in_absence_of_validation_step_for_cleanup_phase(
            self,
            environment: GlobalEnvironmentForPostEdsPhase) -> sh.SuccessOrHardError:
        return self.validator.validate_pre_or_post_eds(environment.home_and_eds)

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
