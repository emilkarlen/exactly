from shelltest.test_case.instructions import PassOrFailOrHardErrorEnum
from shelltest.execution.single_instruction_executor import ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum
from shelltest.test_case import instructions as instr


def _from_success_or_validation_error_or_hard_error(res: instr.SuccessOrValidationErrorOrHardError) \
        -> PartialInstructionControlledFailureInfo:
    if res.is_success:
        return None
    elif res.is_validation_error:
        return PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.VALIDATION,
                                                       res.failure_message)
    else:
        return PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.HARD_ERROR,
                                                       res.failure_message)


def _from_success_or_hard_error(res: instr.SuccessOrHardError) -> PartialInstructionControlledFailureInfo:
    return None \
        if res.is_success \
        else PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.HARD_ERROR,
                                                     res.failure_message)


def _from_pass_or_fail_or_hard_error(res: instr.PassOrFailOrHardError) -> PartialInstructionControlledFailureInfo:
    if res.status is PassOrFailOrHardErrorEnum.PASS:
        return None
    else:
        return PartialInstructionControlledFailureInfo(PartialControlledFailureEnum(res.status.value),
                                                       res.failure_message)


class AnonymousPhaseInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 phase_environment: instr.PhaseEnvironmentForAnonymousPhase):
        self.__phase_environment = phase_environment
        self.__global_environment = ()

    def apply(self, instruction: instr.AnonymousPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.main(self.__global_environment,
                                self.__phase_environment))


class SetupPreValidateInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPreEdsStep):
        self.__global_environment = global_environment

    def apply(self, instruction: instr.SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.pre_validate(self.__global_environment))


class SetupPostValidateInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase):
        self.__global_environment = global_environment

    def apply(self, instruction: instr.SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.post_validate(self.__global_environment))


class SetupPhaseInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase,
                 phase_environment: instr.PhaseEnvironmentForInternalCommands):
        self.__global_environment = global_environment
        self.__phase_environment = phase_environment

    def apply(self, instruction: instr.SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.main(self.__global_environment,
                                self.__phase_environment))


class ActValidateInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase):
        self.__global_environment = global_environment

    def apply(self, instruction: instr.ActPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate(self.__global_environment))


class AssertValidateInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase):
        self.__global_environment = global_environment

    def apply(self, instruction: instr.AssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate(self.__global_environment))


class ActScriptGenerationExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase,
                 phase_environment: instr.PhaseEnvironmentForScriptGeneration):
        self.__global_environment = global_environment
        self.__phase_environment = phase_environment

    def apply(self, instruction: instr.ActPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.main(self.__global_environment,
                                                 self.__phase_environment))


class AssertInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase,
                 phase_environment: instr.PhaseEnvironmentForInternalCommands):
        self.__global_environment = global_environment
        self.__phase_environment = phase_environment

    def apply(self, instruction: instr.AssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_pass_or_fail_or_hard_error(
            instruction.main(self.__global_environment,
                                self.__phase_environment))


class CleanupPhaseInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase,
                 phase_environment: instr.PhaseEnvironmentForInternalCommands):
        self.__global_environment = global_environment
        self.__phase_environment = phase_environment

    def apply(self, instruction: instr.CleanupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.main(self.__global_environment,
                                self.__phase_environment))
