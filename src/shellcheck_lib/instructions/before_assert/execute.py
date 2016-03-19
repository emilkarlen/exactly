from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser
from shellcheck_lib.instructions.multi_phase_instructions import execute
from shellcheck_lib.instructions.utils.pre_or_post_validation import PreOrPostEdsSvhValidationErrorValidator
from shellcheck_lib.test_case.instruction_setup import SingleInstructionSetup
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from shellcheck_lib.test_case.phases.common import GlobalEnvironmentForPostEdsPhase, GlobalEnvironmentForPreEdsStep
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.test_case.phases.result import svh


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
            parser(instruction_name),
        execute.TheInstructionReference(instruction_name,
                                   'Executes a program.'))


def parser(instruction_name: str) -> SingleInstructionParser:
    return execute.InstructionParser(instruction_name,
                                     lambda setup: _Instruction(setup))


class _Instruction(BeforeAssertPhaseInstruction):
    def __init__(self,
                 setup: execute.SetupForExecutableWithArguments):
        self.setup = setup
        self.validator = PreOrPostEdsSvhValidationErrorValidator(setup.validator)

    def validate_pre_eds(self,
                         environment: GlobalEnvironmentForPreEdsStep) -> svh.SuccessOrValidationErrorOrHardError:
        return self.validator.validate_pre_eds_if_applicable(environment.home_directory)

    def validate_post_setup(self,
                            environment: GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        return self.validator.validate_post_eds_if_applicable(environment.eds)

    def main(self,
             environment: GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return execute.run_and_return_sh(self.setup,
                                         environment.home_and_eds,
                                         environment.phase_logging)
