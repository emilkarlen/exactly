from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.sections import common as instrs
from shellcheck_lib.test_case.sections.act.instruction import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.sections.anonymous import AnonymousPhaseInstruction, ExecutionMode, \
    ConfigurationBuilder
from shellcheck_lib.test_case.sections.assert_ import AssertPhaseInstruction
from shellcheck_lib.test_case.sections.cleanup import CleanupPhaseInstruction
from shellcheck_lib.test_case.sections.result import pfh
from shellcheck_lib.test_case.sections.result import sh
from shellcheck_lib.test_case.sections.result import svh
from shellcheck_lib.test_case.sections.setup import SetupPhaseInstruction, SetupSettingsBuilder


class ImplementationErrorTestException(Exception):
    pass


class AnonymousPhaseInstructionThatSetsExecutionMode(AnonymousPhaseInstruction):
    def __init__(self,
                 value_to_set: ExecutionMode):
        self.value_to_set = value_to_set

    def main(self, global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        configuration_builder.set_execution_mode(self.value_to_set)
        return sh.new_sh_success()


class AnonymousPhaseInstructionThatReturns(AnonymousPhaseInstruction):
    def __init__(self,
                 ret_val: sh.SuccessOrHardError):
        self.ret_val = ret_val

    def main(self, global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        return self.ret_val


class AnonymousPhaseInstructionWithImplementationError(AnonymousPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def main(self, global_environment,
             configuration_builder: ConfigurationBuilder) -> sh.SuccessOrHardError:
        raise self.__exception_to_raise


class SetupPhaseInstructionThatReturns(SetupPhaseInstruction):
    def __init__(self,
                 from_pre_validate: svh.SuccessOrValidationErrorOrHardError,
                 from_execute: sh.SuccessOrHardError,
                 from_post_validate: svh.SuccessOrValidationErrorOrHardError):
        self.__from_pre_validate = from_pre_validate
        self.__from_execute = from_execute
        self.__from_post_validate = from_post_validate

    def pre_validate(self,
                     global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.__from_pre_validate

    def main(self,
             os_services: OsServices,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return self.__from_execute

    def post_validate(self,
                      global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.__from_post_validate


class SetupPhaseInstructionWithImplementationErrorInPreValidate(SetupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def pre_validate(self,
                     global_environment: instrs.GlobalEnvironmentForPreEdsStep) \
            -> svh.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise

    def main(self,
             os_services: OsServices,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()


class SetupPhaseInstructionWithImplementationErrorInPostValidate(SetupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def main(self,
             os_services: OsServices,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        return sh.new_sh_success()

    def post_validate(self,
                      global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise


class SetupPhaseInstructionWithExceptionInExecute(SetupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def main(self,
             os_services: OsServices,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             settings_builder: SetupSettingsBuilder) -> sh.SuccessOrHardError:
        raise self.__exception_to_raise


class ActPhaseInstructionThatReturns(ActPhaseInstruction):
    def __init__(self,
                 from_validate: svh.SuccessOrValidationErrorOrHardError,
                 from_execute: sh.SuccessOrHardError):
        self.__for_validate = from_validate
        self.__for_execute = from_execute

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.__for_validate

    def main(
            self,
            global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        return self.__for_execute


class ActPhaseInstructionWithImplementationErrorInValidate(ActPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def validate(self,
                 global_environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise

    def main(
            self,
            global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        return sh.new_sh_success()


class ActPhaseInstructionWithImplementationErrorInExecute(ActPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def main(
            self,
            global_environment: instrs.GlobalEnvironmentForPostEdsPhase,
            phase_environment: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        raise self.__exception_to_raise


class AssertPhaseInstructionThatReturns(AssertPhaseInstruction):
    def __init__(self,
                 from_validate: svh.SuccessOrValidationErrorOrHardError,
                 from_execute: pfh.PassOrFailOrHardError):
        self.__for_validate = from_validate
        self.__for_execute = from_execute

    def validate(self,
                 environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return self.__for_validate

    def main(self,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return self.__for_execute


class AssertPhaseInstructionWithExceptionInValidate(AssertPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def validate(self,
                 environment: instrs.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        raise self.__exception_to_raise

    def main(self,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return sh.new_sh_success()


class AssertPhaseInstructionWithExceptionInExecute(AssertPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def main(self,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        raise self.__exception_to_raise


class CleanupPhaseInstructionThatReturns(CleanupPhaseInstruction):
    def __init__(self,
                 ret_val: sh.SuccessOrHardError):
        self.ret_val = ret_val

    def main(self,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        return self.ret_val


class CleanupPhaseInstructionWithImplementationError(CleanupPhaseInstruction):
    def __init__(self,
                 exception_to_raise: Exception):
        self.__exception_to_raise = exception_to_raise

    def main(self,
             environment: instrs.GlobalEnvironmentForPostEdsPhase,
             os_services: OsServices) -> sh.SuccessOrHardError:
        raise self.__exception_to_raise
