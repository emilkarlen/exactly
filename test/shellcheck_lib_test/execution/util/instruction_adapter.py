from shellcheck_lib.document.model import Instruction
from shellcheck_lib.execution import phases
from shellcheck_lib.test_case.sections.common import GlobalEnvironmentForPostEdsPhase
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections import common as instr
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder


class InternalInstruction(Instruction):
    """
    Abstract base class for instructions that are implemented in python.
    """

    def execute(self,
                phase_name: str,
                global_environment: GlobalEnvironmentForPostEdsPhase,
                phase_environment: OsServices):
        """
        Does whatever this instruction should do.
        :param phase_name The phase in which this instruction is in.
        :param global_environment An object passed to all instructions in the Document.
        :param phase_environment An object passed to all instructions in the Phase.
        """
        raise NotImplementedError()


def as_setup(internal_instruction: InternalInstruction) -> SetupPhaseInstruction:
    return _SetupInstructionExecutor(internal_instruction)


def as_assert(internal_instruction: InternalInstruction) -> AssertPhaseInstruction:
    return _AssertInstructionExecutor(internal_instruction)


def as_cleanup(internal_instruction: InternalInstruction) -> CleanupPhaseInstruction:
    return _CleanupInstructionExecutor(internal_instruction)


class _SetupInstructionExecutor(SetupPhaseInstruction):
    def __init__(self,
                 internal_instruction: InternalInstruction,
                 ret_val: sh.SuccessOrHardError=sh.new_sh_success()):
        self.__internal_instruction = internal_instruction
        self.__ret_val = ret_val

    def pre_validate(self,
                     global_environment: instr.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             os_services: OsServices,
             environment: instr.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        self.__internal_instruction.execute(phases.SETUP.name,
                                            environment,
                                            OsServices())
        return self.__ret_val

    def post_validate(self,
                      global_environment: instr.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()


class _AssertInstructionExecutor(AssertPhaseInstruction):
    def __init__(self,
                 internal_instruction: InternalInstruction,
                 ret_val: pfh.PassOrFailOrHardError=pfh.new_pfh_pass()):
        self.__internal_instruction = internal_instruction
        self.__ret_val = ret_val

    def validate(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: instr.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        self.__internal_instruction.execute(phases.ASSERT.name,
                                            environment,
                                            os_services)
        return self.__ret_val


class _CleanupInstructionExecutor(CleanupPhaseInstruction):
    def __init__(self,
                 internal_instruction: InternalInstruction,
                 ret_val: sh.SuccessOrHardError=sh.new_sh_success()):
        self.__internal_instruction = internal_instruction
        self.__ret_val = ret_val

    def main(self,
             environment: instr.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        self.__internal_instruction.execute(phases.CLEANUP.name,
                                            environment,
                                            os_services)
        return self.__ret_val
