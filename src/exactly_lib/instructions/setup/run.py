from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions import run
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationErrorValidator
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        parser(instruction_name),
        run.TheInstructionDocumentation(instruction_name,
                                        description_rest_text=run.NON_ASSERT_PHASE_DESCRIPTION_REST))


def parser(instruction_name: str) -> SingleInstructionParser:
    return run.InstructionParser(instruction_name,
                                 lambda setup: _Instruction(setup))


class _Instruction(SetupPhaseInstruction):
    def __init__(self,
                 setup: run.SetupForExecutableWithArguments):
        self.setup = setup
        self.svh_validator = PreOrPostEdsSvhValidationErrorValidator(setup.validator)

    def validate_pre_eds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self.svh_validator.validate_pre_eds_if_applicable(environment.home_directory)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        failure_message = self.setup.validator.validate_post_eds_if_applicable(environment.eds)
        if failure_message is not None:
            return sh.new_sh_hard_error(failure_message)
        return run.run_and_return_sh(self.setup,
                                     environment.home_and_eds,
                                     environment.phase_logging)
