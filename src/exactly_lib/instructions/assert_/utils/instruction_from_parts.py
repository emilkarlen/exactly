from exactly_lib.instructions.utils.instruction_parts import InstructionParts, \
    InstructionInfoForConstructingAnInstructionFromParts
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationErrorValidator
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import svh


class AssertPhaseInstructionFromValidatorAndExecutor(AssertPhaseInstruction):
    def __init__(self,
                 instruction_setup: InstructionParts):
        self.setup = instruction_setup
        self._validator = PreOrPostEdsSvhValidationErrorValidator(instruction_setup.validator)

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validator.validate_pre_eds_if_applicable(environment.home_directory)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self._validator.validate_post_eds_if_applicable(environment.sds)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return self.setup.executor.apply_as_assertion(environment,
                                                      self.logging_paths(environment.sds),
                                                      os_services)


def instruction_info_for(instruction_name: str) -> InstructionInfoForConstructingAnInstructionFromParts:
    return InstructionInfoForConstructingAnInstructionFromParts(instruction_name,
                                                                AssertPhaseInstructionFromValidatorAndExecutor)
