from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.execution.phases import SETUP
from shellcheck_lib.instructions.multi_phase_instructions import execute
from shellcheck_lib.instructions.utils import sub_process_execution
from shellcheck_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationErrorValidator
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder


def description(instruction_name: str) -> Description:
    return execute.TheDescription(instruction_name,
                                  'Executes a program.')


def parser(instruction_name: str) -> SingleInstructionParser:
    return execute.InstructionParser(sub_process_execution.InstructionMetaInfo(SETUP.identifier,
                                                                               instruction_name),
                                     lambda setup: _Instruction(setup))


class _Instruction(SetupPhaseInstruction):
    def __init__(self,
                 setup: execute.SetupForExecutableWithArguments):
        self.setup = setup
        self.svh_validator = PreOrPostEdsSvhValidationErrorValidator(setup.validator)

    def pre_validate(self,
                     global_environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self.svh_validator.validate_pre_eds_if_applicable(global_environment.home_directory)

    def validate(self, environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return self.svh_validator.validate_post_eds_if_applicable(environment.eds)

    def main(self,
             os_services: OsServices,
             environment: GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        failure_message = self.setup.validator.validate_post_eds_if_applicable(environment.eds)
        if failure_message is not None:
            return sh.new_sh_hard_error(failure_message)
        result_and_err = execute.execute_setup_and_read_stderr_if_non_zero_exitcode(self.setup,
                                                                                    environment.home_and_eds)
        result = result_and_err.result
        if not result.is_success:
            return sh.new_sh_hard_error(result.error_message)
        if result.exit_code != 0:
            return sh.new_sh_hard_error(execute.failure_message_for_nonzero_status(result_and_err))
        return sh.new_sh_success()
