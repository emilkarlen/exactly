from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions import run
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationForSuccessOrHardError, \
    PreOrPostEdsSvhValidationErrorValidator
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        parser(instruction_name),
        run.TheInstructionDocumentation(instruction_name,
                                        description_rest_text=run.NON_ASSERT_PHASE_DESCRIPTION_REST))


def parser(instruction_name: str) -> SingleInstructionParser:
    return run.InstructionParser(instruction_name,
                                 _Instruction)


class _Instruction(CleanupPhaseInstruction):
    def __init__(self,
                 setup: run.SetupForExecutableWithArguments):
        self.setup = setup

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        validator = PreOrPostEdsSvhValidationErrorValidator(self.setup.validator)
        return validator.validate_pre_eds_if_applicable(environment.home_directory)

    def _validate_from_main(
            self,
            environment: InstructionEnvironmentForPostSdsStep) -> sh.SuccessOrHardError:
        validator = PreOrPostEdsSvhValidationForSuccessOrHardError(self.setup.validator)
        return validator.validate_pre_or_post_eds(environment.home_and_sds)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             previous_phase: PreviousPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        validation_result = self._validate_from_main(environment)
        if validation_result.is_hard_error:
            return validation_result
        return run.run_and_return_sh(self.setup,
                                     environment.home_and_sds,
                                     environment.phase_logging)
