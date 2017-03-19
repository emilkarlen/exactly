from exactly_lib.execution.instruction_execution.single_instruction_executor import ControlledInstructionExecutor, \
    PartialInstructionControlledFailureInfo, PartialControlledFailureEnum
from exactly_lib.execution.instruction_execution.value_definition_validation import validate_symbol_usages
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases import common as instr
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.before_assert import BeforeAssertPhaseInstruction
from exactly_lib.test_case.phases.cleanup import CleanupPhaseInstruction, PreviousPhase
from exactly_lib.test_case.phases.configuration import ConfigurationPhaseInstruction, \
    ConfigurationBuilder
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case.phases.result import sh
from exactly_lib.test_case.phases.result import svh
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction, SetupSettingsBuilder
from exactly_lib.util.symbol_table import SymbolTable


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


class ConfigurationMainExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 phase_environment: ConfigurationBuilder):
        self.__phase_environment = phase_environment

    def apply(self, instruction: ConfigurationPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.main(self.__phase_environment))


class SetupSymbolValidatePreSdsExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environment: instr.InstructionEnvironmentForPreSdsStep):
        self.__instruction_environment = instruction_environment

    def apply(self, instruction: SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _validate_symbol_usages(instruction.value_usages(),
                                       self.__instruction_environment.value_definitions)


class SetupValidatePreSdsExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environment: instr.InstructionEnvironmentForPreSdsStep):
        self.__instruction_environment = instruction_environment

    def apply(self, instruction: SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_pre_sds(self.__instruction_environment))


class SetupValidatePostSetupExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environment: instr.InstructionEnvironmentForPostSdsStep):
        self.__instruction_environment = instruction_environment

    def apply(self, instruction: SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_post_setup(self.__instruction_environment))


class SetupMainExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 os_services: OsServices,
                 environment: instr.InstructionEnvironmentForPostSdsStep,
                 setup_settings_builder: SetupSettingsBuilder):
        self.__os_services = os_services
        self.__environment = environment
        self.__setup_settings_builder = setup_settings_builder

    def apply(self, instruction: SetupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.main(self.__environment,
                             self.__os_services,
                             self.__setup_settings_builder))


class BeforeAssertValidatePostSetupExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environment: instr.InstructionEnvironmentForPostSdsStep):
        self.__instruction_environment = instruction_environment

    def apply(self, instruction: BeforeAssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_post_setup(self.__instruction_environment))


class AssertValidatePostSetupExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environment: instr.InstructionEnvironmentForPostSdsStep):
        self.__instruction_environment = instruction_environment

    def apply(self, instruction: AssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_post_setup(self.__instruction_environment))


class AssertMainExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 environment: instr.InstructionEnvironmentForPostSdsStep,
                 os_services: OsServices):
        self.__environment = environment
        self.__os_services = os_services

    def apply(self, instruction: AssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_pass_or_fail_or_hard_error(
            instruction.main(self.__environment, self.__os_services))


class BeforeAssertValidatePreSdsExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environment: instr.InstructionEnvironmentForPreSdsStep):
        self.__instruction_environment = instruction_environment

    def apply(self, instruction: BeforeAssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_pre_sds(self.__instruction_environment))


class BeforeAssertMainExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 environment: instr.InstructionEnvironmentForPostSdsStep,
                 os_services: OsServices):
        self.__environment = environment
        self.__os_services = os_services

    def apply(self, instruction: BeforeAssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.main(self.__environment, self.__os_services))


class AssertValidatePreSdsExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environment: instr.InstructionEnvironmentForPreSdsStep):
        self.__instruction_environment = instruction_environment

    def apply(self, instruction: AssertPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_pre_sds(self.__instruction_environment))


class CleanupValidatePreSdsExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 instruction_environment: instr.InstructionEnvironmentForPreSdsStep):
        self.__instruction_environment = instruction_environment

    def apply(self, instruction: CleanupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_validation_error_or_hard_error(
            instruction.validate_pre_sds(self.__instruction_environment))


class CleanupMainExecutor(ControlledInstructionExecutor):
    def __init__(self,
                 environment: instr.InstructionEnvironmentForPostSdsStep,
                 previous_phase: PreviousPhase,
                 os_services: OsServices):
        self.__environment = environment
        self.__previous_phase = previous_phase
        self.__os_services = os_services

    def apply(self, instruction: CleanupPhaseInstruction) -> PartialInstructionControlledFailureInfo:
        return _from_success_or_hard_error(
            instruction.main(self.__environment,
                             self.__os_services,
                             self.__previous_phase))


def _validate_symbol_usages(value_usages: list,
                            value_definitions: SymbolTable) -> PartialInstructionControlledFailureInfo:
    for value_usage in value_usages:
        result = validate_symbol_usages(value_usage, value_definitions)
        if result is not None:
            return result
    return None
