import pathlib
from typing import Sequence

from exactly_lib.execution import phase_step_simple as phase_step
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case.act_phase_handling import ActSourceAndExecutor, \
    ActSourceAndExecutorConstructor, ActPhaseOsProcessExecutor
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPreSdsStep, \
    InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.result import sh, svh
from exactly_lib.test_case.result.eh import ExitCodeOrHardError
from exactly_lib.util.std import StdFiles
from exactly_lib_test.execution.test_resources.execution_recording.recorder import ListRecorder
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_source_and_executor_constructors import \
    ActSourceAndExecutorConstructorForConstantExecutor


class ActSourceAndExecutorWrapperThatRecordsSteps(ActSourceAndExecutor):
    def __init__(self,
                 recorder: ListRecorder,
                 wrapped: ActSourceAndExecutor):
        self.__recorder = recorder
        self.__wrapped = wrapped

    def parse(self, environment: InstructionEnvironmentForPreSdsStep):
        self.__recorder.recording_of(phase_step.ACT__PARSE).record()
        self.__wrapped.parse(environment)

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
                script_output_dir_path: pathlib.Path) -> sh.SuccessOrHardError:
        self.__recorder.recording_of(phase_step.ACT__PREPARE).record()
        return self.__wrapped.prepare(environment, script_output_dir_path)

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                script_output_dir_path: pathlib.Path,
                std_files: StdFiles) -> ExitCodeOrHardError:
        self.__recorder.recording_of(phase_step.ACT__EXECUTE).record()
        return self.__wrapped.execute(environment, script_output_dir_path, std_files)


class ActSourceAndExecutorWrapperConstructorThatRecordsSteps(ActSourceAndExecutorConstructor):
    def __init__(self,
                 recorder: ListRecorder,
                 wrapped: ActSourceAndExecutorConstructor):
        self.__recorder = recorder
        self.__wrapped = wrapped

    def apply(self,
              os_process_executor: ActPhaseOsProcessExecutor,
              environment: InstructionEnvironmentForPreSdsStep,
              act_phase_instructions: Sequence[ActPhaseInstruction]) -> ActSourceAndExecutor:
        return ActSourceAndExecutorWrapperThatRecordsSteps(self.__recorder,
                                                           self.__wrapped.apply(os_process_executor,
                                                                                environment,
                                                                                act_phase_instructions))


def constructor_of_constant(recorder: ListRecorder,
                            wrapped: ActSourceAndExecutor) -> ActSourceAndExecutorConstructor:
    return ActSourceAndExecutorWrapperConstructorThatRecordsSteps(
        recorder,
        ActSourceAndExecutorConstructorForConstantExecutor(wrapped))
