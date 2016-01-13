from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.execution.phases import CLEANUP
from shellcheck_lib.instructions.multi_phase_instructions import execute
from shellcheck_lib.instructions.utils import sub_process_execution
from shellcheck_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationForSuccessOrHardError, \
    PreOrPostEdsSvhValidationErrorValidator
from shellcheck_lib.test_case.instruction_description import Description
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction, PreviousPhase
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh


def description(instruction_name: str) -> Description:
    return execute.TheDescription(instruction_name,
                                  'Executes a program.')


def parser(instruction_name: str) -> SingleInstructionParser:
    return execute.InstructionParser(sub_process_execution.InstructionMetaInfo(CLEANUP.identifier,
                                                                               instruction_name),
                                     _Instruction)


class _Instruction(CleanupPhaseInstruction):
    def __init__(self,
                 setup: execute.SetupForExecutableWithArguments):
        self.setup = setup

    def validate_pre_eds(self,
                         environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        validator = PreOrPostEdsSvhValidationErrorValidator(self.setup.validator)
        return validator.validate_pre_eds_if_applicable(environment.home_directory)

    def _validate_from_main(
            self,
            environment: GlobalEnvironmentForPostEdsPhase) -> sh.SuccessOrHardError:
        validator = PreOrPostEdsSvhValidationForSuccessOrHardError(self.setup.validator)
        return validator.validate_pre_or_post_eds(environment.home_and_eds)

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             previous_phase: PreviousPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        validation_result = self._validate_from_main(environment)
        if validation_result.is_hard_error:
            return validation_result
        return execute.run_and_return_sh(self.setup, environment.home_and_eds)
