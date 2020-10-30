from typing import Sequence

from exactly_lib.appl_env.os_services import OsServices
from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.test_case.actor import ActionToCheck
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import svh, sh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.util.file_utils.std import StdFiles
from exactly_lib_test.execution.test_resources.execution_recording.recorder import ListRecorder


class ActionToCheckWrapperThatRecordsSteps(ActionToCheck):
    def __init__(self,
                 recorder: ListRecorder,
                 wrapped: ActionToCheck):
        self.__recorder = recorder
        self.__wrapped = wrapped

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        self.__recorder.recording_of(phase_step.ACT__VALIDATE_SYMBOLS).record()
        return self.__wrapped.symbol_usages()

    def validate_pre_sds(self,
                         environment: InstructionEnvironmentForPreSdsStep
                         ) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__VALIDATE_PRE_SDS).record()
        return self.__wrapped.validate_pre_sds(environment)

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        self.__recorder.recording_of(phase_step.ACT__VALIDATE_POST_SETUP).record()
        return self.__wrapped.validate_post_setup(environment)

    def prepare(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                ) -> sh.SuccessOrHardError:
        self.__recorder.recording_of(phase_step.ACT__PREPARE).record()
        return self.__wrapped.prepare(environment, os_services)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                std_files: StdFiles,
                ) -> ExitCodeOrHardError:
        self.__recorder.recording_of(phase_step.ACT__EXECUTE).record()
        return self.__wrapped.execute(environment, os_services, std_files)
