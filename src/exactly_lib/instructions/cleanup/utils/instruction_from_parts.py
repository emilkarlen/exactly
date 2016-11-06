from exactly_lib.instructions.utils.instruction_parts import InstructionParts, \
    InstructionInfoForConstructingAnInstructionFromParts
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationErrorValidator, \
    PreOrPostEdsSvhValidationForSuccessOrHardError
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh


class CleanupPhaseInstructionFromValidatorAndExecutor(CleanupPhaseInstruction):
    def __init__(self,
                 instruction_setup: InstructionParts):
        self.setup = instruction_setup
        self._validator = PreOrPostEdsSvhValidationErrorValidator(instruction_setup.validator)

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        validator = PreOrPostEdsSvhValidationErrorValidator(self.setup.validator)
        return validator.validate_pre_eds_if_applicable(environment.home_directory)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             previous_phase: PreviousPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        validation_result = self._validate_from_main(environment)
        if validation_result.is_hard_error:
            return validation_result
        return self.setup.executor.apply_as_non_assertion(environment,
                                                          self.logging_paths(environment.sds),
                                                          os_services)

    def _validate_from_main(
            self,
            environment: InstructionEnvironmentForPostSdsStep) -> sh.SuccessOrHardError:
        validator = PreOrPostEdsSvhValidationForSuccessOrHardError(self.setup.validator)
        return validator.validate_pre_or_post_eds(environment.home_and_sds)


def instruction_info_for(instruction_name: str) -> InstructionInfoForConstructingAnInstructionFromParts:
    return InstructionInfoForConstructingAnInstructionFromParts(instruction_name,
                                                                CleanupPhaseInstructionFromValidatorAndExecutor)
