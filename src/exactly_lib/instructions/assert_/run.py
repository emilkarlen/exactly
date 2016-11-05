from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.instructions.multi_phase_instructions import run
from exactly_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationErrorValidator
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    InstructionEnvironmentForPreSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import svh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        parser(instruction_name),
        run.TheInstructionDocumentation(instruction_name,
                                            "Runs a program and PASS if, and only if, its exit code is 0"))


def parser(instruction_name: str) -> SingleInstructionParser:
    return run.InstructionParser(instruction_name,
                                 lambda setup: _Instruction(setup))


class _Instruction(AssertPhaseInstruction):
    def __init__(self,
                 setup: run.SetupForExecutableWithArguments):
        self.setup = setup
        self.validator = PreOrPostEdsSvhValidationErrorValidator(setup.validator)

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self.validator.validate_pre_eds_if_applicable(environment.home_directory)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self.validator.validate_post_eds_if_applicable(environment.sds)

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return run.run_and_return_pfh(self.setup,
                                      environment.home_and_sds,
                                      environment.phase_logging)
