from exactly_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from exactly_lib.instructions.multi_phase_instructions import execute
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationForSuccessOrHardError, \
    PreOrPostEdsSvhValidationErrorValidator
from exactly_lib.test_case.instruction_setup import SingleInstructionSetup
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            parser(instruction_name),
        execute.TheInstructionDocumentation(instruction_name))


def parser(instruction_name: str) -> SingleInstructionParser:
    return execute.InstructionParser(instruction_name,
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
        return execute.run_and_return_sh(self.setup,
                                         environment.home_and_eds,
                                         environment.phase_logging)
