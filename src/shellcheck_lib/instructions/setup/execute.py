from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.execution.phases import SETUP
from shellcheck_lib.instructions.multi_phase_instructions import execute
from shellcheck_lib.instructions.utils import sub_process_execution
from shellcheck_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationErrorValidator
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            parser(instruction_name),
            execute.TheDescription(instruction_name,
                                   'Executes a program.'))


def parser(instruction_name: str) -> SingleInstructionParser:
    return execute.InstructionParser(sub_process_execution.InstructionMetaInfo(SETUP.identifier,
                                                                               instruction_name),
                                     lambda setup: _Instruction(setup))


class _Instruction(SetupPhaseInstruction):
    def __init__(self,
                 setup: execute.SetupForExecutableWithArguments):
        self.setup = setup
        self.svh_validator = PreOrPostEdsSvhValidationErrorValidator(setup.validator)

    def validate_pre_eds(self,
                         environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self.svh_validator.validate_pre_eds_if_applicable(environment.home_directory)

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        failure_message = self.setup.validator.validate_post_eds_if_applicable(environment.eds)
        if failure_message is not None:
            return sh.new_sh_hard_error(failure_message)
        return execute.run_and_return_sh(self.setup, environment.home_and_eds)
