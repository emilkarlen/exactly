from exactly_lib.instructions.utils.main_step_executor import InstructionParts
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationErrorValidator
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
        return self._validator.validate_pre_eds_if_applicable(environment.home_directory)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             previous_phase: PreviousPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return self.setup.executor.apply_sh(environment,
                                            self.logging_paths(environment.sds),
                                            os_services)
