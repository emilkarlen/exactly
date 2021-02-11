from typing import Optional, Iterator

from exactly_lib.execution.impl.single_instruction_executor import ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import instruction_environment as instr_env
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, \
    ConfigurationBuilder
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.instruction_settings import InstructionSettings
from exactly_lib.test_case.phases.setup.instruction import SetupPhaseInstruction
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.test_case.result import pfh, sh, svh

InstructionEnvPostSdsGetter = Iterator[InstructionEnvironmentForPostSdsStep]


def _from_success_or_validation_error_or_hard_error(res: svh.SuccessOrValidationErrorOrHardError,
                                                    ) -> Optional[PartialInstructionControlledFailureInfo]:
    if res.is_success:
        return None
    elif res.is_validation_error:
        return PartialInstructionControlledFailureInfo(
            PartialControlledFailureEnum.VALIDATION_ERROR,
            res.failure_message)
    else:
        return PartialInstructionControlledFailureInfo(
            PartialControlledFailureEnum.HARD_ERROR,
            res.failure_message)


def _from_success_or_hard_error(res: sh.SuccessOrHardError) -> PartialInstructionControlledFailureInfo:
    return (
        None
        if res.is_success
        else PartialInstructionControlledFailureInfo(
            PartialControlledFailureEnum.HARD_ERROR,
            res.failure_message)
    )


def _from_pass_or_fail_or_hard_error(res: pfh.PassOrFailOrHardError
                                     ) -> Optional[PartialInstructionControlledFailureInfo]:
    if res.status is pfh.PassOrFailOrHardErrorEnum.PASS:
        return None
    else:
        return PartialInstructionControlledFailureInfo(
            PartialControlledFailureEnum(res.status.value),
            res.failure_message)


class ConfigurationMainExecutor(ControlledInstructionExecutor):
    def __init__(self, phase_environment: ConfigurationBuilder):
        self._phase_environment = phase_environment

    def apply(self, instruction: ConfigurationPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.main(self._phase_environment)
        )


class SetupValidatePreSdsExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environment: instr_env.InstructionEnvironmentForPreSdsStep):
        self._instruction_environment = instruction_environment

    def apply(self, instruction: SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_pre_sds(self._instruction_environment))


class SetupValidatePostSetupExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environments: InstructionEnvPostSdsGetter):
        self._instruction_environments = instruction_environments

    def apply(self, instruction: SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_post_setup(next(self._instruction_environments)))


class SetupMainExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_settings: InstructionSettings,
                 os_services: OsServices,
                 instruction_environments: InstructionEnvPostSdsGetter,
                 settings_builder: SetupSettingsBuilder):
        self._instruction_settings = instruction_settings
        self._os_services = os_services
        self._instruction_environments = instruction_environments
        self._settings_builder = settings_builder

    def apply(self, instruction: SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.main(next(self._instruction_environments),
                             self._instruction_settings,
                             self._os_services,
                             self._settings_builder))


class BeforeAssertValidatePostSetupExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environments: InstructionEnvPostSdsGetter):
        self._instruction_environments = instruction_environments

    def apply(self, instruction: BeforeAssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_post_setup(next(self._instruction_environments)))


class AssertValidatePostSetupExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environments: InstructionEnvPostSdsGetter):
        self._instruction_environments = instruction_environments

    def apply(self, instruction: AssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_post_setup(next(self._instruction_environments)))


class AssertMainExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environments: InstructionEnvPostSdsGetter,
                 instruction_settings: InstructionSettings,
                 os_services: OsServices):
        self._instruction_environments = instruction_environments
        self._instruction_settings = instruction_settings
        self._os_services = os_services

    def apply(self, instruction: AssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_pass_or_fail_or_hard_error(
            instruction.main(next(self._instruction_environments), self._instruction_settings, self._os_services))


class BeforeAssertValidatePreSdsExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environment: instr_env.InstructionEnvironmentForPreSdsStep):
        self._instruction_environment = instruction_environment

    def apply(self, instruction: BeforeAssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_pre_sds(self._instruction_environment))


class BeforeAssertMainExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environments: InstructionEnvPostSdsGetter,
                 instruction_settings: InstructionSettings,
                 os_services: OsServices):
        self._instruction_environments = instruction_environments
        self._instruction_settings = instruction_settings
        self._os_services = os_services

    def apply(self, instruction: BeforeAssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.main(next(self._instruction_environments),
                             self._instruction_settings,
                             self._os_services))


class AssertValidatePreSdsExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environment: instr_env.InstructionEnvironmentForPreSdsStep):
        self._instruction_environment = instruction_environment

    def apply(self, instruction: AssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_pre_sds(self._instruction_environment))


class CleanupValidatePreSdsExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environment: instr_env.InstructionEnvironmentForPreSdsStep):
        self._instruction_environment = instruction_environment

    def apply(self, instruction: CleanupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_pre_sds(self._instruction_environment))


class CleanupMainExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environments: InstructionEnvPostSdsGetter,
                 instruction_settings: InstructionSettings,
                 previous_phase: PreviousPhase,
                 os_services: OsServices):
        self._instruction_environments = instruction_environments
        self._instruction_settings = instruction_settings
        self._previous_phase = previous_phase
        self._os_services = os_services

    def apply(self, instruction: CleanupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.main(next(self._instruction_environments),
                             self._instruction_settings,
                             self._os_services,
                             self._previous_phase))
