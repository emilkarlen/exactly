from shellcheck_lib.execution.single_instruction_executor import ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections import common as instr
from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.sections.anonymous import AnonymousPhaseInstruction, \
    ConfigurationBuilder
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.before_assert import BeforeAssertPhaseInstruction
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder


def _from_success_or_validation_error_or_hard_error(res: svh.SuccessOrValidationErrorOrHardError) \
        -> PartialInstructionControlledFailureInfo:
    if res.is_success:
        return None
    elif res.is_validation_error:
        return PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.VALIDATION,
                                                       res.failure_message)
    else:
        return PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.HARD_ERROR,
                                                       res.failure_message)


def _from_success_or_hard_error(res: sh.SuccessOrHardError) -> PartialInstructionControlledFailureInfo:
    return None \
        if res.is_success \
        else PartialInstructionControlledFailureInfo(PartialControlledFailureEnum.HARD_ERROR,
                                                     res.failure_message)


def _from_pass_or_fail_or_hard_error(res: pfh.PassOrFailOrHardError) -> PartialInstructionControlledFailureInfo:
    if res.status is pfh.PassOrFailOrHardErrorEnum.PASS:
        return None
    else:
        return PartialInstructionControlledFailureInfo(PartialControlledFailureEnum(res.status.value),
                                                       res.failure_message)


class AnonymousInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 phase_environment: ConfigurationBuilder):
        self.__phase_environment = phase_environment
        self.__global_environment = ()

    def apply(self, instruction: AnonymousPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
                instruction.main(self.__global_environment, self.__phase_environment))


class SetupPreValidateInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPreEdsStep):
        self.__global_environment = global_environment

    def apply(self, instruction: SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
                instruction.validate_pre_eds(self.__global_environment))


class SetupPostValidateInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase):
        self.__global_environment = global_environment

    def apply(self, instruction: SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
                instruction.validate_post_eds(self.__global_environment))


class SetupMainInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 os_services: OsServices,
                 environment: instr.GlobalEnvironmentForPostEdsPhase,
                 setup_settings_builder: SetupSettingsBuilder):
        self.__os_services = os_services
        self.__environment = environment
        self.__setup_settings_builder = setup_settings_builder

    def apply(self, instruction: SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
                instruction.main(self.__os_services,
                                 self.__environment,
                                 self.__setup_settings_builder))


class ActValidateInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase):
        self.__global_environment = global_environment

    def apply(self, instruction: ActPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
                instruction.validate(self.__global_environment))


class BeforeAssertValidatePostSetupInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase):
        self.__global_environment = global_environment

    def apply(self, instruction: BeforeAssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
                instruction.validate_post_eds(self.__global_environment))


class AssertValidateInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase):
        self.__global_environment = global_environment

    def apply(self, instruction: AssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
                instruction.validate(self.__global_environment))


class ActMainInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPostEdsPhase,
                 phase_environment: PhaseEnvironmentForScriptGeneration):
        self.__global_environment = global_environment
        self.__phase_environment = phase_environment

    def apply(self, instruction: ActPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
                instruction.main(self.__global_environment,
                                 self.__phase_environment))


class AssertMainInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 environment: instr.GlobalEnvironmentForPostEdsPhase,
                 os_services: OsServices):
        self.__environment = environment
        self.__os_services = os_services

    def apply(self, instruction: AssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_pass_or_fail_or_hard_error(
                instruction.main(self.__environment, self.__os_services))


class ActPreValidateInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPreEdsStep):
        self.__global_environment = global_environment

    def apply(self, instruction: ActPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
                instruction.validate_pre_eds(self.__global_environment))


class BeforeAssertPreValidateInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPreEdsStep):
        self.__global_environment = global_environment

    def apply(self, instruction: BeforeAssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
                instruction.validate_pre_eds(self.__global_environment))


class BeforeAssertInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 environment: instr.GlobalEnvironmentForPostEdsPhase,
                 os_services: OsServices):
        self.__environment = environment
        self.__os_services = os_services

    def apply(self, instruction: BeforeAssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
                instruction.main(self.__os_services, self.__environment))


class AssertPreValidateInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPreEdsStep):
        self.__global_environment = global_environment

    def apply(self, instruction: AssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
                instruction.validate_pre_eds(self.__global_environment))


class CleanupPreValidateInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 global_environment: instr.GlobalEnvironmentForPreEdsStep):
        self.__global_environment = global_environment

    def apply(self, instruction: CleanupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
                instruction.validate_pre_eds(self.__global_environment))


class CleanupInstructionExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 environment: instr.GlobalEnvironmentForPostEdsPhase,
                 os_services: OsServices):
        self.__environment = environment
        self.__os_services = os_services

    def apply(self, instruction: CleanupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
                instruction.main(self.__environment, self.__os_services))
